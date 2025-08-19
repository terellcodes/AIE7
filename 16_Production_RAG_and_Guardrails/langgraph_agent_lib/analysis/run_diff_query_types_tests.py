#!/usr/bin/env python3
"""
Runner script for testing different query types with LangGraph agents.

This script can be run directly to execute the comprehensive query type tests.
"""

import sys
import os

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph_agent_lib.analysis.test_diff_query_types import run_comprehensive_tests

if __name__ == "__main__":
    print("🚀 Starting Query Type Testing...")
    print("=" * 50)
    
    try:
        results = run_comprehensive_tests()
        print(f"\n✅ Testing completed! Generated {len(results)} test results.")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
