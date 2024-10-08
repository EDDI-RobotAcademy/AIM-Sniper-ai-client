from abc import ABC, abstractmethod


class TestRepository(ABC):
    @abstractmethod
    def printTestWord(self, testWord1, testWord2):
        pass