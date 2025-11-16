from uuid import uuid4
from collections.abc import Iterator

from langchain.agents import create_agent

from .chat_memory import ChatMemory
from .chat_model import llm, get_response_content
from .entity import Entity
from .utils import randint_exclude


class Room:
    """
    A room is an entity aggregator
    """

    def __init__(self, subject: str, preference: str = ""):
        self.uuid = uuid4()
        self.subject = subject
        self.preference = preference
        self.memory = ChatMemory(room_id=str(self.uuid))
        self.entities: list[Entity] = list()

    @property
    def system_prompt(self) -> str:
        return f"""ROOM RULES: 
- In this room, there are entities with different personalities. They talk to each other and try to give different point of view concerning the same CONVERSATION SUBJECT of discussion. You are one of them. When you are told: It's your turn, you will receive the current state of the conversation, and you can continue talking, giving your own point of view. Keep your answers short (4 sentences MAX) and relevant to the current topic of discussion. 
- PREFERENCE (if provided) guides your tone and style of communication. You should adapt your responses to align with this preference, ensuring that your contributions reflect the specified style or tone.
PREFERENCE:
{self.preference}
CONVERSATION SUBJECT: 
{self.subject}.
"""

    def add_entity(self, entity_name: str, entity_system_prompt: str):
        system_message = (
            f"{self.system_prompt}\n YOU ARE {entity_name}: {entity_system_prompt}"
        )
        self.entities.append(Entity(entity_name, system_message, self.memory))

    def generate_entity_summary(self):
        summary_system_prompt = f"""INSTRUCTION: 
Now that the conversation has ended, you have to generate a short, concise summary of each entity's point of view in the conversation. An entity is the one that has their name at the beginning of each paragraph, which is followed by a ":" (same name = same entity). You will also have the room rules and the whole conversation as context to understand better the context. DO NOT invent new information NOR return the whole conversation as it is.
ROOM RULES:
{self.system_prompt}
CONVERSATION:
{self.memory.messages}
"""
        agent = create_agent(model=llm, system_prompt=summary_system_prompt)

        ai_response = agent.invoke(
            {"messages": [{"role": "user", "content": "Generate summary"}]}
        )
        return get_response_content(ai_response)

    def sweat(self, amount_of_messages: int = 10) -> Iterator[str]:
        exposed_entity_index = 0
        for _ in range(0, amount_of_messages):
            exposed_entity_index = randint_exclude(
                0, len(self.entities) - 1, exposed_entity_index
            )
            exposed_entity = self.entities[exposed_entity_index]
            yield f"{exposed_entity.name} says: {exposed_entity.talk()}"

        # Then, send final signal to close conversation phase
        self.memory.add_message("system", "END OF CONVERSATION BETWEEN ENTITIES")

    def post_sweat_chat(self, entity_index: int, prompt: str) -> str:
        if entity_index not in range(0, len(self.entities)):
            raise ValueError("Invalid entity index")
        return self.entities[entity_index].talk(prompt=prompt)
