from fastapi import FastAPI, Query
from request_models import QueryRequest
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import OpenAIEmbeddings
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Define database URIs
DATABASES = {
    "northwind": "mysql+pymysql://northwind_user:northwind_password@localhost:3306/Northwind",
}

def get_db_uri(db_name: str) -> str:
    if db_name not in DATABASES:
        raise ValueError(f"Unsupported database: {db_name}")
    return DATABASES[db_name]


def get_examples(db_name: str) -> list:
    northwind_examples = [
        {
            "input": "What are the names and emails of all customers?",
            "query": "SELECT contactName, email FROM Customer;"
        },
        {
            "input": "Show me all product names and their prices",
            "query": "SELECT productName, unitPrice FROM Product;"
        },
        {
            "input": "List all employees' first and last names",
            "query": "SELECT firstname, lastname FROM Employee;"
        },
        {
            "input": "What are the company names of all suppliers?",
            "query": "SELECT companyName FROM Supplier;"
        },
        {
            "input": "Show me all category names and descriptions",
            "query": "SELECT categoryName, description FROM Category;"
        },
        {
            "input": "Find all customers from the USA",
            "query": "SELECT * FROM Customer WHERE country = 'USA';"
        },
        {
            "input": "Get all products that cost more than 20",
            "query": "SELECT * FROM Product WHERE unitPrice > 20;"
        },
        {
            "input": "Show me all orders placed in 2006",
            "query": "SELECT * FROM SalesOrder WHERE YEAR(orderDate) = 2006;"
        },
        {
            "input": "List all discontinued products",
            "query": "SELECT * FROM Product WHERE discontinued = '1';"
        },
        {
            "input": "Find employees hired after 2020",
            "query": "SELECT * FROM Employee WHERE hireDate > '2020-01-01';"
        },
        {
            "input": "How many customers do we have?",
            "query": "SELECT COUNT(*) FROM Customer;"
        },
        {
            "input": "What is the average product price?",
            "query": "SELECT AVG(unitPrice) FROM Product;"
        },
        {
            "input": "Show me the total number of orders",
            "query": "SELECT COUNT(*) FROM SalesOrder;"
        },
        {
            "input": "Get all products with their category names",
            "query": "SELECT p.productName, c.categoryName FROM Product p JOIN Category c ON p.categoryId = c.categoryId;"
        },
        {
            "input": "List all orders with customer company names",
            "query": "SELECT o.orderId, c.companyName FROM SalesOrder o JOIN Customer c ON o.custId = c.custId;"
        },
        {
            "input": "Show products and their supplier company names",
            "query": "SELECT p.productName, s.companyName FROM Product p JOIN Supplier s ON p.supplierId = s.supplierId;"
        },
        {
            "input": "Find all customers in London",
            "query": "SELECT * FROM Customer WHERE city = 'London';"
        },
        {
            "input": "Get the most expensive product",
            "query": "SELECT * FROM Product ORDER BY unitPrice DESC LIMIT 1;"
        },
        {
            "input": "Show me all shipper company names",
            "query": "SELECT companyName FROM Shipper;"
        },
        {
            "input": "List all regions and their descriptions",
            "query": "SELECT regionId, regiondescription FROM Region;"
        }
    ]

    if db_name == 'northwind':
        return northwind_examples
    else:
        raise ValueError(f"Unsupported database: {db_name}")

# Create the API
app = FastAPI()

# context is just a string that contains either 'retail or claims'
@app.post("/agent/ask")
async def ask_question(request: QueryRequest, context: str = Query(...)):
    db_uri = get_db_uri(context)
    db = SQLDatabase.from_uri(db_uri)

    examples = get_examples(context)

    # each embedding gets converted into an embedding vector using OpenAIs model
    # and stored in a FAISS index. FAISS searches for top 5 most similar embeddings
    # and returns corresponding examples. input keys ells selector which field from 
    # examples to choose from. 
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=5,
        input_keys=["input"],
    )

    system_prefix = """You are a MySQL database agent. You MUST follow this exact process:

        STEP 1: Find all the available tables in the database
        STEP 2: Find the schema for ALL potentially relevant tables to see exact column names  
        STEP 3: Write your data query using the verified column names
        STEP 4: Execute the query and return the results

        DO NOT attempt any SELECT queries until you have completed steps 1 and 2.

        Rules:
        - NEVER GUESS table or column names
        - Limit results to 10 unless asked for more (i.e. asked to ignore the 10 result limit)
        - Use proper MySQL syntax
        - If question is unrelated to database, respond: "I can only answer anything related to the Northwind Database"

        Here are some examples of data queries (step 3) on this database:"""

    # takes the top similar examples and converts them into prompts by using 
    # the input and the query fields in the example to create few shot prompts 
    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template(
            "User input: {input}\nSQL query: {query}"
        ),
        input_variables=["input", "dialect", "top_k"],
        prefix=system_prefix,
        suffix="Now, remember to follow the mandatory process (STEP 1-3) and answer the following question:",
    )

    # SystemMessagePromptTemplate sets up system instructions for the agent, 
    # MessagesPlaceholder allows agent to keep track of own reasoning steps 
    # actual user question, filled in at runtime with user's input 
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=few_shot_prompt.partial(dialect="MySQL", top_k=10)),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "{input}"),
        ]
    )

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    agent_executor = create_sql_agent(llm=llm, db=db, prompt=prompt, agent_type="openai-tools", verbose=True, handle_parsing_errors=True, max_iterations=10)

    response = await agent_executor.ainvoke({"input": request.query})
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)