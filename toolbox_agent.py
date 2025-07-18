from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types
from toolbox_core import ToolboxSyncClient

import os
# TODO(developer): replace this with your Google API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyBaAbvY7Ybo_-mA20xrMhrncLXPHqlZpl4"
os.environ["OPENAI_API_KEY"] = "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"  # For OpenAI models

# Define model constants for cleaner code
MODEL_GEMINI_PRO = "gemini-2.5-pro"
MODEL_GPT_4O = "openai/gpt-4o"

app = FastAPI()

# Initialize services
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

class QueryRequest(BaseModel):
    question: str
    context: Optional[str] = "all"

async def create_agent_with_toolset(context):
    toolset_mapping = {
        'northwind': 'northwind_db_tools'
    }
    
    if context not in toolset_mapping:
        raise ValueError(f"Invalid context: {context}. Must be 'northwind'")
    
    toolset_name = toolset_mapping[context]
    toolbox = ToolboxSyncClient("http://127.0.0.1:5000")

    toolset = toolbox.load_toolset(toolset_name)

    prompt = """
    You are an intelligent agent designed to interact with the SQL northwind database. Your goal is to understand the user's question, generate an SQL query and YOU MUST execute it using the available tools, then summarise the results. 
    
    IMPORTANT WORKFLOW - Follow these steps in order:

    1. **DISCOVER AVAILABLE TABLES**: 
   - First, use the available table listing tools to see what tables exist in the northwind database
   - This will show you the actual table names (never guess table names)

    2. **UNDERSTAND TABLE STRUCTURE**: 
    - Use the schema discovery tools to get the structure for relevant tables
    - This shows you the exact column names, data types, and constraints
    - Check multiple tables if needed to understand relationships between them

    3. **GENERATE CORRECT SQL**: 
    - Write SQL queries using the EXACT table names and column names you discovered
    - Use correct SQL syntax to form correct queries
    - Only query for columns that are relevant to the user's request

    4. **EXECUTE THE QUERY**: 
    - Use the appropriate database tools to execute your queries
    - Return actual data results summarised for the user, not just SQL code
    
    QUERY GUIDELINES:
    - Always discover the schema first - never guess table or column names
    - Limit results to 10 unless explicitly asked for more (e.g. when the user uses all or every)
    - Use proper SQL syntax with correct table and column names
    - Focus only on columns relevant to the user's question

    CRITICAL: When displaying numerical values from database results:
    - Display the EXACT number returned by the database tool
    - Do NOT add any zeros, commas, or formatting
    - Do NOT convert between cents and dollars
    - Double-check your SQL results before presenting them to the user

    If you cannot find relevant tables or if the question is unrelated to northwind data, respond with "I can only answer questions related to Northwind data."

    Remember: The tools available to you will help you discover table names, get table schemas, and execute queries. Use them systematically to ensure accurate results.
    """

    agent = Agent(
        model=LiteLlm(model=MODEL_GPT_4O),
        name='sql_agent',
        description='AI assistant for transforming natural language queries to sql and executing them on databases',
        instruction=prompt,
        tools=toolset,
    )
    return agent, toolbox

async def handle_question(question: str, context: str = 'all'):
    """
    Handle a user question with the specified database context.
    
    Args:
        question: User's question
        context: Database context ('northwind')
    """
    # Create agent with specific toolset
    agent, toolbox_client = await create_agent_with_toolset(context)
    
    try:
        runner = Runner(
            app_name="data_agent",
            agent=agent,
            artifact_service=artifact_service,
            session_service=session_service
        )
        
        session = await session_service.create_session(app_name='data_agent', user_id='123')
        content = types.Content(role='user', parts=[types.Part(text=question)])
        response_generator = runner.run_async(
            session_id=session.id,
            user_id='123',
            new_message=content
        )
        
        # Process events and extract final response
        response_text = "No response received."
        
        if hasattr(response_generator, '__aiter__'):
            async for event in response_generator:
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break
        else:
            # Handle non-async generator case
            events = await response_generator
            for event in events:
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break
        
        return response_text
        
    finally:
        if hasattr(toolbox_client, 'close'):
            toolbox_client.close()

@app.post("/query")
async def query_database(request: QueryRequest):
    try:
        response_text = await handle_question(request.question, request.context)
        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)