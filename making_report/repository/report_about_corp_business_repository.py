from abc import ABC, abstractmethod


class ReportAboutCorpBusinessRepository(ABC):
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
    def apiResponseOfCorpDocument(self, receiptCode):
        pass

    @abstractmethod
    def getDataFromZipFile(self, response):
        pass

    @abstractmethod
    def getOverviewDataFromXml(self, xmlFile, corpName):
        pass

    @abstractmethod
    def getAllDataFromXml(self, xmlFile, wanted_tag):
        pass

    @abstractmethod
    def getRawDataFromDart(self):
        pass

    @abstractmethod
    def preprocessRawData(self, rawData):
        pass

    @abstractmethod
    def changeContentStyle(self, preprocessedData):
        pass

