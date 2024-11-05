from openai.repository.openai_repository_impl import OpenAIRepositoryImpl
from openai.service.openai_service import OpenAIService


class OpenAIServiceImpl(OpenAIService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__openaiApiRepositoryImpl = OpenAIRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def testai(self, userSendMessage):
        return await self.__openaiApiRepositoryImpl.generateQuestion(userSendMessage)