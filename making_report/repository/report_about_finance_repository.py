from abc import ABC, abstractmethod


class ReportAboutFinanceRepository(ABC):
    @abstractmethod
    def getRawDataFromDart(self):
        pass

    @abstractmethod
    def preprocessRawData(self):
        pass
