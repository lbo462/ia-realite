from uuid import UUID


class Entity:
    def __init__(self, agent):
        self._uuid = UUID()
        self._agent = agent

    def _generate_message(self) -> str:
        message = "Hi"
        return f"{self._uuid} says: {message}"

    def talk(self):
        """
        Sends a message to the LLM using its langchain agent
        :return:
        """
        message = self._generate_message()  # noqa
        self._agent.invoke(...)
