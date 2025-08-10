<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 14: Build & Serve Agentic Graphs with LangGraph</h1>

| 🤓 Pre-work | 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| – | – | – | – | You are here! | – | – |

# Build 🏗️

Run the repository and complete the following:

- 🤝 Breakout Room Part #1 — Building and serving your LangGraph Agent Graph
  - Task 1: Getting Dependencies & Environment
    - Configure `.env` (OpenAI, Tavily, optional LangSmith)
  - Task 2: Serve the Graph Locally
    - `uv run langgraph dev` (API on http://localhost:2024)
  - Task 3: Call the API
    - `uv run test_served_graph.py` (sync SDK example)
  - Task 4: Explore assistants (from `langgraph.json`)
    - `agent` → `simple_agent` (tool-using agent)
    - `agent_helpful` → `agent_with_helpfulness` (separate helpfulness node)

- 🤝 Breakout Room Part #2 — Using LangGraph Studio to visualize the graph
  - Task 1: Open Studio while the server is running
    - https://smith.langchain.com/studio?baseUrl=http://localhost:2024
  - Task 2: Visualize & Stream
    - Start a run and observe node-by-node updates
  - Task 3: Compare Flows
    - Contrast `agent` vs `agent_helpful` (tool calls vs helpfulness decision)

<details>
<summary>🚧 Advanced Build 🚧 (OPTIONAL - <i>open this section for the requirements</i>)</summary>

- Create and deploy a locally hosted MCP server with FastMCP.
- Extend your tools in `tools.py` to allow your LangGraph to consume the MCP Server.
</details>

# Ship 🚢

- Running local server (`langgraph dev`)
- Short demo showing both assistants responding

# Share 🚀
- Walk through your graph in Studio
- Share 3 lessons learned and 3 lessons not learned


#### ❓ Question:

What is the purpose of the `chunk_overlap` parameter when using `RecursiveCharacterTextSplitter` to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?

#### ✅ ANSWER
`chunk_overlap` declares how many characters the current chunk will overlapp with the previous chunk. 

Let's say the `chunk_overlap` is 50 and  the first chunk stops at character 2000. The next chunk will not start at character 2001. Instead it will start at character 1951 which is 2001 - 50).

When one chunk ends, the next begins overlapping the previous chunk by the specified number of characters. This mitigagtes lost meaning between splits.

Increase chunk overlap:
- Pro: Better context retention—especially across chunk boundaries. Fragmented context is less likely to break retrieval. 
- Con: More redundancy—embeddings overlap, increasing storage and compute costs. Retrieval latency and vector DB size may inflate.  


Decrease chunk overlap:
- Pro: Less redundancy—fewer overlapping characters means fewer embeddings for duplicated content, improving efficiency.  
- Higher risk of context loss—semantic meaning that spans a chunk boundary may be partially omitted, reducing RAG accuracy.



#### ❓ Question:

Your retriever is configured with `search_kwargs={"k": 5}`. How would adjusting `k` likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?

#### ✅ ANSWER
**Context Precision** measures the percentage of retrieved chunks that are relevant to the query. Increasing k often lowers precision because you pull in more non-relevant context alongside relevant ones. Decreasing k can raise precision by reducing false positives, but risks missing relevant context entirely.

**Context Recall** measures the percentage of all relevant chunks in the vector store that are actually retrieved. Increasing k improves recall by capturing more of the relevant set, while decreasing k lowers recall by potentially omitting relevant chunks.

Trade-off:
	•	High k → higher recall, lower precision.
	•	Low k → higher precision, lower recall.

The optimal k balances both, and should be tuned with retrieval evaluation (e.g., RAGAS metrics) on representative queries.

Advanced adjustments:
	•	Query optimization → Improves semantic matching, helping both metrics.
	•	Memory-Augmented RAG → Reduces the recall penalty of smaller k by storing relevant context after retrieval.
	•	Contextual compression → Allows for higher k without sacrificing precision by re-ranking or filtering retrieved chunks.


#### ❓ Question:

Compare the `agent` and `agent_helpful` assistants defined in `langgraph.json`. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

#### ✅ ANSWER
The helpfulness evaluator is called after the agent generates a response. If the current response is helpful in answering the user's initial query the agent terminates. The agent also terminates if it has done too much work without coming up with a helpful answer (ie. more than 10 agent-tool-evaluator calls) to avoid and endless agent run.

Execution routes back to the agent if the response is not helpful and agent has not yet been running for too long.
