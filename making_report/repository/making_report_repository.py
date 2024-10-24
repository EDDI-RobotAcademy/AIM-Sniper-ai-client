from abc import ABC, abstractmethod


class MakingReportRepository(ABC):
    @abstractmethod
    def getKeysInDictValues(self, dict):
        pass

    @abstractmethod
    def gatherData(self, corpNameList, *data):
        pass
