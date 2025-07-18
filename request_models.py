# request and response models each agent implementation should have 
# Define the request model
from pydantic import BaseModel
from typing import Dict

class QueryRequest(BaseModel):
    query: str

# response should always be of type 
# {response: Dict}
# the dictionary should contain input and output 