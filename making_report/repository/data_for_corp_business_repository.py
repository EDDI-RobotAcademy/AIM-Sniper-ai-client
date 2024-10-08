from abc import ABC, abstractmethod


class DataForCorpBusinessRepository(ABC):
    @abstractmethod
    def saveData(self, dictData, directory):
        pass

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
    def getCorpReceiptCode(self):
        pass

    @abstractmethod
    def getTagDataFromRequest(self, wantedContentUrl, wanted_tag):
        pass

    @abstractmethod
    def getWebDriverAboutReport(self, receiptCode):
        pass

    @abstractmethod
    def getContentsFromDriver(self, driver):
        pass

    @abstractmethod
    def getRawDataFromDart(self):
        pass

    @abstractmethod
    def changeContentStyle(self, preprocessedData):
        pass