from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from app.graph.state import ReportState, ReportStateInput, ReportStateOutput, SectionState, SectionOutputState
from app.graph.nodes import (
    generate_report_plan, human_feedback_api, generate_queries, search_web, 
    write_section, write_final_sections, gather_completed_sections, 
    initiate_final_section_writing, compile_final_report
)
from app.core.config import settings
from dataclasses import dataclass, fields
from typing import Any, Optional, Dict

@dataclass(kw_only=True)
class Configuration:
    """Configuration class for the graph"""
    report_structure: str = settings.default_report_structure
    number_of_queries: int = 1
    max_search_depth: int = 1
    planner_provider: str = "anthropic"
    planner_model: str = "claude-sonnet-4-20250514"
    writer_provider: str = "anthropic"
    writer_model: str = "claude-sonnet-4-20250514"
    search_api: str = "tavily"
    search_api_config: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Configuration":
        """Create Configuration from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if k in [f.name for f in fields(cls)]})

def build_graph():
    """Build and return the compiled graph with checkpointer"""
    # Build section graph
    section_builder = StateGraph(SectionState, output=SectionOutputState)
    section_builder.add_node("generate_queries", generate_queries)
    section_builder.add_node("search_web", search_web)
    section_builder.add_node("write_section", write_section)
    
    section_builder.add_edge(START, "generate_queries")
    section_builder.add_edge("generate_queries", "search_web")
    section_builder.add_edge("search_web", "write_section")
    
    # Build main graph
    builder = StateGraph(ReportState, input=ReportStateInput, output=ReportStateOutput, config_schema=Configuration)
    builder.add_node("generate_report_plan", generate_report_plan)
    builder.add_node("human_feedback", human_feedback_api)
    builder.add_node("build_section_with_web_research", section_builder.compile())
    builder.add_node("gather_completed_sections", gather_completed_sections)
    builder.add_node("write_final_sections", write_final_sections)
    builder.add_node("compile_final_report", compile_final_report)
    
    builder.add_edge(START, "generate_report_plan")
    builder.add_edge("generate_report_plan", "human_feedback")
    builder.add_edge("build_section_with_web_research", "gather_completed_sections")
    builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
    builder.add_edge("write_final_sections", "compile_final_report")
    builder.add_edge("compile_final_report", END)
    
    # Create memory saver and compile with checkpointer
    memory = MemorySaver()
    return builder.compile(checkpointer=memory) 