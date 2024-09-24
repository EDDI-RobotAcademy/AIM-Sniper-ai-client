from abc import ABC, abstractmethod


class MakingReportService(ABC):
    @abstractmethod
    def makingReportAboutCorpBusiness(self):
        pass

    @abstractmethod
    def makingReportAboutFinance(self):
        pass