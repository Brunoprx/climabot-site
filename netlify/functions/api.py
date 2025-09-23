import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI

# Carrega a chave de API do ambiente da Netlify
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- CARREGAMENTO RÁPIDO DO "CÉREBRO" ---
# Caminho para os ficheiros de memória pré-calculados que estão no repositório
faiss_index_path = os.path.join(os.path.dirname(__file__), '..', '..', 'faiss_index')

# Carrega o banco de dados vetorial a partir dos ficheiros (é quase instantâneo)
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
db = FAISS.load_local(faiss_index_path, embeddings_model, allow_dangerous_deserialization=True)

# Configura o modelo de linguagem e o prompt (sem alterações)
llm_geracao = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
prompt_rag = ChatPromptTemplate.from_messages([
    ("system", "Você é o ClimaBot, um assistente virtual especialista em mudanças climáticas da ONG \"Clima Ação\". Sua personalidade é didática, confiável e inspiradora, como um educador apaixonado pelo planeta.\n\nSua missão principal é educar os usuários sobre as causas, consequências e fatos científicos do aquecimento global, de forma clara e acessível.\nSua missão secundária é informar sobre os projetos e as formas de ajudar a ONG \"Clima Ação\" e, quando apropriado, desmentir mitos comuns sobre o clima.\n\nREGRAS FUNDAMENTAIS:\n1. CONHECIMENTO LIMITADO: Sua única fonte de verdade são os documentos de contexto fornecidos a cada pergunta. Responda estritamente com base neles.\n2. SEJA HONESTO: Se a resposta para uma pergunta não estiver nos documentos, responda de forma acolhedora, como: \"Não encontrei informações sobre isso na minha base de dados. Você gostaria de saber sobre outro tópico relacionado ao nosso trabalho ou às mudanças climáticas?\"\n3. TRANSPARÊNCIA GERA CONFIANÇA: Ao fornecer dados ou informações de artigos externos, termine sua resposta de forma natural, mencionando a fonte para que o usuário saiba mais. Por exemplo: \"Você pode ler mais sobre isso em [nome da fonte ou link]\"."),
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])
document_chain = create_stuff_documents_chain(llm_geracao, prompt_rag)

# --- A FUNÇÃO DA API (sem alterações na lógica principal) ---
def handler(event, context):
    try:
        body = json.loads(event['body'])
        pergunta = body.get('pergunta', '')

        if not pergunta:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Pergunta não fornecida'})}

        documentos_relevantes = db.similarity_search(pergunta)
        resposta_gerada = document_chain.invoke({
            "input": pergunta,
            "context": documentos_relevantes
        })

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'resposta': resposta_gerada})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
