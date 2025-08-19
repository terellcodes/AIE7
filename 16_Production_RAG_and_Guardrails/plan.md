file to update: 
- guard_rail_agent.py

Solve the following problem: 
##### 🏗️ Activity #3: Building a Production-Safe LangGraph Agent with Guardrails

**Your Mission**: Enhance the existing LangGraph agent by adding a **Guardrails validation node** that ensures all interactions are safe, on-topic, and compliant.

**📋 Requirements:**

1. **Create a Guardrails Node**: 
   - Implement input validation (jailbreak, topic, PII detection)
   - Implement output validation (content moderation, factuality)
   - Handle guard failures gracefully

2. **Integrate with Agent Workflow**:
   - Add guards as a pre-processing step
   - Add guards as a post-processing step  
   - Implement refinement loops for failed validations

3. **Test with Adversarial Scenarios**:
   - Test jailbreak attempts
   - Test off-topic queries
   - Test inappropriate content generation
   - Test PII leakage scenarios

**🎯 Success Criteria:**
- Agent blocks malicious inputs while allowing legitimate queries
- Agent produces safe, factual, on-topic responses
- System gracefully handles edge cases and provides helpful error messages
- Performance remains acceptable with guard overhead

**💡 Implementation Hints:**
- Use LangGraph's conditional routing for guard decisions
- Implement both synchronous and asynchronous guard validation
- Add comprehensive logging for security monitoring
- Consider guard performance vs security trade-offs

- Approach
    - create a new graph 
        - should be similar to the graph created by  create_helpful_langgraph_agent()
        - this is the parent graph
        - create a new function called create_langgraph_agent_with_guardrails()
    - should include two additional subgraphs
        1. before the agent node, to apply guardrails to the input to the agent
        2. after the helpfulness node, to apply guardrails to the output
    - input guard rail agent:
        - overview: input -> input_guardrail_node -> conditional edge
            - apply guard rails: RestrictToTopic, DetectJailBraik,ProganityFree
            - conditional edge:
                - if all guardrails pass: pass input back to the parent graph
                - if any fail:
                    - end the agent run with a message specifying why the input was blocked
                        - use an llm for this
    - output guard rail agent:
        - overview: input -> input_guardrail_node -> conditional edge
            - apply relevant guardrails (just two or three)
            - conditional edge:
                - if all guardrails pass: pass input back to the parent graph
                - if any fail:
                    - end the agent run with a message specifying why the output was blocked
                        - use an llm for this


libraries docs to use via Context7 mcp:
- LangChain
- guardrails