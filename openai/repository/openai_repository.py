from abc import abstractmethod, ABC


class OpenAIRepository(ABC):
    @abstractmethod
    def generateQuestion(self, userSendMessage):
        pass