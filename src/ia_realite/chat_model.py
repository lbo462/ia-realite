from langchain_openai import ChatOpenAI
from langchain.messages import AIMessage
from langchain_groq import ChatGroq
import re

# Create a global model instance
# llm = ChatOpenAI(
#     model="llama7b",
#     temperature=0.5,
#     base_url="http://localhost:8082/v1",
#     api_key="dummy",
# )

# Alternatively, if using Groq API
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2
)


def get_response_content(ai_response) -> str:
    # Case 1: ai_response is a dict with messages
    if isinstance(ai_response, dict) and "messages" in ai_response:
        messages = ai_response["messages"]
        # Find first AIMessage
        ai_message = next((m for m in messages if isinstance(m, AIMessage)), None)
        if ai_message and isinstance(ai_message.content, str):
            return re.sub(r"^\w+( )?:( )?", "", str(ai_message.content))

    # Case 2: fallback: convert anything else to string
    return re.sub(r"^\w+( )?:( )?", "", str(ai_response))



