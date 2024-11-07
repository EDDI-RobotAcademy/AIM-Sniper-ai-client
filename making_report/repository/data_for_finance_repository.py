from abc import ABC, abstractmethod


class DataForFinanceRepository(ABC):

    @abstractmethod
    def parsingFromOpenAPI(self, corpCode):
        pass

    @abstractmethod
    def getFinancialStatements(self, parsedData, financialStatementsType):
        pass

    @abstractmethod
    def selectIncomeDocument(self, parsedData):
        pass

    @abstractmethod
    def checkLabelNameInFS(self, dfIndex, *probableNames):
        pass

    @abstractmethod
    def checkExactLabelNameInFS(self, dfIndex, *probableNames):
        pass

    @abstractmethod
    def getRevenueTrend(self, income):
        pass

    @abstractmethod
    def getProfitTrend(self, income):
        pass

    @abstractmethod
    def getOwnersCapital(self, balance):
        pass

    @abstractmethod
    def getFinancialDataFromDart(self, corpCodeDict):
        pass