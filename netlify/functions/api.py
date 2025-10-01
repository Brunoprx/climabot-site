import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware

# Cria a aplicação FastAPI
app = FastAPI()

# --- Configuração de CORS ---
# Permite que o seu site na Netlify aceda a esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],
)

# Carrega a chave de API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- CARREGAMENTO DO "CÉREBRO" (sem alterações) ---
faiss_index_path = os.path.join(os.path.dirname(__file__), '..', '..', 'faiss_index')
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
db = FAISS.load_local(faiss_index_path, embeddings_model, allow_dangerous_deserialization=True)

# --- CONFIGURAÇÃO DO LANGCHAIN (sem alterações) ---
llm_geracao = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
prompt_rag = ChatPromptTemplate.from_messages([
    ("system", "Você é o ClimaBot... (coloque o seu prompt de sistema completo aqui)"),
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])
document_chain = create_stuff_documents_chain(llm_geracao, prompt_rag)

# Define o formato esperado para a pergunta
class Pergunta(BaseModel):
    pergunta: str

# --- PONTO DE ENTRADA DA API ---
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
        return {'error': str(e)}
