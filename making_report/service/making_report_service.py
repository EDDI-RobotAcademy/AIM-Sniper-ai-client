from abc import ABC, abstractmethod


class MakingReportService(ABC):
    @abstractmethod
    async def makingReport(self, request):
        pass
