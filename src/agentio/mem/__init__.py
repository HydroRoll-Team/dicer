import abc
from typing import List, Any, Dict
from ..types import AgentMessage

class Memory(abc.ABC):
    @abc.abstractmethod
    def add(self, message: AgentMessage):
        pass

    @abc.abstractmethod
    def get_all(self) -> List[AgentMessage]:
        pass

class EphemeralMemory(Memory):
    def __init__(self):
        self.messages: List[AgentMessage] = []

    def add(self, message: AgentMessage):
        self.messages.append(message)

    def get_all(self) -> List[AgentMessage]:
        return self.messages
