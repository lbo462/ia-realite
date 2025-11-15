from random import randint
from uuid import uuid4

from .chat_memory import ChatMemory

from .entity import Entity


class Room:
    """
    A room is an entity aggregator
    """

    def __init__(self, subject: str):
        self.uuid = uuid4()
        self.room_system_prompt = self._build_room_system_prompt(subject)
        self.memory = ChatMemory(room_id=str(self.uuid))
        self._entities = list()
        
    def _build_room_system_prompt(self, subject: str) -> str:
        return f"ROOM RULES: /n In this room, there are entites with different personalities. They talk to each other and try to give different point of view concerning the same CONVERSATION SUBJECT of discussion. You are one of them. When you are told: It's your turn, you will receive the current state of the conversation, and you can continue talking, giving your own point of view. Keep your answers short (4 sentences MAX) and relevant to the current topic of discussion. /n CONVERSATION SUBJECT: {subject}."

    def add_entity(self, entity_name: str, entity_system_prompt: str):
        system_message = f"ROOM RULES: {self.room_system_prompt}\n YOU ARE {entity_name}: {entity_system_prompt}"
        self._entities.append(
            Entity(entity_name, system_message, self.memory)
        )

    def sweat(self, amount_of_messages: int = 10):
        exposed_entity_index = 0
        for _ in range(0, amount_of_messages):
            exposed_entity_index = _randint_exclude(0, len(self._entities) - 1, exposed_entity_index)
            exposed_entity = self._entities[exposed_entity_index]
            exposed_entity.talk()
            
def _randint_exclude(min: int, max: int, exclude: int) -> int:
    rand = exclude
    while rand == exclude:
        rand = randint(min, max)
        
    return rand
