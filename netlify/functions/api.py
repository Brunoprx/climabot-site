import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Importações para carregar e processar documentos
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Importações para a cadeia de resposta
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI

# --- FUNÇÃO PARA CONSTRUIR O BANCO DE DADOS VETORIAL ---
def criar_banco_de_dados():
    print("Iniciando a criação do banco de dados vetorial...")
    path = "base_conhecimento"
    
    # Carrega os documentos de texto
    loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    docs = loader.load()
    print(f"Carregados {len(docs)} documentos.")

    # Divide os documentos em pedaços (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)
    print(f"Documentos divididos em {len(split_docs)} chunks.")

    # Cria os embeddings
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )

    # Cria o banco de dados FAISS a partir dos documentos e embeddings
    db = FAISS.from_documents(split_docs, embeddings_model)
    print("Banco de dados vetorial criado com sucesso.")
    return db

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---

app = FastAPI()

# Configuração de CORS para permitir acesso do seu site Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega a chave de API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Constrói o banco de dados vetorial quando a aplicação arranca
db = criar_banco_de_dados()

# Configura o LLM e a cadeia de resposta
llm_geracao = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.7)
prompt_rag = ChatPromptTemplate.from_messages([
    ("system", "Você é o ClimaBot, um assistente virtual especialista em mudanças climáticas da ONG \"Clima Ação\". Sua personalidade é didática, confiável e inspiradora, como um educador apaixonado pelo planeta.\n\nSua missão principal é educar os usuários sobre as causas, consequências e fatos científicos do aquecimento global, de forma clara e acessível.\nSua missão secundária é informar sobre os projetos e as formas de ajudar a ONG \"Clima Ação\" e, quando apropriado, desmentir mitos comuns sobre o clima.\n\nREGRAS FUNDAMENTAIS:\n1. CONHECIMENTO LIMITADO: Sua única fonte de verdade são os documentos de contexto fornecidos a cada pergunta. Responda estritamente com base neles.\n2. SEJA HONESTO: Se a resposta para uma pergunta não estiver nos documentos, responda de forma acolhedora, como: \"Não encontrei informações sobre isso na minha base de dados. Você gostaria de saber sobre outro tópico relacionado ao nosso trabalho ou às mudanças climáticas?\"\n3. TRANSPARÊNCIA GERA CONFIANÇA: Ao fornecer dados ou informações de artigos externos, termine sua resposta de forma natural, mencionando a fonte para que o usuário saiba mais. Por exemplo: \"Você pode ler mais sobre isso em [nome da fonte ou link]\"."),
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])
document_chain = create_stuff_documents_chain(llm_geracao, prompt_rag)

class Pergunta(BaseModel):
    pergunta: str

@app.post("/api")
def responder(item: Pergunta):
    try:
        pergunta = item.pergunta
        if not pergunta:
            return {'error': 'Pergunta não fornecida'}

        documentos_relevantes = db.similarity_search(pergunta)
        resposta_gerada = document_chain.invoke({
            "input": pergunta,
            "context": documentos_relevantes
        })

        return {'resposta': resposta_gerada}
    except Exception as e:
        # Retorna o erro detalhado para depuração
        return {'error': f"Erro interno no servidor: {str(e)}"}
