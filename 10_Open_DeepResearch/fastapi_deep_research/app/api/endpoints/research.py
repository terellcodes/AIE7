from fastapi import APIRouter, HTTPException, status
from app.models.requests import ResearchRequest, FeedbackRequest
from app.models.responses import ResearchResponse
from app.services.research_service import ResearchService

router = APIRouter(prefix="/research", tags=["research"])
research_service = ResearchService()

@router.post("/start", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """Start a new research session"""
    try:
        return await research_service.start_research(request)
    except Exception as e:
        print(f"Failed to start research: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start research: {str(e)}"
        )

@router.post("/feedback", response_model=ResearchResponse)
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback to continue research"""
    try:
        return await research_service.provide_feedback(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to provide feedback: {str(e)}"
        )

@router.get("/status/{thread_id}", response_model=ResearchResponse)
async def get_research_status(thread_id: str):
    """Get the current status of a research session"""
    try:
        return research_service.get_research_status(thread_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        ) 