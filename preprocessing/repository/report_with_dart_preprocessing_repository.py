from abc import ABC, abstractmethod


class ReportWithDartPreprocessingRepository(ABC):
    @abstractmethod
    def checkRegisteredCorpInDart(self):
        pass

    @abstractmethod
    def getCorpReceiptCode(self):
        pass

    @abstractmethod
    def getCorpDocument(self):
        pass