from fastapi import FastAPI, Query
from pydantic import BaseModel
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

# Set Ollama host to remote IP
os.environ["OLLAMA_BASE_URL"] = "http://34.142.79.93:11434"
os.environ["OPENAI_API_KEY"] = "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"

# Define database URIs
DATABASES = {
    "retail": "mysql+pymysql://retail-store:retail-store@35.246.67.116:3306/RetailStore",
    "claims": "mysql+pymysql://claims:claims@35.246.67.116:3306/claims"
}

def get_db_uri(db_name: str) -> str:
    if db_name not in DATABASES:
        raise ValueError(f"Unsupported database: {db_name}")
    return DATABASES[db_name]


def get_examples(db_name: str) -> list:
    claims_examples = [
        {
            "input": "Show me policyholders who have filed claims over $100.",
            "query": "SELECT ph.id, ph.full_name, c.claim_amount FROM policyholders ph JOIN policies p ON ph.id = p.policyholder_id JOIN claims c ON p.id = c.policy_id WHERE c.claim_amount > 100;"
        },
        {
            "input": "How many claims has each adjuster handled?",
            "query": "SELECT a.name, COUNT(c.id) AS total_claims FROM adjusters a LEFT JOIN claims c ON a.id = c.adjuster_id GROUP BY a.name;"
        },
        {
            "input": "List all Cyber Liability policies.",
            "query": "SELECT * FROM policies WHERE policy_type = 'Cyber Liability';"
        },
        {
            "input": "Show all claims that are under review.",
            "query": "SELECT c.id, c.claim_amount, cs.status, cs.updated_at FROM claims c JOIN claim_status cs ON c.id = cs.claim_id WHERE cs.status = 'Under Review';"
        },
        {
            "input": "List all claims for Alice Johnson.",
            "query": "SELECT c.id, c.claim_date, c.claim_amount, c.description FROM policyholders ph JOIN policies p ON ph.id = p.policyholder_id JOIN claims c ON p.id = c.policy_id WHERE ph.full_name = 'Alice Johnson';"
        }
    ]
    retail_examples = [
    {
        "input": "What are the names and emails of all customers?",
        "query": "SELECT FirstName, LastName, Email FROM Customers;"
    },
    {
        "input": "List all products in the 'Electronics' category and their prices.",
        "query": "SELECT ProductName, Price FROM Products WHERE Category = 'Electronics';"
    },
    {
        "input": "Show the details (product name, quantity, price) of items in order ID 1.",
        "query": "SELECT p.ProductName, od.Quantity, od.Price FROM OrderDetails od JOIN Products p ON od.ProductID = p.ProductID WHERE od.OrderID = 1;"
    },
    {
        "input": "Find the total number of orders placed by each customer.",
        "query": "SELECT c.FirstName, c.LastName, COUNT(o.OrderID) AS TotalOrders FROM Customers c LEFT JOIN Orders o ON c.CustomerID = o.CustomerID GROUP BY c.CustomerID, c.FirstName, c.LastName;"
    },
    {
        "input": "What is the total revenue from all orders?",
        "query": "SELECT SUM(TotalAmount) AS TotalRevenue FROM Orders;"
    },
    {
        "input": "Which product has the highest stock quantity?",
        "query": "SELECT ProductName, StockQuantity FROM Products ORDER BY StockQuantity DESC LIMIT 1;"
    },
    {
        "input": "Show the orders placed in April 2024.",
        "query": "SELECT OrderID, CustomerID, OrderDate, TotalAmount, Status FROM Orders WHERE OrderDate BETWEEN '2024-04-01' AND '2024-04-30';"
    },
    {
        "input": "List customers who live in 'New York'.",
        "query": "SELECT FirstName, LastName FROM Customers WHERE City = 'New York';"
    },
    {
        "input": "What is the average price of products in the 'Home Appliances' category?",
        "query": "SELECT AVG(Price) AS AveragePrice FROM Products WHERE Category = 'Home Appliances';"
    },
    {
        "input": "Show the payment method used for each order.",
        "query": "SELECT o.OrderID, p.PaymentMethod FROM Orders o JOIN Payments p ON o.OrderID = p.OrderID;"
    }
    ]

    if db_name == 'claims':
        return claims_examples
    elif db_name == 'retail':
        return retail_examples
    else:
        raise ValueError(f"Unsupported database: {db_name}")

# Create the API
app = FastAPI()

# Define the request model
class QuestionRequest(BaseModel):
    question: str

# context is just a string that contains either 'retail or claims'
@app.post("/agent/ask")
async def ask_question(request: QuestionRequest, context: str = Query(...)):
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

    system_prefix = """You are an intelligent agent designed to interact with a SQL database. Your goal is to understand the user's question and generate a syntactically correct MySQL query to retrieve the relevant information.

Even if the user's question is not directly covered by the examples provided, you should use your understanding of the database schema, the English language, and the principles of SQL to formulate an appropriate SQLquery.

Consider the available tables and their columns to determine what information is needed to answer the question. Only query for the specific columns that are relevant to the user's request. Limit your queries to at most 10 results unless explicitly asked for more.

If you are unsure how to answer the question based on the database schema or if the question is completely unrelated, truthfully respond with "I can only answer anything related to Claims or Retail".

Here are some examples of user inputs and their corresponding SQL queries to guide your understanding:"""

    # takes the top similar examples and converts them into prompts by using 
    # the input and the query fields in the example to create few shot prompts 
    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template(
            "User input: {input}\nSQL query: {query}"
        ),
        input_variables=["input", "dialect", "top_k"],
        prefix=system_prefix,
        suffix="",
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

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    agent_executor = create_sql_agent(llm=llm, db=db, prompt=prompt, agent_type="openai-tools", verbose=True, handle_parsing_errors=True, max_iterations=10)

    response = await agent_executor.ainvoke({"input": request.question})
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)