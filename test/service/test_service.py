from abc import ABC, abstractmethod


class TestService(ABC):
    @abstractmethod
    def printTestWord(self, *arg, **kwargs):
        pass