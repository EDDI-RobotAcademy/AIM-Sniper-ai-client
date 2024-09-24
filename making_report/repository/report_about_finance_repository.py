from abc import ABC, abstractmethod


class ReportAboutFinanceRepository(ABC):
    @abstractmethod
    def saveData(self, dictData, directory):
        pass

    @abstractmethod
    def preprocessFSFromDart(self, *dfs):
        pass

    @abstractmethod
    def getFinancailStatements(self, corpCode):
        pass

    @abstractmethod
    def getRevenueTrend(self, revenue):
        pass

    @abstractmethod
    def getReceivableTurnover(self, revenue, tradeReceivables):
        pass

    @abstractmethod
    def getOperatingCashFlow(self, operatingCashFlow):
        pass

    @abstractmethod
    def getProfitDataFromDart(self, corpCodeDict):
        pass