from fastapi import HTTPException, status
from app.core.config import settings
from app.models.requests import ResearchRequest
import os

def validate_api_keys(request: ResearchRequest) -> dict:
    """Validate and prepare API keys for the research request."""
    api_keys = {}
    
    # Tavily API Key
    tavily_key = request.tavily_api_key or settings.default_tavily_api_key or os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tavily API key is required"
        )
    api_keys["TAVILY_API_KEY"] = tavily_key
    
    # Anthropic API Key
    anthropic_key = request.anthropic_api_key or settings.default_anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anthropic API key is required"
        )
    api_keys["ANTHROPIC_API_KEY"] = anthropic_key
    
    # OpenAI API Key (optional)
    openai_key = request.openai_api_key or settings.default_openai_api_key or os.getenv("OPENAI_API_KEY")
    if openai_key:
        api_keys["OPENAI_API_KEY"] = openai_key
    
    return api_keys

def get_graph_config(request: ResearchRequest) -> dict:
    """Create graph configuration from request."""
    return {
        "report_structure": settings.default_report_structure,
        "number_of_queries": request.number_of_queries,
        "max_search_depth": request.max_search_depth,
        "planner_provider": request.planner_provider.value,
        "planner_model": request.planner_model,
        "writer_provider": request.writer_provider.value,
        "writer_model": request.writer_model,
        "search_api": request.search_api.value,
        "search_api_config": None
    } 