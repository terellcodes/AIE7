#!/usr/bin/env python3
"""
Runner script for cache performance analysis with LangGraph agents.

This script can be run directly to execute the cache performance analysis.
"""

import sys
import os

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph_agent_lib.analysis.cache_performance import run_cache_performance_analysis

if __name__ == "__main__":
    print("📊 Starting Cache Performance Analysis...")
    print("=" * 50)
    
    try:
        results = run_cache_performance_analysis()
        print(f"\n✅ Cache performance analysis completed!")
        print(f"Cache growth: {results['cache_growth']['growth_mb']} MB")
        print(f"Files added: {results['cache_growth']['file_growth']}")
        
    except Exception as e:
        print(f"\n❌ Cache performance analysis failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
