from abc import ABC, abstractmethod


class MakingReportService(ABC):
    @abstractmethod
    def makingReport(self):
        pass
