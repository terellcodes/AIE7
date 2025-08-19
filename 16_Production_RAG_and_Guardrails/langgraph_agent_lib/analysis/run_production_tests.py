#!/usr/bin/env python3
"""
Runner script for production readiness testing with LangGraph agents.

This script can be run directly to execute the production readiness tests.
"""

import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))



from langgraph_agent_lib.analysis.production_readiness_tests import run_production_readiness_tests

if __name__ == "__main__":
    print("🏭 Starting Production Readiness Testing...")
    print("=" * 50)

    load_dotenv()

    print(os.getenv("OPENAI_API_KEY"))
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    
    try:        
        results = run_production_readiness_tests()
        print(f"\n✅ Production readiness testing completed!")
        
        # Quick summary
        total_tests = (
            len(results['error_handling_results']) + 
            1 +  # invalid PDF test
            results['missing_api_results'].get("total_tests", 0) +
            len(results['edge_case_results'])
        )
        
        successful_tests = (
            sum(1 for r in results['error_handling_results'] if r["success"]) +
            (1 if results['invalid_pdf_results'].get("success", False) else 0) +
            results['missing_api_results'].get("successful_tests", 0) +
            sum(1 for r in results['edge_case_results'] if r.get("success"))
        )
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        
    except Exception as e:
        print(f"\n❌ Production readiness testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
