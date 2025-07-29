from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class SearchAPI(str, Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    EXA = "exa"
    ARXIV = "arxiv"
    PUBMED = "pubmed"

class PlannerProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"

class WriterProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"

class ResearchRequest(BaseModel):
    topic: str = Field(..., description="The research topic")
    tavily_api_key: Optional[str] = Field(None, description="Tavily API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    
    # Optional configuration
    search_api: SearchAPI = Field(SearchAPI.TAVILY, description="Search API to use")
    planner_provider: PlannerProvider = Field(PlannerProvider.ANTHROPIC, description="Planner provider")
    planner_model: str = Field("claude-sonnet-4-20250514", description="Planner model")
    writer_provider: WriterProvider = Field(WriterProvider.ANTHROPIC, description="Writer provider")
    writer_model: str = Field("claude-sonnet-4-20250514", description="Writer model")
    number_of_queries: int = Field(1, description="Number of search queries per iteration")
    max_search_depth: int = Field(1, description="Maximum search iterations")

class FeedbackRequest(BaseModel):
    thread_id: str = Field(..., description="Thread ID for the research session")
    feedback: str = Field("", description="Feedback on the report plan")
    approve: bool = Field(False, description="Whether to approve the plan") 