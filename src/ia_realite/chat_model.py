import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.messages import AIMessage


load_dotenv()

# Create a global model instance
llm = ChatOpenAI(
    model="llama7b",
    temperature=0.5
)

def get_response_content(ai_response) -> str:
    # Case 1: ai_response is a dict with messages
    if isinstance(ai_response, dict) and "messages" in ai_response:
        messages = ai_response["messages"]
        # Find first AIMessage
        ai_message = next((m for m in messages if isinstance(m, AIMessage)), None)
        if ai_message and isinstance(ai_message.content, str):
            return ai_message.content
        
    # Case 2: fallback: convert anything else to string
    return str(ai_response)
