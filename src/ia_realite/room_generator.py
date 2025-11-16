import json
from langchain.agents import create_agent

from .room import Room
from .chat_model import llm, get_response_content


def randomize_room(
    room_subject: str, number_of_entities: int, preference: str = ""
) -> Room:
    random_system_prompt = f"""INSTRUCTION: 
You are a personality generator. You are in a room where there are {number_of_entities} people, who will discuss around the same ROOM SUBJECT. Your job is to generate the personality of each of these people. 
RULES:
- Given ROOM SUBJECT, generate exactly {number_of_entities} different personalities.
- Each personality must be concise (maximum 2 sentences).
- They must be characters who are interested in the ROOM SUBJECT and who can give various point of view to the ROOM SUBJECT. For example, if the ROOM SUBJECT is "Usage of AI", you can generate an artist, a developer, a teacher, etc.
OUTPUT: 
- Return ONLY a valid JSON list of pairs (each pair is a two-element list), contains EXACTLY {number_of_entities} pairs. 
- Each pair represents a person, which must contain:
  - First element: the name of the entity (string).
  - Second element: the personality/system prompt of the entity (string).
- Example: [["Paul", "42 years old, an artist who works in modern art"], ["Marina", "27 years old, a developer who works particularly in AI and machine learning"], ["Dr. Smith", "50 years old, a teacher who teaches history at university"]]
ROOM SUBJECT:
{room_subject}
"""
    agent = create_agent(model=llm, system_prompt=random_system_prompt)

    ai_response = agent.invoke(
        {"messages": [{"role": "user", "content": "Generate personalities"}]}
    )

    room = Room(subject=room_subject, preference=preference)

    response = json.loads(get_response_content(ai_response))

    for name, system_prompt in response:
        room.add_entity(name, system_prompt)

    return room
