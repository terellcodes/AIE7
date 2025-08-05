# OpenAI Agents SDK - Agent Interaction Flow

```mermaid
flowchart TD
    A[User Input: Research Query] --> B[ResearchManager]
    
    B --> C[Planner Agent]
    C --> |WebSearchPlan| D{Search Plan Created}
    D --> |5-20 search terms| E[Search Agent Pool]
    
    E --> F[WebSearchTool]
    F --> |Search Results| G[Search Summaries]
    G --> |Batch Processing| H[All Searches Complete]
    
    H --> I[Writer Agent]
    I --> |ReportData| J[Final Report Output]
    
    subgraph "Planner Agent Details"
        C1[Instructions: PLANNER_PROMPT]
        C2[Model: GPT-4.1]
        C3[Output: WebSearchPlan]
        C4[Structure: WebSearchItem list]
    end
    
    subgraph "Search Agent Details"
        E1[Instructions: SEARCH_PROMPT]
        E2[Tools: WebSearchTool]
        E3[Tool Choice: Required]
        E4[Concurrent Processing: Max 5]
    end
    
    subgraph "Writer Agent Details"
        I1[Instructions: WRITER_PROMPT]
        I2[Model: o3-mini reasoning model]
        I3[Output: ReportData]
        I4[Content: Summary + Markdown + Questions]
    end
    
    C -.-> C1
    C -.-> C2
    C -.-> C3
    C -.-> C4
    
    E -.-> E1
    E -.-> E2
    E -.-> E3
    E -.-> E4
    
    I -.-> I1
    I -.-> I2
    I -.-> I3
    I -.-> I4
    
    subgraph "Data Flow"
        K[Query String] --> L[WebSearchPlan Object]
        L --> M[List of Search Results]
        M --> N[ReportData Object]
        N --> O[Markdown Report + Follow-up Questions]
    end
    
    subgraph "Progress Tracking"
        P[Printer Class]
        P --> Q[Real-time Updates]
        Q --> R[Rich Console Display]
        R --> S[Spinners & Checkmarks]
    end
    
    B -.-> P
    
    style A fill:#e1f5fe
    style J fill:#c8e6c9
    style C fill:#fff3e0
    style E fill:#f3e5f5
    style I fill:#fce4ec
```

## Agent Interaction Summary

### Flow Steps:
1. **User Query** → ResearchManager receives the research topic
2. **Planning Phase** → Planner Agent breaks down query into 5-20 search terms
3. **Research Phase** → Search Agent performs concurrent web searches (max 5 at a time)
4. **Synthesis Phase** → Writer Agent creates comprehensive report with follow-up questions

### Key Features:
- **Structured Output**: Each agent uses Pydantic models for predictable data flow
- **Concurrent Processing**: Search operations run in parallel for efficiency  
- **Progress Tracking**: Real-time updates via Printer class with Rich console
- **Error Handling**: Graceful failure handling in search operations
- **Tracing**: Built-in OpenAI tracing for observability

### Agent Specialization:
- **Planner**: Strategic query decomposition
- **Search**: Information gathering with web tools
- **Writer**: Synthesis using reasoning model (o3-mini)