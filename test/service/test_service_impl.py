from test.repository.test_repository_impl import TestRepositoryImpl
from test.service.test_service import TestService


class TestServiceImpl(TestService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__testRepository = TestRepositoryImpl.getInstance()

            return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def printTestWord(self, *arg, **kwargs):
        testWord1 = arg[0]
        testWord2 = arg[1]

        return self.__testRepository.printTestWord(testWord1, testWord2)

