import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Importações para carregar e processar documentos
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Importação da biblioteca oficial do Google
import google.generativeai as genai

# Configuração básica do logging
logging.basicConfig(level=logging.INFO)

# --- FUNÇÃO PARA CONSTRUIR O BANCO DE DADOS VETORIAL ---
def criar_banco_de_dados():
    print("Iniciando a criação do banco de dados vetorial...")
    path = "base_conhecimento"
    
    loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    docs = loader.load()
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

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega a chave de API e configura o cliente do Google
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Constrói o banco de dados vetorial quando a aplicação arranca
db = criar_banco_de_dados()

# --- ALTERAÇÃO PRINCIPAL AQUI ---
# Configura o modelo de linguagem com o nome correto
llm_geracao = genai.GenerativeModel('gemini-1.0-pro')

# Cria o template do prompt
prompt_template = """Você é o ClimaBot, um assistente virtual especialista em mudanças climáticas da ONG "Clima Ação". Sua personalidade é didática, confiável e inspiradora, como um educador apaixonado pelo planeta.

Sua missão principal é educar os usuários sobre as causas, consequências e fatos científicos do aquecimento global, de forma clara e acessível.
Sua missão secundária é informar sobre os projetos e as formas de ajudar a ONG "Clima Ação" e, quando apropriado, desmentir mitos comuns sobre o clima.

REGRAS FUNDAMENTAIS:
1. CONHECIMENTO LIMITADO: Sua única fonte de verdade são os documentos de contexto fornecidos a cada pergunta. Responda estritamente com base neles.
2. SEJA HONESTO: Se a resposta para uma pergunta não estiver nos documentos, responda de forma acolhedora, como: "Não encontrei informações sobre isso na minha base de dados. Você gostaria de saber sobre outro tópico relacionado ao nosso trabalho ou às mudanças climáticas?"
3. TRANSPARÊNCIA GERA CONFIANÇA: Ao fornecer dados ou informações de artigos externos, termine sua resposta de forma natural, mencionando a fonte para que o usuário saiba mais. Por exemplo: "Você pode ler mais sobre isso em [nome da fonte ou link]".

---
Pergunta do usuário: {pergunta}

Contexto relevante:
{contexto}
---

Resposta:
"""

class Pergunta(BaseModel):
    pergunta: str

@app.post("/api")
def responder(item: Pergunta):
    try:
        pergunta = item.pergunta
        if not pergunta:
            return {'error': 'Pergunta não fornecida'}

        # Faz a busca por similaridade
        documentos_relevantes = db.similarity_search(pergunta)
        
        # Junta o conteúdo dos documentos relevantes
        contexto = "\n\n".join([doc.page_content for doc in documentos_relevantes])
        
        # Formata o prompt final
        prompt_final = prompt_template.format(pergunta=pergunta, contexto=contexto)
        
        # Gera a resposta usando a biblioteca direta do Google
        resposta = llm_geracao.generate_content(prompt_final)

        # Verifica se a resposta tem texto antes de retornar
        if resposta and hasattr(resposta, 'text'):
            return {'resposta': resposta.text}
        else:
            # Se não houver texto, retorna uma resposta padrão
            logging.warning("A resposta do modelo de IA estava vazia ou bloqueada.")
            return {'resposta': 'Desculpe, não consegui gerar uma resposta para isso. Tente perguntar de outra forma.'}
        
    except Exception as e:
        # Adiciona um log para que o erro apareça nos logs do Render
        logging.error(f"Erro ao processar a pergunta: {e}")
        return {'error': f"Erro interno no servidor: {str(e)}"}
