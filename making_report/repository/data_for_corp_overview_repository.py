from abc import ABC, abstractmethod


class DataForCorpOverviewRepository(ABC):
    @abstractmethod
    def saveData(self, dictData, directory):
        pass

    @abstractmethod
    def getRawOverviewDataFromDart(self, corpCodeDict):
        pass

    @abstractmethod
    def preprocessRawData(self, corpOverviewRawData):
        pass
