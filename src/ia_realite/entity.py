from uuid import uuid4
from langchain.agents import create_agent

from .chat_model import llm, get_response_content
from .chat_memory import ChatMemory
from .metrics_collector import measure_inference

class Entity:
    def __init__(self, name, system_prompt: str, memory: ChatMemory):
        self._uuid = uuid4()
        self.name = name
        self.system_prompt = system_prompt
        self.memory = memory

    def _generate_message(self, prompt: str = "What's your name?") -> str:
        agent = create_agent(model=llm, system_prompt=self.system_prompt)

        # construire callable d'invocation selon ton code existant
        def invoke():
            return agent.invoke({"messages": self.memory.messages + [{"role": "user", "content": prompt}]})

        ai_response, metrics = measure_inference(invoke)
        # pousse metrics dans la room centrale si accessible
        try:
            if hasattr(self, "room") and self.room is not None:
                self.room.push_metric(metrics)
        except Exception:
            pass

        # extraire texte depuis ai_response avec ta fonction existante
        return get_response_content(ai_response)

    def talk(self, prompt: str = "It's your turn!") -> str:
        """
        Sends a message to the shared conversation
        :return:
        """
        message = self._generate_message(prompt)
        self.memory.add_message(self.name, message)

        return message
