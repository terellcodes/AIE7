# Deep Research API

A FastAPI application that provides research report generation using LangGraph and multiple search APIs.

## Features

- **Multi-API Search**: Supports Tavily, Perplexity, Exa, arXiv, and PubMed
- **Hierarchical Report Generation**: Uses LangGraph for structured report creation
- **Interactive Feedback**: Allows human feedback on report plans
- **Session Management**: Maintains research sessions with checkpointing
- **Configurable Models**: Support for Anthropic Claude, OpenAI, and Groq models

## Setup

### 1. Install Dependencies

```bash
cd fastapi_deep_research
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```env
DEFAULT_TAVILY_API_KEY=your_tavily_key
DEFAULT_ANTHROPIC_API_KEY=your_anthropic_key
DEFAULT_OPENAI_API_KEY=your_openai_key
```

### 3. Run the Application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
python app/main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Start Research

**POST** `/api/v1/research/start`

Start a new research session:

```json
{
  "topic": "Dynamic Chunking for End-to-End Hierarchical Sequence Modeling",
  "tavily_api_key": "your_key",
  "anthropic_api_key": "your_key",
  "search_api": "tavily",
  "number_of_queries": 2,
  "max_search_depth": 1
}
```

Response:
```json
{
  "thread_id": "uuid-string",
  "status": "awaiting_feedback",
  "message": "Research started successfully",
  "feedback_prompt": "Please provide feedback...",
  "sections": [...]
}
```

### 2. Provide Feedback

**POST** `/api/v1/research/feedback`

Provide feedback on the report plan:

```json
{
  "thread_id": "uuid-string",
  "feedback": "Optional feedback text",
  "approve": true
}
```

### 3. Check Status

**GET** `/api/v1/research/status/{thread_id}`

Get the current status of a research session.

## Usage Example

### Python Client

```python
import requests

# Start research
response = requests.post("http://localhost:8000/api/v1/research/start", json={
    "topic": "Machine Learning in Healthcare",
    "tavily_api_key": "your_tavily_key",
    "anthropic_api_key": "your_anthropic_key",
    "search_api": "tavily",
    "number_of_queries": 2,
    "max_search_depth": 1
})

data = response.json()
thread_id = data["thread_id"]

# If feedback needed, approve the plan
if data["status"] == "awaiting_feedback":
    feedback_response = requests.post("http://localhost:8000/api/v1/research/feedback", json={
        "thread_id": thread_id,
        "approve": True
    })

# Check final status
status_response = requests.get(f"http://localhost:8000/api/v1/research/status/{thread_id}")
final_data = status_response.json()

if final_data["status"] == "completed":
    print("Final Report:")
    print(final_data["final_report"])
```

### cURL Examples

```bash
# Start research
curl -X POST "http://localhost:8000/api/v1/research/start" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Artificial Intelligence Ethics",
    "tavily_api_key": "your_key",
    "anthropic_api_key": "your_key"
  }'

# Approve plan
curl -X POST "http://localhost:8000/api/v1/research/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "your-thread-id",
    "approve": true
  }'

# Check status
curl "http://localhost:8000/api/v1/research/status/your-thread-id"
```

## Configuration Options

### Search APIs
- `tavily`: General web search
- `perplexity`: AI-powered search
- `exa`: Semantic web search
- `arxiv`: Academic papers
- `pubmed`: Medical literature

### Model Providers
- `anthropic`: Claude models
- `openai`: GPT models
- `groq`: Groq models

### Research Configuration
- `number_of_queries`: Queries per search iteration (default: 1)
- `max_search_depth`: Maximum search iterations (default: 1)
- `planner_model`: Model for planning (default: claude-sonnet-4-20250514)
- `writer_model`: Model for writing (default: claude-sonnet-4-20250514)

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Architecture

The application follows a clean architecture pattern:

- **API Layer**: FastAPI endpoints
- **Service Layer**: Business logic and orchestration
- **Graph Layer**: LangGraph implementation
- **Core Layer**: Configuration and dependencies

## Development

### Project Structure
```
app/
├── api/endpoints/          # API endpoints
├── core/                   # Configuration and dependencies
├── graph/                  # LangGraph implementation
├── models/                 # Pydantic models
└── services/              # Business logic
```

### Adding New Search APIs

1. Add search function to `app/graph/utils.py`
2. Update `get_search_params()` in utils
3. Add API option to `SearchAPI` enum in models
4. Update search logic in nodes

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are provided
2. **Rate Limiting**: Increase delays between requests in utils
3. **Memory Issues**: Reduce `max_search_depth` and `number_of_queries`
4. **Model Errors**: Check model availability and permissions

### Logs

Check application logs for detailed error information:
```bash
uvicorn app.main:app --log-level debug
```

## License

MIT License - see LICENSE file for details. 