from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send
from langgraph.types import interrupt, Command
from app.graph.state import ReportState, SectionState, Section, Sections, Queries, Feedback, SearchQuery
from app.graph.utils import (
    get_config_value, get_search_params, tavily_search_async, perplexity_search, 
    exa_search, arxiv_search_async, pubmed_search_async, deduplicate_and_format_sources,
    format_sections
)

# Prompt templates
report_planner_query_writer_instructions = """You are performing research for a report. 

<Report topic>
{topic}
</Report topic>

<Report organization>
{report_organization}
</Report organization>

<Task>
Your goal is to generate {number_of_queries} web search queries that will help gather information for planning the report sections. 

The queries should:

1. Be related to the Report topic
2. Help satisfy the requirements specified in the report organization

Make the queries specific enough to find high-quality, relevant sources while covering the breadth needed for the report structure.
</Task>
"""

report_planner_instructions = """I want a plan for a report that is concise and focused.

<Report topic>
The topic of the report is:
{topic}
</Report topic>

<Report organization>
The report should follow this organization: 
{report_organization}
</Report organization>

<Context>
Here is context to use to plan the sections of the report: 
{context}
</Context>

<Task>
Generate a list of sections for the report. Your plan should be tight and focused with NO overlapping sections or unnecessary filler. 

For example, a good report structure might look like:
1/ intro
2/ overview of topic A
3/ overview of topic B
4/ comparison between A and B
5/ conclusion

Each section should have the fields:

- Name - Name for this section of the report.
- Description - Brief overview of the main topics covered in this section.
- Research - Whether to perform web research for this section of the report.
- Content - The content of the section, which you will leave blank for now.

Integration guidelines:
- Include examples and implementation details within main topic sections, not as separate sections
- Ensure each section has a distinct purpose with no content overlap
- Combine related concepts rather than separating them

Before submitting, review your structure to ensure it has no redundant sections and follows a logical flow.
</Task>

<Feedback>
Here is feedback on the report structure from review (if any):
{feedback}
</Feedback>
"""

query_writer_instructions = """You are an expert technical writer crafting targeted web search queries that will gather comprehensive information for writing a technical report section.

<Report topic>
{topic}
</Report topic>

<Section topic>
{section_topic}
</Section topic>

<Task>
Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information above the section topic. 

The queries should:

1. Be related to the topic 
2. Examine different aspects of the topic

Make the queries specific enough to find high-quality, relevant sources.
</Task>
"""

section_writer_instructions = """You are an expert technical writer crafting one section of a technical report.

<Report topic>
{topic}
</Report topic>

<Section name>
{section_name}
</Section name>

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Source material>
{context}
</Source material>

<Guidelines for writing>
1. If the existing section content is not populated, write a new section from scratch.
2. If the existing section content is populated, write a new section that synthesizes the existing section content with the Source material.
</Guidelines for writing>

<Length and style>
- Strict 150-200 word limit
- No marketing language
- Technical focus
- Write in simple, clear language
- Start with your most important insight in **bold**
- Use short paragraphs (2-3 sentences max)
- Use ## for section title (Markdown format)
- Only use ONE structural element IF it helps clarify your point:
  * Either a focused table comparing 2-3 key items (using Markdown table syntax)
  * Or a short list (3-5 items) using proper Markdown list syntax:
    - Use `*` or `-` for unordered lists
    - Use `1.` for ordered lists
    - Ensure proper indentation and spacing
- End with ### Sources that references the below source material formatted as:
  * List each source with title, date, and URL
  * Format: `- Title : URL`
</Length and style>

<Quality checks>
- Exactly 150-200 words (excluding title and sources)
- Careful use of only ONE structural element (table or list) and only if it helps clarify your point
- One specific example / case study
- Starts with bold insight
- No preamble prior to creating the section content
- Sources cited at end
</Quality checks>
"""

section_grader_instructions = """Review a report section relative to the specified topic:

<Report topic>
{topic}
</Report topic>

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
Evaluate whether the section content adequately addresses the section topic.

If the section content does not adequately address the section topic, generate {number_of_follow_up_queries} follow-up search queries to gather missing information.
</task>

<format>
    grade: Literal["pass","fail"] = Field(
        description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="List of follow-up search queries.",
    )
</format>
"""

final_section_writer_instructions = """You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

<Report topic>
{topic}
</Report topic>

<Section name>
{section_name}
</Section name>

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 50-100 word limit
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 100-150 word limit
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports: 
    * Only use ONE structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
- Focus on your single most important point
</Task>

<Quality Checks>
- For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
- For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
- Markdown format
- Do not include word count or any preamble in your response
</Quality Checks>
"""

# Nodes
async def generate_report_plan(state: ReportState, config: RunnableConfig):
    """ Generate the report plan """

    # Inputs
    topic = state["topic"]
    feedback = state.get("feedback_on_report_plan", None)

    # Get configuration
    from app.graph.graph_builder import Configuration
    configurable = Configuration.from_dict(config.get("configurable", {}))
    report_structure = configurable.report_structure
    number_of_queries = configurable.number_of_queries
    search_api = get_config_value(configurable.search_api)
    search_api_config = configurable.search_api_config or {}
    params_to_pass = get_search_params(search_api, search_api_config)

    # Convert JSON object to string if necessary
    if isinstance(report_structure, dict):
        report_structure = str(report_structure)

    # Set writer model
    writer_provider = get_config_value(configurable.writer_provider)
    writer_model_name = get_config_value(configurable.writer_model)
    writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider) 
    structured_llm = writer_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions_query = report_planner_query_writer_instructions.format(
        topic=topic, 
        report_organization=report_structure, 
        number_of_queries=number_of_queries
    )

    # Generate queries  
    results = structured_llm.invoke([
        SystemMessage(content=system_instructions_query),
        HumanMessage(content="Generate search queries that will help with planning the sections of the report.")
    ])

    # Web search
    query_list = [query.search_query for query in results.queries]

    # Search the web with parameters
    if search_api == "tavily":
        search_results = await tavily_search_async(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    elif search_api == "exa":
        search_results = await exa_search(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    elif search_api == "arxiv":
        search_results = await arxiv_search_async(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    elif search_api == "pubmed":
        search_results = await pubmed_search_async(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    else:
        raise ValueError(f"Unsupported search API: {search_api}")

    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(
        topic=topic, 
        report_organization=report_structure, 
        context=source_str, 
        feedback=feedback
    )

    # Set the planner
    planner_provider = get_config_value(configurable.planner_provider)
    planner_model = get_config_value(configurable.planner_model)

    # Report planner instructions
    planner_message = """Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. 
                        Each section must have: name, description, research, and content fields."""

    # Run the planner
    if planner_model == "claude-3-7-sonnet-latest-thinking":

        # Allocate a thinking budget for claude-3-7-sonnet-latest as the planner model
        planner_llm = init_chat_model(model="claude-3-7-sonnet-latest", 
                                      model_provider=planner_provider, 
                                      max_tokens=20_000, 
                                      thinking={"type": "enabled", "budget_tokens": 16_000})
        
        # with_structured_output uses forced tool calling, which thinking mode with Claude 3.7 does not support
        # So, we use bind_tools without enforcing tool calling to generate the report sections
        report_sections = planner_llm.bind_tools([Sections]).invoke([
            SystemMessage(content=system_instructions_sections),
            HumanMessage(content=planner_message)
        ])
        tool_call = report_sections.tool_calls[0]['args']
        report_sections = Sections.model_validate(tool_call)

    else:

        # With other models, we can use with_structured_output
        planner_llm = init_chat_model(model=planner_model, model_provider=planner_provider)
        structured_llm = planner_llm.with_structured_output(Sections)
        report_sections = structured_llm.invoke([
            SystemMessage(content=system_instructions_sections),
            HumanMessage(content=planner_message)
        ])

    # Get sections
    sections = report_sections.sections

    return {"sections": sections}

def human_feedback_api(state: ReportState, config: RunnableConfig):
    """ Get feedback on the report plan - modified for API """

    # Get sections
    topic = state["topic"]
    sections = state['sections']
    sections_str = "\n\n".join(
        f"Section: {section.name}\n"
        f"Description: {section.description}\n"
        f"Research needed: {'Yes' if section.research else 'No'}\n"
        for section in sections
    )

    # Create feedback prompt for API
    feedback_prompt = f"""Please provide feedback on the following report plan. 

{sections_str}

Does the report plan meet your needs? Provide feedback to regenerate the report plan or approve to continue:"""
    
    # Return interrupt with feedback prompt and sections for API handling
    return interrupt({
        "feedback_prompt": feedback_prompt, 
        "sections": [
            {
                "name": section.name,
                "description": section.description,
                "research_needed": section.research
            }
            for section in sections
        ]
    })

def generate_queries(state: SectionState, config: RunnableConfig):
    """ Generate search queries for a report section """

    # Get state 
    topic = state["topic"]
    section = state["section"]

    # Get configuration
    from app.graph.graph_builder import Configuration
    configurable = Configuration.from_dict(config.get("configurable", {}))
    number_of_queries = configurable.number_of_queries

    # Generate queries 
    writer_provider = get_config_value(configurable.writer_provider)
    writer_model_name = get_config_value(configurable.writer_model)
    writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider) 
    structured_llm = writer_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions = query_writer_instructions.format(
        topic=topic, 
        section_topic=section.description, 
        number_of_queries=number_of_queries
    )

    # Generate queries  
    queries = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate search queries on the provided topic.")
    ])

    return {"search_queries": queries.queries}

async def search_web(state: SectionState, config: RunnableConfig):
    """ Search the web for each query, then return a list of raw sources and a formatted string of sources."""
    # Get state
    search_queries = state["search_queries"]

    # Get configuration
    from app.graph.graph_builder import Configuration
    configurable = Configuration.from_dict(config.get("configurable", {}))
    search_api = get_config_value(configurable.search_api)
    search_api_config = configurable.search_api_config or {}
    params_to_pass = get_search_params(search_api, search_api_config)

    # Web search
    query_list = [query.search_query for query in search_queries]

    # Search the web with parameters
    if search_api == "tavily":
        search_results = await tavily_search_async(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=True)
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=False)
    elif search_api == "exa":
        search_results = await exa_search(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    elif search_api == "arxiv":
        search_results = await arxiv_search_async(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    elif search_api == "pubmed":
        search_results = await pubmed_search_async(query_list, **params_to_pass)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    else:
        raise ValueError(f"Unsupported search API: {search_api}")

    return {"source_str": source_str, "search_iterations": state["search_iterations"] + 1}

def write_section(state: SectionState, config: RunnableConfig):
    """ Write a section of the report """

    # Get state 
    topic = state["topic"]
    section = state["section"]
    source_str = state["source_str"]

    # Get configuration
    from app.graph.graph_builder import Configuration
    configurable = Configuration.from_dict(config.get("configurable", {}))

    # Format system instructions
    system_instructions = section_writer_instructions.format(
        topic=topic, 
        section_name=section.name, 
        section_topic=section.description, 
        context=source_str, 
        section_content=section.content
    )

    # Generate section  
    writer_provider = get_config_value(configurable.writer_provider)
    writer_model_name = get_config_value(configurable.writer_model)
    writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider) 
    section_content = writer_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate a report section based on the provided sources.")
    ])
    
    # Write content to the section object  
    section.content = section_content.content

    # Grade prompt 
    section_grader_message = """Grade the report and consider follow-up questions for missing information.
                               If the grade is 'pass', return empty strings for all follow-up queries.
                               If the grade is 'fail', provide specific search queries to gather missing information."""
    
    section_grader_instructions_formatted = section_grader_instructions.format(
        topic=topic, 
        section_topic=section.description,
        section=section.content, 
        number_of_follow_up_queries=configurable.number_of_queries
    )

    # Use planner model for reflection
    planner_provider = get_config_value(configurable.planner_provider)
    planner_model = get_config_value(configurable.planner_model)

    # If the planner model is claude-3-7-sonnet-latest, we need to use bind_tools to use thinking when generating the feedback 
    if planner_model == "claude-3-7-sonnet-latest":
        # Allocate a thinking budget for claude-3-7-sonnet-latest as the planner model
        reflection_model = init_chat_model(model=planner_model, 
                                           model_provider=planner_provider, 
                                           max_tokens=20_000, 
                                           thinking={"type": "enabled", "budget_tokens": 16_000})
        
        # with_structured_output uses forced tool calling, which thinking mode with Claude 3.7 does not support
        # So, we use bind_tools without enforcing tool calling to generate the report sections
        reflection_result = reflection_model.bind_tools([Feedback]).invoke([
            SystemMessage(content=section_grader_instructions_formatted),
            HumanMessage(content=section_grader_message)
        ])
        tool_call = reflection_result.tool_calls[0]['args']
        feedback = Feedback.model_validate(tool_call)
    
    else:
        reflection_model = init_chat_model(model=planner_model, 
                                           model_provider=planner_provider).with_structured_output(Feedback)
        
        feedback = reflection_model.invoke([
            SystemMessage(content=section_grader_instructions_formatted),
            HumanMessage(content=section_grader_message)
        ])

    # If the section is passing or the max search depth is reached, publish the section to completed sections 
    if feedback.grade == "pass" or state["search_iterations"] >= configurable.max_search_depth:
        # Publish the section to completed sections 
        return Command(
            update={"completed_sections": [section]},
            goto="END"
        )
    # Update the existing section with new content and update search queries
    else:
        return Command(
            update={"search_queries": feedback.follow_up_queries, "section": section},
            goto="search_web"
        )

def write_final_sections(state: SectionState, config: RunnableConfig):
    """ Write final sections of the report, which do not require web search and use the completed sections as context """

    # Get configuration
    from app.graph.graph_builder import Configuration
    configurable = Configuration.from_dict(config.get("configurable", {}))

    # Get state 
    topic = state["topic"]
    section = state["section"]
    completed_report_sections = state["report_sections_from_research"]
    
    # Format system instructions
    system_instructions = final_section_writer_instructions.format(
        topic=topic, 
        section_name=section.name, 
        section_topic=section.description, 
        context=completed_report_sections
    )

    # Generate section  
    writer_provider = get_config_value(configurable.writer_provider)
    writer_model_name = get_config_value(configurable.writer_model)
    writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider) 
    section_content = writer_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate a report section based on the provided sources.")
    ])
    
    # Write content to section 
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}

def gather_completed_sections(state: ReportState):
    """ Gather completed sections from research and format them as context for writing the final sections """    

    # List of completed sections
    completed_sections = state["completed_sections"]

    # Format completed section to str to use as context for final sections
    completed_report_sections = format_sections(completed_sections)

    return {"report_sections_from_research": completed_report_sections}

def initiate_final_section_writing(state: ReportState):
    """ Write any final sections using the Send API to parallelize the process """    

    # Kick off section writing in parallel via Send() API for any sections that do not require research
    return [
        Send("write_final_sections", {
            "topic": state["topic"], 
            "section": s, 
            "report_sections_from_research": state["report_sections_from_research"]
        }) 
        for s in state["sections"] 
        if not s.research
    ]

def compile_final_report(state: ReportState):
    """ Compile the final report """    

    # Get sections
    sections = state["sections"]
    completed_sections = {s.name: s.content for s in state["completed_sections"]}

    # Update sections with completed content while maintaining original order
    for section in sections:
        section.content = completed_sections[section.name]

    # Compile final report
    all_sections = "\n\n".join([s.content for s in sections])

    return {"final_report": all_sections} 