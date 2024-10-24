from abc import ABC, abstractmethod


class DataForCorpBusinessRepository(ABC):

    @abstractmethod
    def getCorpCodeDict(self):
        pass

    @abstractmethod
    def alarmWrongRegisteredCorpName(self, name, corp):
        pass

    @abstractmethod
    def alarmMultiRegisteredCorpNames(self, name, corp):
        pass

    @abstractmethod
    def getCorpCode(self):
        pass

    @abstractmethod
    def getRawBusinessDataFromDart(self):
        pass

    @abstractmethod
    def changeContentStyle(self, businessData):
        pass
