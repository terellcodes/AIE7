from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Deep Research API"
    api_version: str = "1.0.0"
    api_description: str = "API for generating research reports using LangGraph"
    
    # Default API Keys (can be overridden by request)
    default_tavily_api_key: Optional[str] = None
    default_anthropic_api_key: Optional[str] = None
    default_openai_api_key: Optional[str] = None
    
    # Graph Configuration
    default_report_structure: str = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list or table) that distills the main body sections 
   - Provide a concise summary of the report
   
Provide a paragraph with no more than 500 words to describe the key take aways on the topic"""

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings() 