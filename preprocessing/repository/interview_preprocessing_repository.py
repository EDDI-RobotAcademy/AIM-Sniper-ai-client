from abc import ABC, abstractmethod


class InterviewPreprocessingRepository(ABC):
    @abstractmethod
    def readRawJson(self):
        pass