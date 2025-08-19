"""
Compare Agent Behaviors: Analyze differences between simple and helpful LangGraph agents.

This script focuses on:
1. Tool selection patterns and decision-making
2. Response time and performance analysis
3. Response quality and content assessment
4. Helpfulness evaluation results and patterns
"""

import json
import time
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Import helpers from helpers.py
from .helpers import (
    setup_agents, 
    prepare_agent_input, 
    run_agent, 
    quick_clear
)


@dataclass
class AgentResponse:
    """Structured data for agent response analysis."""
    query: str
    agent_type: str
    response_content: str
    execution_time: float
    tool_usage: Dict[str, Any]
    message_count: int
    helpfulness_loop_count: int
    success: bool
    error_message: str = ""


@dataclass
class ComparisonResult:
    """Structured data for agent comparison results."""
    query: str
    simple_agent: AgentResponse
    helpful_agent: AgentResponse
    performance_difference: float
    tool_usage_difference: Dict[str, Any]
    response_quality_metrics: Dict[str, Any]
    helpfulness_analysis: Dict[str, Any]


def analyze_agent_behavior(response: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
    """
    Deep analysis of agent behavior and decision-making patterns.
    
    Args:
        response: Agent response dictionary
        agent_type: Type of agent ('simple' or 'helpful')
        
    Returns:
        Behavioral analysis dictionary
    """
    behavior = {
        "agent_type": agent_type,
        "message_count": len(response.get('messages', [])),
        "has_tool_calls": False,
        "tool_calls_count": 0,
        "tools_used": [],
        "helpfulness_loop_count": 0,
        "response_pattern": "direct",
        "decision_making": {}
    }
    
    messages = response.get('messages', [])
    
    # Analyze message flow and tool usage
    for i, message in enumerate(messages):
        if hasattr(message, 'tool_calls') and message.tool_calls:
            behavior["has_tool_calls"] = True
            behavior["tool_calls_count"] += len(message.tool_calls)
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                behavior["tools_used"].append(tool_name)
                
                # Analyze tool call reasoning
                if hasattr(tool_call, 'args'):
                    behavior["decision_making"][f"tool_call_{i}"] = {
                        "tool": tool_name,
                        "reasoning": getattr(tool_call, 'args', {})
                    }
    
    # Count helpfulness evaluation loops
    helpfulness_messages = [m for m in messages if "HELPFULNESS:" in getattr(m, 'content', '')]
    behavior["helpfulness_loop_count"] = len(helpfulness_messages)
    
    # Determine response pattern
    if behavior["has_tool_calls"]:
        behavior["response_pattern"] = "tool_enhanced"
    elif behavior["helpfulness_loop_count"] > 0:
        behavior["response_pattern"] = "helpfulness_evaluated"
    
    return behavior


def measure_response_quality(response_content: str, query: str) -> Dict[str, Any]:
    """
    Assess the quality of agent responses.
    
    Args:
        response_content: The response text to analyze
        query: The original query for context
        
    Returns:
        Quality metrics dictionary
    """
    quality_metrics = {
        "length": len(response_content),
        "word_count": len(response_content.split()),
        "sentence_count": len([s for s in response_content.split('.') if s.strip()]),
        "has_error": "error" in response_content.lower() or "exception" in response_content.lower(),
        "completeness_score": 0,
        "relevance_score": 0
    }
    
    # Calculate completeness score (basic heuristic)
    query_words = set(query.lower().split())
    response_words = set(response_content.lower().split())
    if query_words:
        common_words = query_words.intersection(response_words)
        quality_metrics["completeness_score"] = len(common_words) / len(query_words)
    
    # Calculate relevance score (basic heuristic)
    if quality_metrics["word_count"] > 0:
        quality_metrics["relevance_score"] = min(1.0, quality_metrics["word_count"] / 50)  # Normalize by expected length
    
    return quality_metrics


def analyze_helpfulness_patterns(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze helpfulness evaluation patterns and results.
    
    Args:
        response: Agent response dictionary
        
    Returns:
        Helpfulness analysis dictionary
    """
    helpfulness_analysis = {
        "total_evaluations": 0,
        "final_decision": "unknown",
        "loop_pattern": [],
        "evaluation_timeline": [],
        "convergence_speed": 0
    }
    
    messages = response.get('messages', [])
    
    # Extract helpfulness evaluation messages
    helpfulness_messages = []
    for i, message in enumerate(messages):
        content = getattr(message, 'content', '')
        if "HELPFULNESS:" in content:
            helpfulness_messages.append({
                "index": i,
                "content": content,
                "decision": "Y" if "Y" in content else "N" if "N" in content else "END"
            })
    
    helpfulness_analysis["total_evaluations"] = len(helpfulness_messages)
    
    if helpfulness_messages:
        # Analyze the pattern
        decisions = [msg["decision"] for msg in helpfulness_messages]
        helpfulness_analysis["loop_pattern"] = decisions
        
        # Find final decision
        final_msg = helpfulness_messages[-1]
        helpfulness_analysis["final_decision"] = final_msg["decision"]
        
        # Calculate convergence speed
        if final_msg["decision"] == "Y":
            helpfulness_analysis["convergence_speed"] = len(helpfulness_messages)
        
        # Create evaluation timeline
        helpfulness_analysis["evaluation_timeline"] = [
            {
                "step": i + 1,
                "decision": msg["decision"],
                "message_index": msg["index"]
            }
            for i, msg in enumerate(helpfulness_messages)
        ]
    
    return helpfulness_analysis


def run_agent_with_analysis(agent: Any, query: str, agent_type: str) -> AgentResponse:
    """
    Run an agent with comprehensive analysis and timing.
    
    Args:
        agent: LangGraph agent to test
        query: Query string to test
        agent_type: Type of agent ('simple' or 'helpful')
        
    Returns:
        AgentResponse object with analysis
    """
    print(f"🧪 Testing {agent_type} agent with: '{query[:50]}...'")
    
    start_time = time.time()
    try:
        response = agent.invoke(prepare_agent_input(query))
        execution_time = time.time() - start_time
        
        # Extract final response content
        final_message = response['messages'][-1].content
        if "HELPFULNESS" in final_message:
            final_content = response['messages'][-2].content
        else:
            final_content = final_message
        
        # Analyze behavior and quality
        behavior = analyze_agent_behavior(response, agent_type)
        quality = measure_response_quality(final_content, query)
        helpfulness = analyze_helpfulness_patterns(response)
        
        # Create structured response
        agent_response = AgentResponse(
            query=query,
            agent_type=agent_type,
            response_content=final_content,
            execution_time=execution_time,
            tool_usage=behavior,
            message_count=behavior["message_count"],
            helpfulness_loop_count=behavior["helpfulness_loop_count"],
            success=True
        )
        
        print(f"✅ {agent_type} agent completed in {execution_time:.2f}s")
        print(f"   Tools used: {behavior['tools_used']}")
        print(f"   Helpfulness loops: {behavior['helpfulness_loop_count']}")
        
        return agent_response
        
    except Exception as e:
        execution_time = time.time() - start_time
        agent_response = AgentResponse(
            query=query,
            agent_type=agent_type,
            response_content=f"Error: {str(e)}",
            execution_time=execution_time,
            tool_usage={},
            message_count=0,
            helpfulness_loop_count=0,
            success=False,
            error_message=str(e)
        )
        print(f"❌ {agent_type} agent failed: {str(e)}")
        return agent_response


def compare_agent_responses(simple_response: AgentResponse, helpful_response: AgentResponse) -> ComparisonResult:
    """
    Compare responses from both agents and analyze differences.
    
    Args:
        simple_response: Response from simple agent
        helpful_response: Response from helpful agent
        
    Returns:
        ComparisonResult object with analysis
    """
    # Performance comparison
    performance_diff = helpful_response.execution_time - simple_response.execution_time
    
    # Tool usage comparison
    tool_usage_diff = {
        "simple_tools": simple_response.tool_usage.get('tools_used', []),
        "helpful_tools": helpful_response.tool_usage.get('tools_used', []),
        "tool_count_difference": len(helpful_response.tool_usage.get('tools_used', [])) - len(simple_response.tool_usage.get('tools_used', [])),
        "unique_tools_helpful": set(helpful_response.tool_usage.get('tools_used', [])) - set(simple_response.tool_usage.get('tools_used', []))
    }
    
    # Response quality comparison
    simple_quality = measure_response_quality(simple_response.response_content, simple_response.query)
    helpful_quality = measure_response_quality(helpful_response.response_content, helpful_response.query)
    
    response_quality_metrics = {
        "simple_quality": simple_quality,
        "helpful_quality": helpful_quality,
        "quality_improvement": {
            "length_difference": helpful_quality["length"] - simple_quality["length"],
            "completeness_improvement": helpful_quality["completeness_score"] - simple_quality["completeness_score"],
            "relevance_improvement": helpful_quality["relevance_score"] - simple_quality["relevance_score"]
        }
    }
    
    # Helpfulness analysis comparison
    simple_helpfulness = analyze_helpfulness_patterns({"messages": [simple_response.response_content]})
    helpful_helpfulness = analyze_helpfulness_patterns({"messages": [helpful_response.response_content]})
    
    helpfulness_analysis = {
        "simple_helpfulness": simple_helpfulness,
        "helpful_helpfulness": helpful_helpfulness,
        "helpfulness_advantage": helpful_response.helpfulness_loop_count > simple_response.helpfulness_loop_count
    }
    
    return ComparisonResult(
        query=simple_response.query,
        simple_agent=simple_response,
        helpful_agent=helpful_response,
        performance_difference=performance_diff,
        tool_usage_difference=tool_usage_diff,
        response_quality_metrics=response_quality_metrics,
        helpfulness_analysis=helpfulness_analysis
    )


def generate_behavioral_report(comparison_results: List[ComparisonResult]) -> str:
    """
    Generate a comprehensive behavioral analysis report.
    
    Args:
        comparison_results: List of comparison results
        
    Returns:
        Formatted behavioral report string
    """
    report = []
    report.append("=" * 80)
    report.append("LANGGRAPH AGENT BEHAVIORAL COMPARISON REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Overall statistics
    total_queries = len(comparison_results)
    successful_comparisons = sum(1 for r in comparison_results if r.simple_agent.success and r.helpful_agent.success)
    
    # Performance analysis
    performance_diffs = [r.performance_difference for r in comparison_results if r.simple_agent.success and r.helpful_agent.success]
    avg_performance_diff = statistics.mean(performance_diffs) if performance_diffs else 0
    
    # Tool usage analysis
    all_tools_used = []
    for result in comparison_results:
        all_tools_used.extend(result.helpful_agent.tool_usage.get('tools_used', []))
    
    tool_frequency = {}
    for tool in all_tools_used:
        tool_frequency[tool] = tool_frequency.get(tool, 0) + 1
    
    report.append("OVERALL BEHAVIORAL STATISTICS:")
    report.append(f"- Total queries compared: {total_queries}")
    report.append(f"- Successful comparisons: {successful_comparisons}")
    report.append(f"- Average performance difference: {avg_performance_diff:.2f}s")
    report.append("")
    
    # Behavioral patterns
    report.append("BEHAVIORAL PATTERNS:")
    report.append("-" * 40)
    
    for result in comparison_results:
        report.append(f"\nQuery: {result.query[:60]}...")
        report.append(f"  Simple Agent:")
        report.append(f"    - Tools: {result.simple_agent.tool_usage.get('tools_used', [])}")
        report.append(f"    - Time: {result.simple_agent.execution_time:.2f}s")
        report.append(f"    - Pattern: {result.simple_agent.tool_usage.get('response_pattern', 'unknown')}")
        
        report.append(f"  Helpful Agent:")
        report.append(f"    - Tools: {result.helpful_agent.tool_usage.get('tools_used', [])}")
        report.append(f"    - Time: {result.helpful_agent.execution_time:.2f}s")
        report.append(f"    - Pattern: {result.helpful_agent.tool_usage.get('response_pattern', 'unknown')}")
        report.append(f"    - Helpfulness loops: {result.helpful_agent.helpfulness_loop_count}")
        
        report.append(f"  Comparison:")
        report.append(f"    - Performance diff: {result.performance_difference:+.2f}s")
        report.append(f"    - Tool advantage: {len(result.tool_usage_difference['unique_tools_helpful'])} additional tools")
        report.append(f"    - Quality improvement: {result.response_quality_metrics['quality_improvement']['length_difference']:+d} chars")
    
    # Tool usage breakdown
    report.append("\n" + "=" * 80)
    report.append("TOOL USAGE BEHAVIORAL ANALYSIS:")
    report.append("=" * 80)
    
    for tool, count in sorted(tool_frequency.items(), key=lambda x: x[1], reverse=True):
        report.append(f"- {tool}: {count} uses")
    
    # Helpfulness evaluation patterns
    report.append("\n" + "=" * 80)
    report.append("HELPFULNESS EVALUATION PATTERNS:")
    report.append("=" * 80)
    
    helpfulness_patterns = {}
    for result in comparison_results:
        if result.helpful_agent.helpfulness_loop_count > 0:
            pattern = tuple(result.helpful_agent.tool_usage.get('loop_pattern', []))
            helpfulness_patterns[pattern] = helpfulness_patterns.get(pattern, 0) + 1
    
    for pattern, count in sorted(helpfulness_patterns.items(), key=lambda x: x[1], reverse=True):
        report.append(f"- Pattern {pattern}: {count} occurrences")
    
    report.append("\n" + "=" * 80)
    return "\n".join(report)


def run_behavioral_comparison():
    """
    Run comprehensive behavioral comparison between agents.
    """
    print("🔍 Starting Agent Behavioral Comparison Analysis")
    print("=" * 60)
    
    # Setup agents
    print("Setting up agents...")
    simple_agent, helpful_agent = setup_agents()
    
    # Define test queries that highlight behavioral differences
    test_queries = [
        "What are the eligibility requirements for the Direct Loan Program?",
        "How do student loan forgiveness policies work?",
        "What is the current status of student loan debt in the US?",
        "Explain the difference between subsidized and unsubsidized loans",
        "What are the latest developments in student loan policy?",
        "How do student loans affect credit scores?",
        "What are the repayment options for federal student loans?",
        "How do student loans compare to other types of debt?"
    ]
    
    # Run behavioral analysis
    comparison_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*20} Query {i}/{len(test_queries)} {'='*20}")
        print(f"Query: {query}")
        
        # Test simple agent
        simple_response = run_agent_with_analysis(simple_agent, query, "simple")
        
        # Test helpful agent
        helpful_response = run_agent_with_analysis(helpful_agent, query, "helpful")
        
        # Compare responses
        comparison = compare_agent_responses(simple_response, helpful_response)
        comparison_results.append(comparison)
        
        print(f"📊 Comparison Summary:")
        print(f"   Performance difference: {comparison.performance_difference:+.2f}s")
        print(f"   Tool usage difference: {comparison.tool_usage_difference['tool_count_difference']:+d} tools")
        print(f"   Quality improvement: {comparison.response_quality_metrics['quality_improvement']['length_difference']:+d} chars")
    
    # Generate and display behavioral report
    print("\n" + "="*80)
    print("📊 GENERATING BEHAVIORAL ANALYSIS REPORT")
    print("="*80)
    
    report = generate_behavioral_report(comparison_results)
    print(report)
    
    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"behavioral_comparison_{timestamp}.json"
    
    # Convert dataclasses to dictionaries for JSON serialization
    serializable_results = []
    for result in comparison_results:
        serializable_result = {
            "query": result.query,
            "simple_agent": asdict(result.simple_agent),
            "helpful_agent": asdict(result.helpful_agent),
            "performance_difference": result.performance_difference,
            "tool_usage_difference": result.tool_usage_difference,
            "response_quality_metrics": result.response_quality_metrics,
            "helpfulness_analysis": result.helpfulness_analysis
        }
        serializable_results.append(serializable_result)
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed behavioral analysis saved to: {results_file}")
    
    return comparison_results


if __name__ == "__main__":
    # Clear cache before testing
    quick_clear()
    
    # Run behavioral comparison
    results = run_behavioral_comparison()
    
    print("\n🎉 Behavioral comparison completed successfully!")
    print("Check the generated report above for detailed behavioral analysis.")
