import uuid
import os
from typing import Dict, Any, Optional
from app.graph.graph_builder import build_graph, Configuration
from app.models.responses import ResearchStatus
from langgraph.types import Command

class GraphService:
    def __init__(self):
        self.graph = build_graph()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def _set_environment_variables(self, api_keys: dict):
        """Set environment variables for API keys"""
        for key, value in api_keys.items():
            os.environ[key] = value
    
    async def start_research(self, topic: str, config_dict: dict, api_keys: dict) -> tuple[str, dict]:
        """Start a new research session"""
        thread_id = str(uuid.uuid4())
        
        # Set API keys in environment
        self._set_environment_variables(api_keys)
        
        # Create configuration
        config = Configuration.from_dict(config_dict)
        
        # Store session info
        self._active_sessions[thread_id] = {
            "status": ResearchStatus.STARTED,
            "topic": topic,
            "config": config,
            "api_keys": api_keys
        }
        
        # Start graph execution
        graph_config = {"configurable": {"thread_id": thread_id, **config_dict}}
        
        try:
            result = None
            async for chunk in self.graph.astream(
                {"topic": topic}, 
                graph_config,
                stream_mode="updates"
            ):
                result = chunk
                
                # Check for interrupt (feedback needed)
                if isinstance(chunk, dict) and '__interrupt__' in chunk:
                    interrupt_data = chunk['__interrupt__'][0].value
                    self._active_sessions[thread_id]["status"] = ResearchStatus.AWAITING_FEEDBACK
                    self._active_sessions[thread_id]["interrupt_data"] = interrupt_data
                    return thread_id, {
                        "status": ResearchStatus.AWAITING_FEEDBACK,
                        "feedback_prompt": interrupt_data.get("feedback_prompt"),
                        "sections": interrupt_data.get("sections", [])
                    }
                
                # Check for completion
                if isinstance(chunk, dict) and 'compile_final_report' in chunk:
                    final_report = chunk['compile_final_report'].get('final_report')
                    if final_report:
                        self._active_sessions[thread_id]["status"] = ResearchStatus.COMPLETED
                        self._active_sessions[thread_id]["final_report"] = final_report
                        return thread_id, {
                            "status": ResearchStatus.COMPLETED,
                            "final_report": final_report
                        }
            
            return thread_id, {"status": ResearchStatus.RESEARCHING}
            
        except Exception as e:
            self._active_sessions[thread_id]["status"] = ResearchStatus.FAILED
            self._active_sessions[thread_id]["error"] = str(e)
            raise e
    
    async def provide_feedback(self, thread_id: str, feedback: str, approve: bool) -> dict:
        """Provide feedback to continue research"""
        if thread_id not in self._active_sessions:
            raise ValueError("Invalid thread ID")
        
        session = self._active_sessions[thread_id]
        if session["status"] != ResearchStatus.AWAITING_FEEDBACK:
            raise ValueError("Session is not awaiting feedback")
        
        # Set API keys again
        self._set_environment_variables(session["api_keys"])
        
        # Get the original config
        config_dict = {
            "report_structure": session["config"].report_structure,
            "number_of_queries": session["config"].number_of_queries,
            "max_search_depth": session["config"].max_search_depth,
            "planner_provider": session["config"].planner_provider,
            "planner_model": session["config"].planner_model,
            "writer_provider": session["config"].writer_provider,
            "writer_model": session["config"].writer_model,
            "search_api": session["config"].search_api,
            "search_api_config": session["config"].search_api_config
        }
        
        graph_config = {"configurable": {"thread_id": thread_id, **config_dict}}
        
        # Provide feedback or approval
        command = Command(resume=True if approve else feedback)
        
        try:
            result = None
            async for chunk in self.graph.astream(
                command,
                graph_config,
                stream_mode="updates"
            ):
                result = chunk
                
                # Check for completion
                if isinstance(chunk, dict) and 'compile_final_report' in chunk:
                    final_report = chunk['compile_final_report'].get('final_report')
                    if final_report:
                        session["status"] = ResearchStatus.COMPLETED
                        session["final_report"] = final_report
                        return {
                            "status": ResearchStatus.COMPLETED,
                            "final_report": final_report
                        }
                
                # Check if we need feedback again
                if isinstance(chunk, dict) and '__interrupt__' in chunk:
                    interrupt_data = chunk['__interrupt__'][0].value
                    session["status"] = ResearchStatus.AWAITING_FEEDBACK
                    session["interrupt_data"] = interrupt_data
                    return {
                        "status": ResearchStatus.AWAITING_FEEDBACK,
                        "feedback_prompt": interrupt_data.get("feedback_prompt"),
                        "sections": interrupt_data.get("sections", [])
                    }
            
            session["status"] = ResearchStatus.RESEARCHING
            return {"status": ResearchStatus.RESEARCHING}
            
        except Exception as e:
            session["status"] = ResearchStatus.FAILED
            session["error"] = str(e)
            raise e
    
    def get_session_status(self, thread_id: str) -> Optional[dict]:
        """Get the current status of a research session"""
        if thread_id not in self._active_sessions:
            return None
        
        session = self._active_sessions[thread_id]
        return {
            "status": session["status"],
            "topic": session["topic"],
            "final_report": session.get("final_report"),
            "error": session.get("error")
        } 