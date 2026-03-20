import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from app.db.connectors import NeonPostgresConnector
from app.core.config import settings

# 1. Define the State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_question: str
    generated_sql: str
    query_results: str

# Initialize our components
db_connector = NeonPostgresConnector()

# We need an LLM. Since it's Gemini, we use ChatGoogleGenerativeAI.
# We'll use a reliable model for reasoning and coding (gemini-1.5-pro or flash)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0
)

# 2. Define the Nodes

def node_understand_and_write_sql(state: AgentState) -> AgentState:
    """
    Analyzes the user's question against the DB schema and writes a SQL query.
    """
    question = state["user_question"]
    schema = db_connector.get_schema()
    
    system_prompt = f"""
You are a highly capable AI assistant that answers questions based on a SQL database.
Given the following database schema, your job is to write a PostgreSQL SELECT query to answer the user's question.

SCHEMA:
{schema}

RULES:
1. Return ONLY the raw SQL query. Do not wrap it in ```sql ``` markdown blocks or include any other text.
2. The query must be a valid PostgreSQL SELECT statement.
3. If the question cannot be answered using the available schema, return the exact string: "CANNOT_ANSWER".
"""
    
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"]) + [HumanMessage(content=question)]
    response = llm.invoke(messages)
    
    sql_query = response.content.strip()
    
    # Strip markdown if the LLM ignored rule #1
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    sql_query = sql_query.strip()
        
    return {"generated_sql": sql_query}

def node_execute_sql(state: AgentState) -> AgentState:
    """
    Executes the generated SQL query against the database.
    """
    sql_query = state["generated_sql"]
    
    if sql_query == "CANNOT_ANSWER":
        return {"query_results": "I'm sorry, I don't have enough information in the database to answer that question."}
        
    results = db_connector.execute_query(sql_query)
    return {"query_results": results}

def node_generate_answer(state: AgentState) -> AgentState:
    """
    Takes the SQL query results and formulates a natural language answer.
    """
    question = state["user_question"]
    results = state["query_results"]
    sql_query = state["generated_sql"]
    
    if sql_query == "CANNOT_ANSWER":
        final_answer = results # which is the error message from execute node
    else:
        system_prompt = f"""
You are a helpful AI data assistant. 
The user asked: "{question}"

To answer this, I queried the database with: `{sql_query}`

Here are the results of that query:
{results}

Formulate a friendly, concise, and helpful natural language response to the user based ONLY on the provided results. Do not mention the SQL query itself unless relevant. Format neatly.
"""
        response = llm.invoke([SystemMessage(content=system_prompt)])
        final_answer = response.content

    # Because we use `add_messages`, we only need to return the new messages
    new_messages = [
        HumanMessage(content=question),
        AIMessage(content=final_answer)
    ]
    
    return {"messages": new_messages}

# 3. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("write_sql", node_understand_and_write_sql)
workflow.add_node("execute_sql", node_execute_sql)
workflow.add_node("generate_answer", node_generate_answer)

workflow.set_entry_point("write_sql")
workflow.add_edge("write_sql", "execute_sql")
workflow.add_edge("execute_sql", "generate_answer")
workflow.add_edge("generate_answer", END)

# Compile the graph
chatbot_agent = workflow.compile()

def ask_chatbot(question: str, history: list = None):
    """
    Helper function to invoke the graph from the API.
    """
    if history is None:
        history = []
        
    # Convert dict history to Langchain Messages
    lc_messages = []
    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
            
    inputs = {
        "user_question": question,
        "messages": lc_messages,
        "generated_sql": "",
        "query_results": ""
    }
    
    result = chatbot_agent.invoke(inputs)
    
    # The final message in 'messages' is the AI's latest response
    return result["messages"][-1].content
