from abc import ABC, abstractmethod


class DataForCorpOverviewRepository(ABC):

    @abstractmethod
    def getRawOverviewDataFromDart(self, corpCodeDict):
        pass

    @abstractmethod
    def preprocessRawData(self, corpOverviewRawData):
        pass
