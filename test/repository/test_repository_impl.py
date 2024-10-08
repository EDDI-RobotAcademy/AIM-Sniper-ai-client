from test.repository.test_repository import TestRepository


class TestRepositoryImpl(TestRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def printTestWord(self, testWord1, testWord2):
        print(f"testWord1: {testWord1}")
        print(f"testWord2: {testWord2}")
        print("Test success")

        return {"testWord": [testWord1, testWord2]}
