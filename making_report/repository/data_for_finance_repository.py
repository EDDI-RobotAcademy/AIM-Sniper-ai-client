from abc import ABC, abstractmethod


class DataForFinanceRepository(ABC):
    @abstractmethod
    def saveData(self, dictData, directory):
        pass
    @abstractmethod
    def preprocessFSFromDart(self, *dfs):
        pass

    @abstractmethod
    def selectIncomeDocument(self, incomeDf, comprehensiveIncomeDf):
        pass

    @abstractmethod
    def getFinancialStatements(self, corpCode):
        pass

    @abstractmethod
    def checkLabelNameInFS(self, df, *probableNames):
        pass

    @abstractmethod
    def checkLabelComboNameInFS(self, df, *comboNames):
        pass

    @abstractmethod
    def getRevenueTrend(self, income):
        pass

    @abstractmethod
    def getReceivableTurnover(self, income, balance):
        pass

    @abstractmethod
    def getOperatingCashFlow(self, cashFlow):
        pass

    @abstractmethod
    def getProfitDataFromDart(self, corpCodeDict):
        pass