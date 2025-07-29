#!/usr/bin/env python3
"""
Test script for the Deep Research API

This script tests the basic functionality of the FastAPI application
without requiring actual API keys.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Set dummy environment variables to avoid API key errors during testing
os.environ["TAVILY_API_KEY"] = "test_key"
os.environ["ANTHROPIC_API_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

async def test_import_modules():
    """Test that all modules can be imported correctly"""
    print("Testing module imports...")
    
    try:
        # Test core modules
        from app.core.config import settings
        from app.core.dependencies import validate_api_keys, get_graph_config
        print("✅ Core modules imported successfully")
        
        # Test models
        from app.models.requests import ResearchRequest, FeedbackRequest
        from app.models.responses import ResearchResponse, ResearchStatus
        print("✅ Model modules imported successfully")
        
        # Test graph modules
        from app.graph.state import ReportState, Section, SearchQuery
        from app.graph.utils import get_config_value, format_sections
        from app.graph.graph_builder import Configuration, build_graph
        print("✅ Graph modules imported successfully")
        
        # Test services
        from app.services.graph_service import GraphService
        from app.services.research_service import ResearchService
        print("✅ Service modules imported successfully")
        
        # Test API
        from app.api.endpoints.research import router
        from app.main import app
        print("✅ API modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_pydantic_models():
    """Test Pydantic model validation"""
    print("\nTesting Pydantic models...")
    
    try:
        from app.models.requests import ResearchRequest
        from app.models.responses import ResearchResponse, ResearchStatus
        from app.graph.state import Section, SearchQuery
        
        # Test Section model
        section = Section(
            name="Test Section",
            description="A test section for validation",
            research=True,
            content=""
        )
        print("✅ Section model works correctly")
        
        # Test SearchQuery model  
        query = SearchQuery(search_query="test query")
        print("✅ SearchQuery model works correctly")
        
        # Test ResearchRequest model
        request = ResearchRequest(
            topic="Test Topic",
            tavily_api_key="test_key",
            anthropic_api_key="test_key"
        )
        print("✅ ResearchRequest model works correctly")
        
        # Test ResearchResponse model
        response = ResearchResponse(
            thread_id="test-thread",
            status=ResearchStatus.STARTED,
            message="Test message"
        )
        print("✅ ResearchResponse model works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Pydantic model error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from app.core.config import settings
        from app.graph.graph_builder import Configuration
        
        # Test settings
        print(f"API Title: {settings.api_title}")
        print(f"API Version: {settings.api_version}")
        print("✅ Settings loaded successfully")
        
        # Test graph configuration
        config = Configuration.from_dict({
            "number_of_queries": 2,
            "max_search_depth": 1,
            "search_api": "tavily"
        })
        print(f"Config queries: {config.number_of_queries}")
        print(f"Config search API: {config.search_api}")
        print("✅ Configuration works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_graph_building():
    """Test graph construction (without execution)"""
    print("\nTesting graph building...")
    
    try:
        from app.graph.graph_builder import build_graph
        
        # This should build the graph without errors
        graph = build_graph()
        print("✅ Graph built successfully")
        print(f"Graph type: {type(graph)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Graph building error: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\nTesting FastAPI app...")
    
    try:
        from app.main import app
        
        # Test that app is created
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
        
        # Test routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/api/v1/research/start", "/api/v1/research/feedback"]
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"✅ Route {expected} found")
            else:
                print(f"❌ Route {expected} missing")
                return False
        
        print("✅ FastAPI app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Deep Research API Tests\n")
    
    tests = [
        test_import_modules(),
        test_pydantic_models(),
        test_configuration(), 
        test_graph_building(),
        test_fastapi_app()
    ]
    
    results = []
    for test in tests:
        if asyncio.iscoroutine(test):
            result = await test
        else:
            result = test
        results.append(result)
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The API is ready to use.")
        print("\nTo start the server, run:")
        print("cd fastapi_deep_research")
        print("source venv/bin/activate")
        print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 