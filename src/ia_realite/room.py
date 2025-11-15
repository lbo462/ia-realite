from random import randint

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


from .entity import Entity


class Room:
    """
    A room is an entity aggregator
    """

    def __init__(self):
        self._entities = list()

    @property
    def room_system_prompt(self) -> str:
        return f"""Their are {len(self._entities)} entities living in this room, that are talking to each others. You are one of them."""

    def _create_agent(self, agent_system_prompt: str):
        system_prompt = f"{self.room_system_prompt}\n{agent_system_prompt}"
        return create_agent(
            model="", checkpointer=InMemorySaver(), system_prompt=system_prompt
        )

    def add_entity(self, system_prompt: str):
        self._entities.append(
            Entity(
                agent=self._create_agent(agent_system_prompt=system_prompt),
            )
        )

    def sweat(self, amount_of_messages: int = 10):
        for _ in range(0, amount_of_messages):
            exposed_entity = self._entities[randint(0, len(self._entities) - 1)]
            exposed_entity.talk()
