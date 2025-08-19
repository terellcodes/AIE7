import shutil
import os
from dotenv import load_dotenv
from langgraph_agent_lib.agents import create_helpful_langgraph_agent, create_langgraph_agent
from langgraph_agent_lib.rag import ProductionRAGChain
from langchain_core.messages import HumanMessage

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
# os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
# os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Quick cache clear (use with caution!)
def quick_clear():
    if os.path.exists("cache/embeddings"):
        shutil.rmtree("cache/embeddings")
        os.makedirs("cache/embeddings")
        print("Cache cleared!")

def setup_agents():
    print("Setting up RAG chain...")
    rag_chain = ProductionRAGChain(
        file_path="./data/The_Direct_Loan_Program.pdf" ,
        chunk_size=1000,
        chunk_overlap=100,
        embedding_model="text-embedding-3-small",
        llm_model="gpt-4.1-mini",
        cache_dir="./cache",
        collection_name="student_loans_test"
    )
    print("✓ RAG chain created successfully")

    print("\nCreating simple LangGraph agent...")
    simple_agent = create_langgraph_agent(
        model_name="gpt-4.1-mini",
        temperature=0.1,
        rag_chain=rag_chain
    )
    print("✓ Simple agent created successfully")
    print("  - Model: gpt-4.1-mini")
    print("  - Tools: RAG System")

    print("\nCreating helpful LangGraph agent...")
    helpful_agent = create_helpful_langgraph_agent(
        model_name="gpt-4.1-mini",
        temperature=0.1,
        rag_chain=rag_chain
    )
    print("✓ Helpful agent created successfully")
    print("  - Model: gpt-4.1-mini") 
    print("  - Tools: Tavily Search, Arxiv, RAG System")
    print("  - Features: Tool calling, parallel execution")

    return simple_agent, helpful_agent

def prepare_agent_input(query):
    return {"messages": [HumanMessage(content=query)]}

def run_agent(agent, query):
    response = agent.invoke(prepare_agent_input(query))
    final_message = response['messages'][-1].content
    if "HELPFULNESS" in final_message:
        return response['messages'][-2].content
    else:
        return final_message

if __name__ == "__main__":
    quick_clear()
    simple_agent, helpful_agent = setup_agents()
    queries_to_test = [
        "What is the main purpose of the Direct Loan Program?",  # RAG-focused
        # "What are the latest developments in AI safety?",  # Web search
        # "Find recent papers about transformer architectures",  # Academic search
        # "How do the concepts in this document relate to current AI research trends?"  # Multi-tool
    ]
    for query in queries_to_test:
        simple_agent_response = run_agent(simple_agent, query)
        print(f"Simple Agent Response: {simple_agent_response}")
        helpful_agent_response = run_agent(helpful_agent, query)
        print(f"Helpful Agent Response: {helpful_agent_response}")