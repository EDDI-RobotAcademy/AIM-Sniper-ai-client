from abc import ABC, abstractmethod


class OpenAIService(ABC):
    @abstractmethod
    def testai(self, userSendMessage):
        pass