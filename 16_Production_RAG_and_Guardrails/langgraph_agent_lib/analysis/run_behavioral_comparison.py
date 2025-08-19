#!/usr/bin/env python3
"""
Runner script for comparing agent behaviors with LangGraph agents.

This script can be run directly to execute the comprehensive behavioral comparison analysis.
"""

import sys
import os

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph_agent_lib.analysis.compare_agents import run_behavioral_comparison

if __name__ == "__main__":
    print("🔍 Starting Agent Behavioral Comparison...")
    print("=" * 50)
    
    try:
        results = run_behavioral_comparison()
        print(f"\n✅ Behavioral comparison completed! Generated {len(results)} comparison results.")
        
    except Exception as e:
        print(f"\n❌ Behavioral comparison failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
