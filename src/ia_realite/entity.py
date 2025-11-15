from uuid import uuid4
from langchain.agents import create_agent
from langchain.messages import AIMessage

from src.ia_realite.chat_model import llm
from src.ia_realite.chat_memory import ChatMemory

class Entity:
    def __init__(self, name, system_prompt: str, memory: ChatMemory):
        self._uuid = uuid4()
        self.name = name
        self.system_prompt = system_prompt
        self.memory = memory
        
    def _get_response_content(self, ai_response) -> str:
        # Case 1: ai_response is a dict with messages
        if isinstance(ai_response, dict) and "messages" in ai_response:
            messages = ai_response["messages"]
            # Find first AIMessage
            ai_message = next((m for m in messages if isinstance(m, AIMessage)), None)
            if ai_message and isinstance(ai_message.content, str):
                return ai_message.content

        # Case 2: fallback: convert anything else to string
        return str(ai_response)
    
    def _generate_message(self, prompt: str = "What's your name?") -> str:
        agent = create_agent(
            model=llm,
            system_prompt=self.system_prompt
        )
        
        ai_response = agent.invoke(
            {"messages": self.memory.messages + [{"role": "user", "content": prompt}]},
            {"configurable": {"thread_id": "1"}}
        )
        
        return self._get_response_content(ai_response)

    def talk(self, prompt: str = "It's your turn!"):
        """
        Sends a message to the shared conversation
        :return:
        """
        message = self._generate_message(prompt)
        self.memory.add_message(self.name, message)
