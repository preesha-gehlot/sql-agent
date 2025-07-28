from fastapi import FastAPI, Query
from request_models import QueryRequest
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
import uvicorn
import os

# Set Ollama host to remote IP

# Define database URIs
DATABASES = {
    "northwind": "mysql+pymysql://northwind_user:northwind_password@localhost:3306/Northwind",
}

def get_db_uri(db_name: str) -> str:
    if db_name not in DATABASES:
        raise ValueError(f"Unsupported context: {db_name}")
    return DATABASES[db_name]

# Create the API
app = FastAPI()

@app.post("/agent/ask")
async def ask_question(request: QueryRequest, context: str = Query(...)):
    db_uri = get_db_uri(context)
    db = SQLDatabase.from_uri(db_uri)

    # llm = OllamaLLM(model="gemma3:latest", temperature=0, streaming=False)
    llm = ChatOpenAI(model_name="gpt-4o")
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-functions",
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )

    response = await agent_executor.ainvoke(request.query)
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)