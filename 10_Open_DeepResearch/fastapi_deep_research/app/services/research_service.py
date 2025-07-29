from app.services.graph_service import GraphService
from app.models.requests import ResearchRequest, FeedbackRequest
from app.models.responses import ResearchResponse, ResearchStatus
from app.core.dependencies import validate_api_keys, get_graph_config

class ResearchService:
    def __init__(self):
        self.graph_service = GraphService()
    
    async def start_research(self, request: ResearchRequest) -> ResearchResponse:
        """Start a new research session"""
        # Validate API keys
        api_keys = validate_api_keys(request)
        
        # Get graph configuration
        config = get_graph_config(request)
        
        # Start research
        thread_id, result = await self.graph_service.start_research(
            request.topic, 
            config, 
            api_keys
        )
        
        return ResearchResponse(
            thread_id=thread_id,
            status=result["status"],
            message="Research started successfully",
            final_report=result.get("final_report"),
            sections=result.get("sections"),
            feedback_prompt=result.get("feedback_prompt")
        )
    
    async def provide_feedback(self, request: FeedbackRequest) -> ResearchResponse:
        """Provide feedback to continue research"""
        result = await self.graph_service.provide_feedback(
            request.thread_id,
            request.feedback,
            request.approve
        )
        
        return ResearchResponse(
            thread_id=request.thread_id,
            status=result["status"],
            message="Feedback provided successfully",
            final_report=result.get("final_report"),
            sections=result.get("sections"),
            feedback_prompt=result.get("feedback_prompt")
        )
    
    def get_research_status(self, thread_id: str) -> ResearchResponse:
        """Get current research status"""
        status_info = self.graph_service.get_session_status(thread_id)
        
        if not status_info:
            return ResearchResponse(
                thread_id=thread_id,
                status=ResearchStatus.FAILED,
                message="Session not found"
            )
        
        return ResearchResponse(
            thread_id=thread_id,
            status=status_info["status"],
            message="Status retrieved successfully",
            final_report=status_info.get("final_report")
        ) 