# Imports
import os
import getpass
import nest_asyncio
import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from uuid import uuid4

# Environment Variables
os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API Key:")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com/"
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com/"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass('Enter your LangSmith API key: ')
unique_id = uuid4().hex[0:8]
os.environ["LANGSMITH_PROJECT"] = f"LangSmith - {unique_id}"
# os.environ["LANGSMITH_PROJECT"] = "pr-puzzled-backpack-3"

# Asyncio Patch
nest_asyncio.apply()

# --- Data Loading ---
directory_loader = DirectoryLoader("data", glob="**/*.pdf", loader_cls=PyMuPDFLoader)
loan_knowledge_resources = directory_loader.load()

# --- Chunking ---
def tiktoken_len(text):
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(text)
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=750,
    chunk_overlap=0,
    length_function=tiktoken_len,
)
loan_knowledge_chunks = text_splitter.split_documents(loan_knowledge_resources)

# --- Vector Store Setup ---
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
qdrant_vectorstore = Qdrant.from_documents(
    documents=loan_knowledge_chunks,
    embedding=embedding_model,
    location=":memory:"
)
qdrant_retriever = qdrant_vectorstore.as_retriever()

# --- Prompt and Model Setup ---
HUMAN_TEMPLATE = """
#CONTEXT:
{context}

QUERY:
{query}

Use the provide context to answer the provided user query. Only use the provided context to answer the query. If you do not know the answer, or it's not contained in the provided context respond with \"I don't know\"
"""
chat_prompt = ChatPromptTemplate.from_messages([
    ("human", HUMAN_TEMPLATE)
])
openai_chat_model = ChatOpenAI(model="gpt-4.1-nano")

# --- RAG Pipeline Setup ---
class State(TypedDict):
    question: str
    context: list[Document]
    response: str

def retrieve(state: State) -> State:
    retrieved_docs = qdrant_retriever.invoke(state["question"])
    return {"context": retrieved_docs}

def generate(state: State) -> State:
    generator_chain = chat_prompt | openai_chat_model | StrOutputParser()
    response = generator_chain.invoke({"query": state["question"], "context": state["context"]})
    return {"response": response}

graph_builder = StateGraph(State)
graph_builder = graph_builder.add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
rag_graph = graph_builder.compile()

# --- Example Queries ---
response = rag_graph.invoke({"question": "Is applying for and securing a student loan in 2025 a terrible idea?"})
print(response["response"])
for context in response["context"]:
    print("Context:")
    print(context.page_content[:100])
    print("----")

response = rag_graph.invoke({"question": "What is the airspeed velocity of an unladen swallow?"})
print(response["response"])

# --- LangSmith Demo Run ---
rag_graph.invoke({"question": "What is the maximum loan amount I can get from the government to go to school these days?"}, {"tags": ["Demo Run"]})['response']
