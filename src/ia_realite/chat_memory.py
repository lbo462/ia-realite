class ChatMemory:
    """
    Simple in-memory chat memory.
    Lives only in RAM, nothing is written to disk.
    """

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.memory = []  # List of dicts
        
    @property
    def messages(self):
        """
        Convert ChatMemory list into LangChain-compatible messages.
        """
        messages = []
        for msg in self.memory:
            messages.append({
                "role": "user",
                "content": f"{msg['entity']}: {msg['message']}"
            })
        return messages

    def add_message(self, entity_name: str, message: str):
        self.memory.append({
            "entity": entity_name,
            "message": message
        })
        