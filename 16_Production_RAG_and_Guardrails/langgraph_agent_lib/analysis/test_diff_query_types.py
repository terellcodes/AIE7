"""
Test different query types with LangGraph agents to demonstrate tool usage patterns.

This script tests:
1. RAG-focused queries (should use RAG tool)
2. Current events queries (should use Tavily search)
3. Academic research queries (should use Arxiv tool)
4. Complex multi-step queries (should use multiple tools)
"""

import json
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Import helpers from helpers.py
from .helpers import (
    setup_agents, 
    prepare_agent_input, 
    run_agent, 
    quick_clear
)


def analyze_tool_usage(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze which tools were used in the agent response.
    
    Args:
        response: Agent response dictionary
        
    Returns:
        Dictionary with tool usage analysis
    """
    tool_usage = {
        "tools_used": [],
        "tool_calls_count": 0,
        "has_tool_calls": False,
        "response_type": "direct"
    }
    
    messages = response.get('messages', [])
    
    for message in messages:
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_usage["has_tool_calls"] = True
            tool_usage["tool_calls_count"] = len(message.tool_calls)
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.get('name', 'unknown')
                tool_usage["tools_used"].append(tool_name)
    
    if tool_usage["has_tool_calls"]:
        tool_usage["response_type"] = "tool_enhanced"
    
    return tool_usage


def compare_responses(
    simple_response: str, 
    helpful_response: str, 
    simple_tools: Dict[str, Any], 
    helpful_tools: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare responses from both agents.
    
    Args:
        simple_response: Response from simple agent
        helpful_response: Response from helpful agent
        simple_tools: Tool usage from simple agent
        helpful_tools: Tool usage from helpful agent
        
    Returns:
        Comparison analysis dictionary
    """
    comparison = {
        "response_length": {
            "simple": len(simple_response),
            "helpful": len(helpful_response)
        },
        "tool_usage": {
            "simple": simple_tools,
            "helpful": helpful_tools
        },
        "response_difference": len(helpful_response) - len(simple_response),
        "helpful_advantage": helpful_tools["tool_calls_count"] > simple_tools["tool_calls_count"]
    }
    
    return comparison


def generate_test_report(
    test_results: List[Dict[str, Any]], 
    query_categories: List[str]
) -> str:
    """
    Generate a comprehensive test report.
    
    Args:
        test_results: List of test results
        query_categories: List of query category names
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("LANGGRAPH AGENT QUERY TYPE TESTING REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary statistics
    total_tests = len(test_results)
    total_tool_calls = sum(
        result["helpful_tools"]["tool_calls_count"] 
        for result in test_results
    )
    
    report.append("SUMMARY STATISTICS:")
    report.append(f"- Total queries tested: {total_tests}")
    report.append(f"- Total tool calls made: {total_tool_calls}")
    report.append(f"- Average tool calls per query: {total_tool_calls/total_tests:.2f}")
    report.append("")
    
    # Category analysis
    report.append("QUERY CATEGORY ANALYSIS:")
    report.append("-" * 40)
    
    for i, category in enumerate(query_categories):
        result = test_results[i]
        report.append(f"\n{category.upper()}:")
        report.append(f"  Query: {result['query']}")
        report.append(f"  Simple Agent Tools: {result['simple_tools']['tools_used']}")
        report.append(f"  Helpful Agent Tools: {result['helpful_tools']['tools_used']}")
        report.append(f"  Response Length Difference: {result['comparison']['response_difference']} chars")
        report.append(f"  Helpful Agent Advantage: {result['comparison']['helpful_advantage']}")
    
    # Tool usage breakdown
    report.append("\n" + "=" * 80)
    report.append("TOOL USAGE BREAKDOWN:")
    report.append("=" * 80)
    
    tool_counts = {}
    for result in test_results:
        for tool in result['helpful_tools']['tools_used']:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
        report.append(f"- {tool}: {count} uses")
    
    report.append("\n" + "=" * 80)
    return "\n".join(report)


def test_query_category(
    agent: Any, 
    query: str, 
    category: str
) -> Dict[str, Any]:
    """
    Test a specific query with an agent.
    
    Args:
        agent: LangGraph agent to test
        query: Query string to test
        category: Category name for the query
        
    Returns:
        Test result dictionary
    """
    print(f"\n🧪 Testing {category}: '{query}'")
    
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
        
        # Analyze tool usage
        tool_usage = analyze_tool_usage(response)
        
        result = {
            "category": category,
            "query": query,
            "response": final_content,
            "tool_usage": tool_usage,
            "execution_time": execution_time,
            "success": True
        }
        
        print(f"✅ {category} completed in {execution_time:.2f}s")
        print(f"   Tools used: {tool_usage['tools_used']}")
        
    except Exception as e:
        execution_time = time.time() - start_time
        result = {
            "category": category,
            "query": query,
            "response": f"Error: {str(e)}",
            "tool_usage": {"tools_used": [], "tool_calls_count": 0, "has_tool_calls": False, "response_type": "error"},
            "execution_time": execution_time,
            "success": False
        }
        print(f"❌ {category} failed: {str(e)}")
    
    return result


def run_comprehensive_tests():
    """
    Run comprehensive tests on different query types.
    """
    print("🚀 Starting Comprehensive Query Type Testing")
    print("=" * 60)
    
    # Setup agents
    print("Setting up agents...")
    simple_agent, helpful_agent = setup_agents()
    
    # Define test queries by category
    test_queries = [
        {
            "category": "RAG-Focused Query",
            "query": "What are the eligibility requirements for the Direct Loan Program?",
            "expected_tool": "RAG System"
        },
        {
            "category": "Current Events Query", 
            "query": "What are the latest developments in student loan forgiveness policies?",
            "expected_tool": "Tavily Search"
        },
        {
            "category": "Academic Research Query",
            "query": "Find recent research papers about student loan default rates and economic impact",
            "expected_tool": "Arxiv Tool"
        },
        {
            "category": "Complex Multi-Step Query",
            "query": "How do the Direct Loan Program requirements compare to current student loan forgiveness policies, and what does recent research say about their effectiveness?",
            "expected_tool": "Multiple Tools"
        }
    ]
    
    # Run tests
    test_results = []
    
    for test_case in test_queries:
        print(f"\n{'='*20} {test_case['category']} {'='*20}")
        
        # Test simple agent
        simple_result = test_query_category(
            simple_agent, 
            test_case['query'], 
            f"Simple Agent - {test_case['category']}"
        )
        
        # Test helpful agent
        helpful_result = test_query_category(
            helpful_agent, 
            test_case['query'], 
            f"Helpful Agent - {test_case['category']}"
        )
        
        # Compare responses
        comparison = compare_responses(
            simple_result['response'],
            helpful_result['response'],
            simple_result['tool_usage'],
            helpful_result['tool_usage']
        )
        
        # Store combined result
        combined_result = {
            "query": test_case['query'],
            "category": test_case['category'],
            "expected_tool": test_case['expected_tool'],
            "simple_response": simple_result['response'],
            "helpful_response": helpful_result['response'],
            "simple_tools": simple_result['tool_usage'],
            "helpful_tools": helpful_result['tool_usage'],
            "simple_execution_time": simple_result['execution_time'],
            "helpful_execution_time": helpful_result['execution_time'],
            "comparison": comparison
        }
        
        test_results.append(combined_result)
    
    # Generate and display report
    print("\n" + "="*80)
    print("📊 GENERATING COMPREHENSIVE REPORT")
    print("="*80)
    
    query_categories = [test['category'] for test in test_queries]
    report = generate_test_report(test_results, query_categories)
    
    print(report)
    
    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return test_results


if __name__ == "__main__":
    # Clear cache before testing
    quick_clear()
    
    # Run comprehensive tests
    results = run_comprehensive_tests()
    
    print("\n🎉 Testing completed successfully!")
    print("Check the generated report above for detailed analysis.")
