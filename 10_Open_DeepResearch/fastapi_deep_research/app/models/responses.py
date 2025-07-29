from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from enum import Enum

class ResearchStatus(str, Enum):
    STARTED = "started"
    PLAN_GENERATED = "plan_generated"
    AWAITING_FEEDBACK = "awaiting_feedback"
    RESEARCHING = "researching"
    COMPLETED = "completed"
    FAILED = "failed"

class SectionInfo(BaseModel):
    name: str
    description: str
    research_needed: bool

class ResearchPlanResponse(BaseModel):
    thread_id: str
    status: ResearchStatus
    sections: List[SectionInfo]
    feedback_prompt: Optional[str] = None

class ResearchResponse(BaseModel):
    thread_id: str
    status: ResearchStatus
    message: str
    final_report: Optional[str] = None
    sections: Optional[List[SectionInfo]] = None
    feedback_prompt: Optional[str] = None

class ResearchStatusResponse(BaseModel):
    thread_id: str
    status: ResearchStatus
    current_step: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None 