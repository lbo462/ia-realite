import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Create a global model instance
llm = ChatOpenAI(
    model="llama7b",
    temperature=0.0
)
