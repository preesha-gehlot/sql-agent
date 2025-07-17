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

async def create_agent_with_toolset(context):
    toolset_mapping = {
        'retail': 'retail-tools',
        'claims': 'claims_tools',
        'all': 'all_tools'
    }
    
    if context not in toolset_mapping:
        raise ValueError(f"Invalid context: {context}. Must be 'retail', 'claims', or 'all'")
    
    toolset_name = toolset_mapping[context]
    toolbox = ToolboxSyncClient("http://127.0.0.1:5000")

    toolset = toolbox.load_toolset(toolset_name)

    prompt = """
    You are an intelligent agent designed to interact with a SQL database. Your goal is to understand the user's question, generate an SQL query and YOU MUST execute it using the available tools, then summarise the results. 
    
    IMPORTANT WORKFLOW - Follow these steps in order:

    1. **DISCOVER AVAILABLE TABLES**: 
   - First, use the available table listing tools to see what tables exist in the relevant database
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
    - Return actual data results, not just SQL code
    
    QUERY GUIDELINES:
    - Always discover the schema first - never guess table or column names
    - Limit results to 10 unless explicitly asked for more
    - Use proper SQL syntax with correct table and column names
    - Focus only on columns relevant to the user's question
    - Choose the appropriate database based on the user's question context

    PROCESS FOR ANSWERING QUESTIONS:
    1. Determine which database(s) the question relates to (retail, claims, or both)
    2. Discover what tables are available in the relevant database(s)
    3. Get the schema for tables that seem relevant to the question
    4. Generate SQL using the exact names you discovered
    5. Execute the query using the appropriate database tools
    6. Summarize the results for the user

    If you cannot find relevant tables or if the question is unrelated to retail or claims data, respond with "I can only answer questions related to Claims or Retail data."

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
        context: Database context ('retail', 'claims', or 'all')
    """
    # Create agent with specific toolset
    agent, toolbox_client = await create_agent_with_toolset(context)
    
    try:
        # Create runner and session
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        runner = Runner(
            app_name="data_agent",
            agent=agent,
            artifact_service=artifact_service,
            session_service=session_service
        )
        
        # Run the agent
        session = await session_service.create_session(app_name='data_agent', user_id='123')
        content = types.Content(role='user', parts=[types.Part(text=question)])
        response_generator = runner.run_async(
            session_id=session.id,
            user_id='123',
            new_message=content
        )
        
        # Check if it's an async generator
        if hasattr(response_generator, '__aiter__'):
            # It's an async generator, collect all responses
            responses = []
            async for response_chunk in response_generator:
                responses.append(response_chunk)
                print(f"Response chunk: {response_chunk}")
            return responses
        else:
            # It's a regular awaitable
            response = await response_generator
            print(f"Full response: {response}")
            return response
    finally:
        # Clean up the toolbox client
        if hasattr(toolbox_client, 'close'):
            toolbox_client.close()
        elif hasattr(toolbox_client, 'cleanup'):
            toolbox_client.cleanup()


async def main():
    try: 
        # Test a simple question
        print("\nTesting with a claims question...")
        question = "Which approved claim was the most expensive? Give a report of who was involved, the policies and all relevant infomation related to the claim."
        response = await handle_question(question, context='all')
        print(f"\n=== FINAL RESPONSE ===")
        if isinstance(response, list):
            for i, chunk in enumerate(response):
                print(f"Chunk {i}: {chunk}")
        else:
            print(f"Response: {response}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
