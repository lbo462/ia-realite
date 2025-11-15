from src.ia_realite.entity import Entity
from src.ia_realite.room import Room

room_subject= "Usage of AI."

room = Room(room_subject)

room.add_entity("Agent A", "an artist")
room.add_entity("Agent B", "a developper")

room.sweat(2)

for m in room.memory.messages:
    print(m["content"])
    
print("\n--- SUMMARY ---\n")
print(room.summary)

print("\n--- POST CHAT ---\n")
user_message = "As an artist, don't you think that AI can be a threat to creativity?"
print(f"USER MESSAGE: {user_message}")
print(f"{room.entities[0].name}: {room.post_sweat_chat(0, user_message)}")
