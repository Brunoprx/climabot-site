import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Importações para carregar e processar documentos
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Configuração básica do logging
logging.basicConfig(level=logging.INFO)

# --- FUNÇÃO PARA CONSTRUIR O BANCO DE DADOS VETORIAL ---
def criar_banco_de_dados():
    print("Iniciando a criação do banco de dados vetorial...")
    path = "base_conhecimento"
    
    try:
        loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
        docs = loader.load()
        if not docs:
            logging.error("Nenhum documento encontrado na pasta 'base_conhecimento'.")
            return None
        print(f"Carregados {len(docs)} documentos.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)
        print(f"Documentos divididos em {len(split_docs)} chunks.")

        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ.get("GOOGLE_API_KEY")
        )

        db = FAISS.from_documents(split_docs, embeddings_model)
        print("Banco de dados vetorial criado com sucesso.")
        return db
    except Exception as e:
        logging.error(f"Falha ao criar o banco de dados vetorial: {e}")
        return None

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---

app = FastAPI()

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

# --- ALTERAÇÃO PRINCIPAL AQUI: USANDO LANGCHAIN PARA TUDO ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)

prompt_template_str = """Você é o ClimaBot, um assistente virtual especialista em mudanças climáticas da ONG "Clima Ação". Sua personalidade é didática, confiável e inspiradora.

Sua missão é educar os usuários sobre o aquecimento global e informar sobre os projetos da ONG "Clima Ação", usando apenas o CONTEXTO abaixo.

REGRAS:
1.  Responda estritamente com base no CONTEXTO fornecido.
2.  Se a resposta não estiver no CONTEXTO, diga: "Não encontrei informações sobre isso na minha base de dados. Você poderia perguntar sobre o nosso trabalho ou sobre as mudanças climáticas?"
3.  Se usar dados de uma fonte externa do contexto, cite-a no final. Ex: "Você pode ler mais sobre isso na [nome da fonte]".

CONTEXTO:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:
"""

prompt = PromptTemplate.from_template(prompt_template_str)

class Pergunta(BaseModel):
    pergunta: str

@app.post("/api")
def responder(item: Pergunta):
    if db is None:
        return {'error': "O banco de dados de conhecimento não está disponível."}
        
    try:
        pergunta = item.pergunta
        if not pergunta:
            return {'error': 'Pergunta não fornecida'}

        # O retriever busca os documentos relevantes no banco de dados vetorial
        retriever = db.as_retriever(search_kwargs={"k": 5})

        # Cria a "chain" (cadeia) de processamento do LangChain
        rag_chain = (
            {"contexto": retriever, "pergunta": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Invoca a chain para obter a resposta
        resposta = rag_chain.invoke(pergunta)
        
        return {'resposta': resposta}
        
    except Exception as e:
        logging.error(f"Erro ao processar a pergunta: {e}")
        return {'error': f"Erro interno no servidor: {str(e)}"}
