import os
import json
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI

# Carrega a chave de API do ambiente
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- O "CÉREBRO" DO CHATBOT ---
# Caminho para a base de conhecimento
knowledge_base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'base_conhecimento')

# Carrega e processa os documentos
loader = DirectoryLoader(knowledge_base_path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(docs)

# Cria o banco de dados vetorial
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
db = FAISS.from_documents(split_docs, embeddings_model)

# Configura o modelo de linguagem e o prompt
llm_geracao = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
prompt_rag = ChatPromptTemplate.from_messages([
    ("system", "Você é o ClimaBot, um assistente virtual especialista em mudanças climáticas da ONG \"Clima Ação\". Sua personalidade é didática, confiável e inspiradora, como um educador apaixonado pelo planeta.\n\nSua missão principal é educar os usuários sobre as causas, consequências e fatos científicos do aquecimento global, de forma clara e acessível.\nSua missão secundária é informar sobre os projetos e as formas de ajudar a ONG \"Clima Ação\" e, quando apropriado, desmentir mitos comuns sobre o clima.\n\nREGRAS FUNDAMENTAIS:\n1. CONHECIMENTO LIMITADO: Sua única fonte de verdade são os documentos de contexto fornecidos a cada pergunta. Responda estritamente com base neles.\n2. SEJA HONESTO: Se a resposta para uma pergunta não estiver nos documentos, responda de forma acolhedora, como: \"Não encontrei informações sobre isso na minha base de dados. Você gostaria de saber sobre outro tópico relacionado ao nosso trabalho ou às mudanças climáticas?\"\n3. TRANSPARÊNCIA GERA CONFIANÇA: Ao fornecer dados ou informações de artigos externos, termine sua resposta de forma natural, mencionando a fonte para que o usuário saiba mais. Por exemplo: \"Você pode ler mais sobre isso em [nome da fonte ou link]\"."), # << Adapte o seu prompt
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])
document_chain = create_stuff_documents_chain(llm_geracao, prompt_rag)

# --- A FUNÇÃO DA API ---
def handler(event, context):
    try:
        # Pega a pergunta do utilizador enviada pelo site
        body = json.loads(event['body'])
        pergunta = body.get('pergunta', '')

        if not pergunta:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Pergunta não fornecida'})}

        # Executa a lógica RAG
        documentos_relevantes = db.similarity_search(pergunta)
        resposta_gerada = document_chain.invoke({
            "input": pergunta,
            "context": documentos_relevantes
        })

        # Retorna a resposta para o site
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Permite que o seu site aceda à API
            },
            'body': json.dumps({'resposta': resposta_gerada})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
