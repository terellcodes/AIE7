"""
Cache Performance Analysis: Test caching behavior with LangGraph agents.

This script analyzes:
1. Cache hits with repeated queries
2. Cache behavior with similar queries
3. Cache directory growth monitoring
4. Performance improvements from caching
"""

import os
import time
import shutil
from typing import List, Dict, Any
from pathlib import Path

# Import helpers from helpers.py
from .helpers import (
    setup_agents, 
    prepare_agent_input, 
    run_agent, 
    quick_clear
)


def get_cache_size(cache_dir: str = "cache/embeddings") -> Dict[str, Any]:
    """
    Get current cache directory size and file count.
    
    Args:
        cache_dir: Path to cache directory
        
    Returns:
        Dictionary with cache size information
    """
    cache_path = Path(cache_dir)
    
    if not cache_path.exists():
        return {
            "exists": False,
            "size_bytes": 0,
            "size_mb": 0,
            "file_count": 0,
            "directory_count": 0
        }
    
    total_size = 0
    file_count = 0
    directory_count = 0
    
    for root, dirs, files in os.walk(cache_path):
        directory_count += len(dirs)
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
                file_count += 1
    
    return {
        "exists": True,
        "size_bytes": total_size,
        "size_mb": round(total_size / (1024 * 1024), 2),
        "file_count": file_count,
        "directory_count": directory_count
    }


def test_cache_hit_performance(agent: Any, query: str, repetitions: int = 3) -> Dict[str, Any]:
    """
    Test cache hit performance with repeated identical queries.
    
    Args:
        agent: LangGraph agent to test
        query: Query to repeat
        repetitions: Number of times to repeat the query
        
    Returns:
        Performance test results
    """
    print(f"🔄 Testing cache hits with '{query[:50]}...' ({repetitions} repetitions)")
    
    results = []
    
    for i in range(repetitions):
        start_time = time.time()
        try:
            response = agent.invoke(prepare_agent_input(query))
            execution_time = time.time() - start_time
            
            # Extract response content
            final_message = response['messages'][-1].content
            if "HELPFULNESS" in final_message:
                final_content = response['messages'][-2].content
            else:
                final_content = final_message
            
            results.append({
                "iteration": i + 1,
                "execution_time": execution_time,
                "response_length": len(final_content),
                "success": True
            })
            
            print(f"   Iteration {i+1}: {execution_time:.2f}s ({len(final_content)} chars)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            results.append({
                "iteration": i + 1,
                "execution_time": execution_time,
                "response_length": 0,
                "success": False,
                "error": str(e)
            })
            print(f"   Iteration {i+1}: Failed - {str(e)}")
    
    # Calculate performance metrics
    successful_results = [r for r in results if r["success"]]
    
    if successful_results:
        first_call_time = successful_results[0]["execution_time"]
        subsequent_times = [r["execution_time"] for r in successful_results[1:]]
        
        if subsequent_times:
            avg_subsequent_time = sum(subsequent_times) / len(subsequent_times)
            speedup = first_call_time / avg_subsequent_time if avg_subsequent_time > 0 else 0
        else:
            speedup = 1.0
        
        performance_metrics = {
            "first_call_time": first_call_time,
            "avg_subsequent_time": avg_subsequent_time if subsequent_times else first_call_time,
            "speedup_factor": round(speedup, 2),
            "total_time": sum(r["execution_time"] for r in successful_results),
            "cache_hits": len(subsequent_times)
        }
    else:
        performance_metrics = {
            "first_call_time": 0,
            "avg_subsequent_time": 0,
            "speedup_factor": 0,
            "total_time": 0,
            "cache_hits": 0
        }
    
    return {
        "query": query,
        "repetitions": repetitions,
        "results": results,
        "performance_metrics": performance_metrics
    }


def test_similar_query_caching(agent: Any, base_query: str, variations: List[str]) -> Dict[str, Any]:
    """
    Test caching behavior with similar but not identical queries.
    
    Args:
        agent: LangGraph agent to test
        base_query: Base query to test first
        variations: List of similar query variations
        
    Returns:
        Similar query caching test results
    """
    print(f"🔍 Testing similar query caching with base: '{base_query[:50]}...'")
    
    # Test base query first
    base_start = time.time()
    try:
        base_response = agent.invoke(prepare_agent_input(base_query))
        base_time = time.time() - base_start
        
        final_message = base_response['messages'][-1].content
        if "HELPFULNESS" in final_message:
            base_content = base_response['messages'][-2].content
        else:
            base_content = final_message
        
        print(f"   Base query: {base_time:.2f}s ({len(base_content)} chars)")
        
    except Exception as e:
        base_time = time.time() - base_start
        base_content = f"Error: {str(e)}"
        print(f"   Base query: Failed - {str(e)}")
    
    # Test variations
    variation_results = []
    
    for i, variation in enumerate(variations):
        var_start = time.time()
        try:
            var_response = agent.invoke(prepare_agent_input(variation))
            var_time = time.time() - var_start
            
            final_message = var_response['messages'][-1].content
            if "HELPFULNESS" in final_message:
                var_content = var_response['messages'][-2].content
            else:
                var_content = final_message
            
            variation_results.append({
                "variation": variation,
                "execution_time": var_time,
                "response_length": len(var_content),
                "time_difference": var_time - base_time,
                "success": True
            })
            
            print(f"   Variation {i+1}: {var_time:.2f}s ({len(var_content)} chars)")
            
        except Exception as e:
            var_time = time.time() - var_start
            variation_results.append({
                "variation": variation,
                "execution_time": var_time,
                "response_length": 0,
                "time_difference": var_time - base_time,
                "success": False,
                "error": str(e)
            })
            print(f"   Variation {i+1}: Failed - {str(e)}")
    
    return {
        "base_query": base_query,
        "base_time": base_time,
        "base_response_length": len(base_content),
        "variations": variation_results,
        "total_variations": len(variations)
    }


def generate_cache_report(
    cache_hit_results: List[Dict[str, Any]], 
    similar_query_results: List[Dict[str, Any]], 
    cache_growth: Dict[str, Any]
) -> str:
    """
    Generate a simple cache performance report.
    
    Args:
        cache_hit_results: Results from cache hit tests
        similar_query_results: Results from similar query tests
        cache_growth: Cache size information
        
    Returns:
        Formatted cache report string
    """
    report = []
    report.append("=" * 60)
    report.append("CACHE PERFORMANCE ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Cache size information
    report.append("CACHE DIRECTORY STATUS:")
    report.append(f"- Exists: {cache_growth['exists']}")
    if cache_growth['exists']:
        report.append(f"- Total size: {cache_growth['size_mb']} MB")
        report.append(f"- File count: {cache_growth['file_count']}")
        report.append(f"- Directory count: {cache_growth['directory_count']}")
    report.append("")
    
    # Cache hit performance
    report.append("CACHE HIT PERFORMANCE:")
    report.append("-" * 30)
    
    for result in cache_hit_results:
        metrics = result['performance_metrics']
        report.append(f"\nQuery: {result['query'][:60]}...")
        report.append(f"  First call: {metrics['first_call_time']:.2f}s")
        report.append(f"  Avg subsequent: {metrics['avg_subsequent_time']:.2f}s")
        report.append(f"  Speedup factor: {metrics['speedup_factor']}x")
        report.append(f"  Cache hits: {metrics['cache_hits']}")
    
    # Similar query analysis
    report.append("\nSIMILAR QUERY CACHING:")
    report.append("-" * 30)
    
    for result in similar_query_results:
        report.append(f"\nBase query: {result['base_query'][:50]}...")
        report.append(f"  Base time: {result['base_time']:.2f}s")
        
        for var in result['variations']:
            status = "✅" if var['success'] else "❌"
            report.append(f"  {status} {var['variation'][:40]}...")
            report.append(f"    Time: {var['execution_time']:.2f}s (diff: {var['time_difference']:+.2f}s)")
    
    report.append("\n" + "=" * 60)
    return "\n".join(report)


def run_cache_performance_analysis():
    """
    Run comprehensive cache performance analysis.
    """
    print("📊 Starting Cache Performance Analysis")
    print("=" * 50)
    
    # Setup agents
    print("Setting up agents...")
    simple_agent, helpful_agent = setup_agents()
    
    # Get initial cache size
    print("\n📁 Checking initial cache status...")
    initial_cache = get_cache_size()
    print(f"Initial cache: {initial_cache['size_mb']} MB, {initial_cache['file_count']} files")
    
    # Test cache hits with repeated queries
    print("\n🔄 Testing cache hit performance...")
    cache_hit_results = []
    
    test_queries = [
        "What are the eligibility requirements for the Direct Loan Program?",
        "How do student loan forgiveness policies work?",
        "What is the current status of student loan debt in the US?"
    ]
    
    for query in test_queries:
        # Test with simple agent
        simple_result = test_cache_hit_performance(simple_agent, query, repetitions=3)
        cache_hit_results.append(simple_result)
        
        # Test with helpful agent
        helpful_result = test_cache_hit_performance(helpful_agent, query, repetitions=3)
        cache_hit_results.append(helpful_result)
    
    # Test similar query caching
    print("\n🔍 Testing similar query caching...")
    similar_query_results = []
    
    similar_query_tests = [
        {
            "base": "What are student loan requirements?",
            "variations": [
                "What are the requirements for student loans?",
                "Tell me about student loan requirements",
                "Student loan requirements information"
            ]
        },
        {
            "base": "How do I apply for student loans?",
            "variations": [
                "What's the application process for student loans?",
                "Student loan application steps",
                "How to get student loans"
            ]
        }
    ]
    
    for test in similar_query_tests:
        # Test with simple agent
        simple_result = test_similar_query_caching(
            simple_agent, 
            test["base"], 
            test["variations"]
        )
        similar_query_results.append(simple_result)
        
        # Test with helpful agent
        helpful_result = test_similar_query_caching(
            helpful_agent, 
            test["base"], 
            test["variations"]
        )
        similar_query_results.append(helpful_result)
    
    # Get final cache size
    print("\n📁 Checking final cache status...")
    final_cache = get_cache_size()
    print(f"Final cache: {final_cache['size_mb']} MB, {final_cache['file_count']} files")
    
    # Calculate cache growth
    cache_growth = {
        "exists": final_cache['exists'],
        "size_bytes": final_cache['size_bytes'],
        "size_mb": final_cache['size_mb'],
        "file_count": final_cache['file_count'],
        "directory_count": final_cache['directory_count'],
        "growth_bytes": final_cache['size_bytes'] - initial_cache['size_bytes'],
        "growth_mb": round((final_cache['size_bytes'] - initial_cache['size_bytes']) / (1024 * 1024), 2),
        "file_growth": final_cache['file_count'] - initial_cache['file_count']
    }
    
    # Generate and display report
    print("\n" + "="*60)
    print("📊 GENERATING CACHE PERFORMANCE REPORT")
    print("="*60)
    
    report = generate_cache_report(cache_hit_results, similar_query_results, cache_growth)
    print(report)
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"cache_performance_{timestamp}.json"
    
    results_data = {
        "timestamp": timestamp,
        "initial_cache": initial_cache,
        "final_cache": final_cache,
        "cache_growth": cache_growth,
        "cache_hit_results": cache_hit_results,
        "similar_query_results": similar_query_results
    }
    
    with open(results_file, 'w') as f:
        import json
        json.dump(results_data, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return results_data


if __name__ == "__main__":
    # Clear cache before testing
    print("🧹 Clearing cache before testing...")
    quick_clear()
    
    # Run cache performance analysis
    results = run_cache_performance_analysis()
    
    print("\n🎉 Cache performance analysis completed successfully!")
    print("Check the generated report above for detailed analysis.")
