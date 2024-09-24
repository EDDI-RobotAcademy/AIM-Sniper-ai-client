import os
from abc import ABC, abstractmethod


class ReportAboutCorpBusinessService(ABC):
    @abstractmethod
    def makingReportAboutCorpBusiness(self):
        pass