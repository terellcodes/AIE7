import uuid
import os

from langgraph_agent_lib.agents import create_helpful_langgraph_agent
from langgraph_agent_lib.rag import ProductionRAGChain

# os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # Set this in your environment
os.environ["TAVILY_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = f"AIM Session 16 LangGraph Integration - {uuid.uuid4().hex[0:8]}"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"

rag_chain = ProductionRAGChain(
    file_path="./data/The_Direct_Loan_Program.pdf" ,
    chunk_size=1000,
    chunk_overlap=100,
    embedding_model="text-embedding-3-small",
    llm_model="gpt-4.1-mini",
    cache_dir="./cache",
    collection_name="student_loans_test"
)

# Create a Simple LangGraph Agent with RAG capabilities
print("Creating Helpful LangGraph Agent...")

try:
    helpful_agent = create_helpful_langgraph_agent(
        model_name="gpt-4.1-mini",
        temperature=0.1,
        rag_chain=rag_chain  # Pass our cached RAG chain as a tool
    )
    print("✓ Helpful Agent created successfully!")
    print("  - Model: gpt-4.1-mini")
    print("  - Tools: Tavily Search, Arxiv, RAG System")
    print("  - Features: Tool calling, parallel execution")
    import time
    time.sleep(10)
    from langchain_core.messages import HumanMessage
    response = helpful_agent.invoke({"messages": [HumanMessage(content="What is the maximum amount of student loan debt a person can have?")]})
    print(response["messages"][-2].content)
    import time

except Exception as e:
    print(f"❌ Error creating simple agent: {e}")
    simple_agent = None