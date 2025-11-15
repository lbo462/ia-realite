from random import randint
from uuid import uuid4
from langchain.agents import create_agent

from .chat_memory import ChatMemory
from .chat_model import llm, get_response_content

from .entity import Entity


class Room:
    """
    A room is an entity aggregator
    """

    def __init__(self, subject: str):
        self.uuid = uuid4()
        self.room_system_prompt = self._build_room_system_prompt(subject)
        self.memory = ChatMemory(room_id=str(self.uuid))
        self.entities = list()
        self.summary = ""
        
    # dans Room
    def _build_room_system_prompt(self, subject: str) -> str:
        return f"ROOM RULES: /n In this room, there are entites with different personalities. They talk to each other and try to give different point of view concerning the same CONVERSATION SUBJECT of discussion. You are one of them. When you are told: It's your turn, you will receive the current state of the conversation, and you can continue talking, giving your own point of view. Keep your answers short (4 sentences MAX) and relevant to the current topic of discussion. /n CONVERSATION SUBJECT: {subject}."

    def add_entity(self, entity_name: str, entity_system_prompt: str):
        system_message = f"{self.room_system_prompt}\n YOU ARE {entity_name}: {entity_system_prompt}"
        self.entities.append(
            Entity(entity_name, system_message, self.memory)
        )
    
    def _generate_entity_summary(self):
        summary_system_prompt = f"""INSTRUCTION: 
Now that the conversation has ended, you have to generate a short, concise summary of each entity's point of view in the conversation. An entity is the one that has their name at the beginning of each paragraph, which is followed by a ":" (same name = same entity). You will also have the room rules and the whole conversation as context to understand better the context. DO NOT invent new information NOR return the whole conversation as it is.
ROOM RULES:
{self.room_system_prompt}
CONVERSATION:
{self.memory.messages}
"""
        agent = create_agent(
            model=llm,
            system_prompt=summary_system_prompt
        )
        
        ai_response = agent.invoke(
            {"messages": [{"role": "user", "content": "Generate summary"}]}
        )
        
        self.summary = get_response_content(ai_response)

    def sweat(self, amount_of_messages: int = 10):
        exposed_entity_index = 0
        for _ in range(0, amount_of_messages):
            exposed_entity_index = _randint_exclude(0, len(self.entities) - 1, exposed_entity_index)
            exposed_entity = self.entities[exposed_entity_index]
            exposed_entity.talk()
            
        # When it's done, generate a summary
        self._generate_entity_summary()
        # Then, send final signal to close conversation phase
        self.memory.add_message("system", "END OF CONVERSATION BETWEEN ENTITIES")
        
    def post_sweat_chat(self, entity_index: int, prompt: str) -> str:
        if entity_index < 0 or entity_index >= len(self.entities):
            raise ValueError("Invalid entity index")
        
        entity = self.entities[entity_index]
        
        return entity.talk(prompt=prompt)
        
        

def _randint_exclude(min: int, max: int, exclude: int) -> int:
    rand = exclude
    while rand == exclude:
        rand = randint(min, max)
        
    return rand
