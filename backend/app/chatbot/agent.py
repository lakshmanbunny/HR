import os
import re
import json
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from app.db.connectors import ProductionSqlConnector
from app.core.config import settings

# 1. Define the State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_question: str
    generated_sql: str
    query_results: str
    intent: str  # Added intent for better routing
    query_metadata: dict # Store extracted job_id, target_hires, etc.
    sourcing_metadata: dict # Store location, experience, etc. for sourcing

# Initialize our components
db_connector = ProductionSqlConnector()

# We need an LLM. Since it's Gemini, we use ChatGoogleGenerativeAI.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", # Using Flash for speed/reliability in intent detection
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0
)

# 2. Define the Nodes

def node_understand_and_write_sql(state: AgentState) -> AgentState:
    """
    Analyzes the user's question and identifies the INTENT: SQL_QUERY, SQL_AUDIT, RECRUITMENT_FORECAST, RECRUITMENT_SOURCE, or CANNOT_ANSWER.
    """
    import re
    import json
    question = state["user_question"]
    schema = db_connector.get_schema()
    
    # Fetch available jobs for better matching in RECRUITMENT_FORECAST and RECRUITMENT_SOURCE
    from app.db import repository
    from app.db.database import SessionLocal
    db_session = SessionLocal()
    try:
        jobs = repository.get_jobs(db_session)
        job_list_str = "\n".join([f"- ID: {j['id']}, Title: {j['title']}" for j in jobs])
    finally:
        db_session.close()

    system_prompt = f"""
You are a highly capable AI assistant that answers questions based on a SQL database and recruitment funnel performance.
Your first task is to identify the USER'S INTENT.

INTENT OPTIONS:
1. SQL_QUERY: The user wants data from the main database (jobs, candidates, placements, stats).
2. SQL_AUDIT: The user wants to know about the SQL recruitment pipeline, technical failures, candidate test performance, or weaknesses in SQL tests.
3. RECRUITMENT_FORECAST: The user wants to know about sourcing targets or hiring timelines (e.g., "How many to source?", "How long to fill?").
4. RECRUITMENT_SOURCE: The user wants help in SOURCING candidates from LinkedIn or Naukri for a job order.
   - Example: "Can you help me source candidates for this role?", "Find me candidates for .NET Medidata", "Source from LinkedIn/Naukri".
   - If user provides parameters like location (e.g., "in Bangalore") or experience (e.g., "5+ years"), extract them.
5. CANNOT_ANSWER: The question is unrelated or cannot be answered with the available data.

DATABASE SCHEMA (for SQL_QUERY):
{schema}

AVAILABLE JOB ORDERS (for RECRUITMENT_FORECAST and RECRUITMENT_SOURCE):
{job_list_str}

--- SEARCH RULES (CRITICAL) ---
1. For NAME SEARCHES (e.g., "find lakshman", "search for sai"):
   - ALWAYS use `LIKE` with wildcards (`%`). 
   - Use `CONCAT(first_name, ' ', last_name) LIKE '%term%'` to handle multi-word names or first-last name variations.

--- OUTPUT FORMAT (STRICT) ---
Return your response ONLY in this structured format:
INTENT: [SQL_QUERY | SQL_AUDIT | RECRUITMENT_FORECAST | RECRUITMENT_SOURCE | CANNOT_ANSWER]
SQL: [Your SQL query here if intent is SQL_QUERY, otherwise leave blank]
METADATA: [JSON with job_id and target_hires if intent is RECRUITMENT_FORECAST/RECRUITMENT_SOURCE. 
           If intent is RECRUITMENT_SOURCE, also include "location" and "experience" if found.
           e.g. {{"job_id": 123, "target": 158, "location": "Bangalore", "experience": "5+ years"}}]

STRICT RULE: Do NOT include ANY conversational text in the SQL: field.
"""
    
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"]) + [HumanMessage(content=question)]
    
    response = llm.invoke(messages)
    content = response.content.strip()
    
    intent = "CANNOT_ANSWER"
    sql_query = ""
    query_metadata = {}
    
    if "INTENT: RECRUITMENT_SOURCE" in content:
        intent = "RECRUITMENT_SOURCE"
        meta_match = re.search(r'METADATA:\s*(\{.*\})', content, re.DOTALL | re.IGNORECASE)
        if meta_match:
            try:
                query_metadata = json.loads(meta_match.group(1))
            except:
                pass
    elif "INTENT: RECRUITMENT_FORECAST" in content:
        intent = "RECRUITMENT_FORECAST"
        meta_match = re.search(r'METADATA:\s*(\{.*\})', content, re.DOTALL | re.IGNORECASE)
        if meta_match:
            try:
                query_metadata = json.loads(meta_match.group(1))
            except:
                pass
    elif "INTENT: SQL_AUDIT" in content:
        intent = "SQL_AUDIT"
    elif "INTENT: SQL_QUERY" in content:
        intent = "SQL_QUERY"
        code_block_match = re.search(r'SQL:\s*```(?:sql|mysql)?\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            sql_query = code_block_match.group(1).strip()
        else:
            sql_match = re.search(r'SQL:\s*(SELECT.*?;)', content, re.DOTALL | re.IGNORECASE)
            if not sql_match:
                sql_match = re.search(r'SQL:\s*(SELECT.*)', content, re.IGNORECASE)
            if sql_match:
                sql_query = sql_match.group(1).strip()
                if ";" in sql_query:
                    sql_query = sql_query.split(";")[0] + ";"
    
    # Merge existing sourcing metadata if it's a follow-up
    current_sourcing_meta = state.get("sourcing_metadata", {})
    if intent == "RECRUITMENT_SOURCE":
        new_meta = {
            "job_id": query_metadata.get("job_id") or current_sourcing_meta.get("job_id"),
            "target": query_metadata.get("target") or current_sourcing_meta.get("target") or 10,
            "location": query_metadata.get("location") or current_sourcing_meta.get("location"),
            "experience": query_metadata.get("experience") or current_sourcing_meta.get("experience")
        }
    else:
        new_meta = current_sourcing_meta

    return {"generated_sql": sql_query, "intent": intent, "query_metadata": query_metadata, "sourcing_metadata": new_meta}

def node_fetch_audit_data(state: AgentState) -> AgentState:
    """Fetches candidate test results from Neon DB."""
    from app.db import repository
    import json
    audit_results = repository.get_sql_test_results()
    return {"query_results": json.dumps(audit_results, indent=2) if audit_results else "No audit data found."}

def node_fetch_funnel_stats(state: AgentState) -> AgentState:
    """Fetches historical funnel stats AND time metrics when intent is RECRUITMENT_FORECAST."""
    from app.db import repository
    from app.db.database import SessionLocal
    import json
    
    db_session = SessionLocal()
    meta = state.get("query_metadata", {})
    job_id = meta.get("job_id")
    
    try:
        # Fetch Overall funnel stats (all history)
        overall_stats = repository.get_funnel_stats(db_session, days=10000)
        
        specific_stats = []
        if job_id:
            specific_stats = repository.get_funnel_stats(db_session, days=10000, job_id=job_id)
        
        # Fetch time metrics (job-specific + overall)
        overall_time = repository.get_job_time_metrics(db_session)
        specific_time = repository.get_job_time_metrics(db_session, job_id=job_id) if job_id else {}
            
        data = {
            "overall_funnel": overall_stats,
            "specific_funnel": specific_stats,
            "overall_time_metrics": overall_time,
            "specific_time_metrics": specific_time,
            "target": meta.get("target", 1)
        }
        return {"query_results": json.dumps(data, indent=2)}
    finally:
        db_session.close()

def node_refine_sourcing(state: AgentState) -> AgentState:
    """Checks if we have enough info to source. If not, asks clarifying questions."""
    meta = state.get("sourcing_metadata", {})
    missing = []
    if not meta.get("location"): missing.append("Location (e.g., Bangalore, Remote)")
    if not meta.get("experience"): missing.append("Experience Level (e.g., 5+ years, Lead)")
    
    if missing:
        msg = f"I'm ready to help you source candidates! However, to generate the most effective X-Ray search, could you please provide: {', '.join(missing)}?"
        return {"query_results": "WAITING_FOR_Sourcing_PARAMS", "messages": [AIMessage(content=msg)]}
    
    return {"query_results": "PARAMS_COMPLETE"}

def node_perform_sourcing(state: AgentState) -> AgentState:
    """Generates X-Ray strings and calls the Google Search service."""
    from app.services import sourcing_service
    from app.db import repository
    from app.db.database import SessionLocal
    
    meta = state.get("sourcing_metadata", {})
    job_id = meta.get("job_id")
    
    # Get Job Title for context
    job_title = "Developer"
    if job_id:
        db_session = SessionLocal()
        try:
            # Safely fetch jobs, handling missing table or permission issues
            jobs = repository.get_jobs(db_session)
            job = next((j for j in jobs if str(j.get('id')) == str(job_id)), None)
            if job: 
                job_title = job.get('title') or job.get('name') or job_title
        except Exception as e:
            print(f"Warning: Could not fetch job context from database: {e}")
        finally:
            db_session.close()

    # 1. Generate Expert Recruiter X-Ray Strings
    prompt = f"""
    You are a 20-year veteran recruitment expert. Generate TWO highly effective X-Ray search strings for Google:
    Role: {job_title}
    Location: {meta.get('location')}
    Experience: {meta.get('experience')}
    
    Sites to cover: linkedin.com/in, naukri.com
    
    Return ONLY the search strings, one per line.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    queries = response.content.strip().split("\n")
    
    # 2. Call Sourcing Service
    all_results = []
    # Default to 5 candidates for demo as requested
    target_count = int(meta.get("target", 5))
    if target_count > 5: target_count = 5 # Force limit for demo
    
    for q in queries:
        if len(all_results) >= target_count: break
        results = sourcing_service.perform_search(q, target_count)
        all_results.extend(results)
    
    return {"query_results": json.dumps(all_results[:target_count], indent=2)}

def node_execute_sql(state: AgentState) -> AgentState:
    """Executes the generated SQL query."""
    sql_query = state["generated_sql"]
    if not sql_query or state["intent"] == "CANNOT_ANSWER":
        return {"query_results": "I'm sorry, I don't have enough information."}
    results = db_connector.execute_query(sql_query)
    return {"query_results": results}

def node_generate_answer(state: AgentState) -> AgentState:
    """Formulates a natural language answer based on intent and results."""
    question = state["user_question"]
    results = state["query_results"]
    intent = state["intent"]
    
    if results == "WAITING_FOR_Sourcing_PARAMS":
        # The node_refine_sourcing already added a message
        return {}

    if intent == "RECRUITMENT_SOURCE":
        try:
            candidates = json.loads(results)
            count = len(candidates)
            meta = state.get("sourcing_metadata", {})
            msg = f"I've successfully sourced {count} potential profiles for the role in **{meta.get('location')}** with **{meta.get('experience')}** experience.\n\nI used professional X-Ray strings targeting LinkedIn and Naukri to find the best matches."
            # The frontend will check for intent: RECRUITMENT_SOURCE and query_results to show the button
            return {"messages": [AIMessage(content=msg)]}
        except:
            return {"messages": [AIMessage(content="I encountered an issue while sourcing candidates. Please try again later.")]}

    if intent == "RECRUITMENT_FORECAST":
        system_prompt = f"""
You are a senior recruitment analytics advisor.
The user wants a forecast/recommendation: "{question}"

I have retrieved the following data:
{results}

The data includes:
- **Funnel conversion data** (overall_funnel & specific_funnel): Submissions -> Pre-screening -> Written -> L1/L2/L3 -> Offered -> Joined
- **Time metrics** (overall_time_metrics & specific_time_metrics): avg days to screening, interview, offer, and fill/placement

Logic for your answer:
1. If the user asks about SOURCING VOLUME (how many to source):
   - Use (Joined / Submissions) conversion rate. Prefer specific data if available.
   - Formula: Required Submissions = Target Hires / Conversion Rate.
2. If the user asks about TIME/DURATION (how long will it take):
   - Use the time metrics. Prefer job-specific times if available.
   - Present avg_time_to_offer_days and avg_time_to_fill_days clearly.
   - Break down each stage velocity if available.
3. If both are asked, provide both.
4. Be professional. Mention the data source (job-specific vs overall benchmark).
5. Format the recommendation clearly with numbers and stage breakdowns.
"""
        response = llm.invoke([HumanMessage(content=system_prompt)])
        final_answer = response.content
    elif intent == "SQL_AUDIT":
        system_prompt = f"""
You are a helpful AI recruitment data assistant. 
The user asked about candidate technical performance: "{question}"
DATA:
{results[:8000]}
Formulate a data-driven response (analyzing all 18 candidates) based on technical audits.
"""
        response = llm.invoke([HumanMessage(content=system_prompt)])
        final_answer = response.content
    else:
        system_prompt = f"""
You are a helpful AI HR data assistant. User asked: "{question}"
DB RESULTS: {results}
Formulate a friendly, concise, and helpful response.
"""
        response = llm.invoke([HumanMessage(content=system_prompt)])
        final_answer = response.content

    return {"messages": [HumanMessage(content=question), AIMessage(content=final_answer)]}

# Routing logic
def should_route(state: AgentState):
    intent = state.get("intent", "CANNOT_ANSWER")
    if intent == "SQL_QUERY": return "execute"
    if intent == "SQL_AUDIT": return "audit"
    if intent == "RECRUITMENT_FORECAST": return "forecast"
    if intent == "RECRUITMENT_SOURCE": return "source"
    return "skip"

def source_route(state: AgentState):
    if state.get("query_results") == "WAITING_FOR_Sourcing_PARAMS":
        return END
    return "perform"

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("understand", node_understand_and_write_sql)
workflow.add_node("execute_sql", node_execute_sql)
workflow.add_node("fetch_audit", node_fetch_audit_data)
workflow.add_node("fetch_funnel", node_fetch_funnel_stats)
workflow.add_node("refine_sourcing", node_refine_sourcing)
workflow.add_node("perform_sourcing", node_perform_sourcing)
workflow.add_node("generate_answer", node_generate_answer)

workflow.set_entry_point("understand")
workflow.add_conditional_edges("understand", should_route, {
    "execute": "execute_sql",
    "audit": "fetch_audit",
    "forecast": "fetch_funnel",
    "source": "refine_sourcing",
    "skip": "generate_answer"
})

workflow.add_conditional_edges("refine_sourcing", source_route, {
    "perform": "perform_sourcing",
    END: END
})

workflow.add_edge("execute_sql", "generate_answer")
workflow.add_edge("fetch_audit", "generate_answer")
workflow.add_edge("fetch_funnel", "generate_answer")
workflow.add_edge("perform_sourcing", "generate_answer")
workflow.add_edge("generate_answer", END)

chatbot_agent = workflow.compile()

def ask_chatbot(question: str, history: list = None, sourcing_context: dict = None):
    if history is None: history = []
    if sourcing_context is None: sourcing_context = {}
    
    lc_messages = []
    for msg in history:
        if msg["role"] == "user": lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant": lc_messages.append(AIMessage(content=msg["content"]))
            
    inputs = {
        "user_question": question, 
        "messages": lc_messages, 
        "generated_sql": "", 
        "query_results": "", 
        "intent": "", 
        "query_metadata": {},
        "sourcing_metadata": sourcing_context
    }
    result = chatbot_agent.invoke(inputs)
    return {
        "reply": result["messages"][-1].content,
        "source_data": result.get("query_results", ""),
        "generated_sql": result.get("generated_sql", ""),
        "intent": result.get("intent", ""),
        "sourcing_metadata": result.get("sourcing_metadata", {})
    }
