from uuid import uuid4
from langchain.agents import create_agent

from .chat_model import llm, get_response_content
from .chat_memory import ChatMemory


class Entity:
    def __init__(self, name, system_prompt: str, memory: ChatMemory):
        self._uuid = uuid4()
        self.name = name
        self.system_prompt = system_prompt
        self.memory = memory
    
    def _generate_message(self, prompt: str = "What's your name?") -> str:
        agent = create_agent(
            model=llm,
            system_prompt=self.system_prompt
        )
        
        ai_response = agent.invoke(
            {"messages": self.memory.messages + [{"role": "user", "content": prompt}]}
        )
        
        return get_response_content(ai_response)

    def talk(self, prompt: str = "It's your turn!"):
        """
        Sends a message to the shared conversation
        :return:
        """
        message = self._generate_message(prompt)
        self.memory.add_message(self.name, message)
