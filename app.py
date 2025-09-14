%%writefile app.py
# --- Importações Essenciais ---
import streamlit as st
import os
import time
import asyncio # <-- ADICIONADO PARA A CORREÇÃO
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

# --- Carregando a Chave de API (do ambiente de execução) ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- Função para Criar o Banco de Dados Vetorial (com cache e correção) ---
@st.cache_resource
def criar_banco_de_dados():
    """Função para criar e carregar o banco de dados vetorial."""
    try:
        # ===== CORREÇÃO PARA O ERRO 'EVENT LOOP' =====
        # Garante que um "gerente de tarefas" (event loop) esteja ativo
        # para as bibliotecas assíncronas do Google.
        asyncio.set_event_loop(asyncio.new_event_loop())
        # ===============================================

        path = "base_conhecimento"
        loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        db = FAISS.from_documents(split_docs, embeddings_model)
        return db
    except Exception as e:
        st.error(f"Erro ao criar o banco de dados: {e}")
        return None

# --- O restante do código permanece o mesmo ---
db = criar_banco_de_dados()
if db:
    llm_geracao = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
    prompt_rag = ChatPromptTemplate.from_messages([
        ("system",
         "Você é o ClimaBot, um assistente virtual especialista em mudanças climáticas da ONG \"Clima Ação\". "
         "Sua personalidade é didática, confiável e inspiradora, como um educador apaixonado pelo planeta.\n"
         "Sua missão principal é educar os usuários sobre as causas, consequências e fatos científicos do aquecimento global, de forma clara e acessível.\n"
         "Sua missão secundária é informar sobre os projetos e as formas de ajudar a ONG \"Clima Ação\" e, quando apropriado, desmentir mitos comuns sobre o clima.\n\n"
         "REGRAS FUNDAMENTAIS:\n"
         "1. CONHECIMENTO LIMITADO: Sua única fonte de verdade são os documentos de contexto fornecidos a cada pergunta. Responda estritamente com base neles.\n"
         "2. SEJA HONESTO: Se a resposta para uma pergunta não estiver nos documentos, responda de forma acolhedora, como: \"Não encontrei informações sobre isso na minha base de dados. Você gostaria de saber sobre outro tópico relacionado ao nosso trabalho ou às mudanças climáticas?\"\n"
         "3. TRANSPARÊNCIA GERA CONFIANÇA: Ao fornecer dados ou informações de artigos externos, termine sua resposta de forma natural, mencionando a fonte para que o usuário saiba mais. Por exemplo: \"Você pode ler mais sobre isso em [nome da fonte ou link]\"."
        ),
        ("human", "Pergunta: {input}\n\nContexto:\n{context}")
    ])
    document_chain = create_stuff_documents_chain(llm_geracao, prompt_rag)
    class AgentState(TypedDict, total=False):
        pergunta: str
        resposta: str
        documentos: List[str]
    def node_rag(state: AgentState) -> AgentState:
        documentos_relevantes = db.similarity_search(state["pergunta"])
        resposta_gerada = document_chain.invoke({
            "input": state["pergunta"],
            "context": documentos_relevantes
        })
        return {"documentos": documentos_relevantes, "resposta": resposta_gerada}
    workflow = StateGraph(AgentState)
    workflow.add_node("rag", node_rag)
    workflow.add_edge(START, "rag")
    workflow.add_edge("rag", END)
    chatbot_final = workflow.compile()
st.title("🌍 ClimaBot - Seu Assistente da Clima Ação")
st.caption("Faça uma pergunta sobre mudanças climáticas ou sobre o nosso trabalho!")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("Qual a sua dúvida?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            if db:
                response = chatbot_final.invoke({"pergunta": prompt})
                st.markdown(response['resposta'])
            else:
                st.error("O banco de dados de conhecimento não pôde ser carregado. A aplicação não pode funcionar.")
    st.session_state.messages.append({"role": "assistant", "content": response['resposta']})
