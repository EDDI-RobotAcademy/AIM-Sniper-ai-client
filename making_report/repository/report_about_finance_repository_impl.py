import json
import os
import dart_fss as dart
from datetime import datetime, timedelta

from dotenv import load_dotenv
from tqdm import tqdm

from making_report.repository.report_about_finance_repository import ReportAboutFinanceRepository

load_dotenv()

dartApiKey = os.getenv('DART_API_KEY')
if not dartApiKey:
    raise ValueError("Dart API Key가 준비되어 있지 않습니다.")

class ReportAboutFinanceRepositoryImpl(ReportAboutFinanceRepository):
    __instance = None
    SEARCH_YEAR_GAP = 2
    SEARCH_START_YEAR = f'{(datetime.today() - timedelta(days=365*SEARCH_YEAR_GAP)).year}1231'
    SEARCH_END_YEAR = f'{datetime.today().year}1231'

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            dart.set_api_key(dartApiKey)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def saveData(self, dictData, directory):
        date = datetime.today().strftime("%Y_%m_%d")
        path = f"../{directory}"

        os.makedirs(path, exist_ok=True)
        with open(f"{path}/{date}.json", "w", encoding='UTF-8-sig') as file:
            json.dump(dictData, file, ensure_ascii=False, indent=4)


    def preprocessFSFromDart(self, *dfs):
        for df in dfs:
            newColList = [upperIndex
                          if type(lowerIndex) == tuple else lowerIndex
                          for (upperIndex, lowerIndex) in df.columns]

            df.columns = newColList

            numerical_cols = df.select_dtypes(exclude="O").columns
            df.set_index("concept_id", inplace=True)
            df.drop(columns=[col for col in df.columns if col not in numerical_cols], axis=1, inplace=True)

        return dfs

    def getFinancailStatements(self, corpCode):
        fs = dart.fs.extract(
            corp_code=corpCode, report_tp='annual',
            bgn_de=self.SEARCH_START_YEAR, end_de=self.SEARCH_END_YEAR,
            dataset="web", progressbar=False)

        balanceSheet, incomeStatement, cashFlow = \
                        self.preprocessFSFromDart(fs['bs'], fs['is'], fs['cf'])

        return balanceSheet, incomeStatement, cashFlow


    def getRevenueTrend(self, revenue):
        return revenue.to_dict()

    def getReceivableTurnover(self, revenue, tradeReceivables):
        revenue.index = revenue.index.map(lambda x: x[:4])
        tradeReceivables.index = tradeReceivables.index.map(lambda x: x[:4])

        receivableTturnover = (revenue / tradeReceivables)
        averagedReceivableTurnover = revenue / ((tradeReceivables.shift(1) + tradeReceivables) / 2)

        return receivableTturnover.to_dict()

    def getOperatingCashFlow(self, operatingCashFlow):
        return operatingCashFlow.to_dict()

    def getProfitDataFromDart(self, corpCodeDict):
        profitDataDict = {}

        for corpName, corpCode in tqdm(corpCodeDict.items(), desc="getProfitDataFromDart"):
            balanceSheet, incomeStatement, cashFlow = self.getFinancailStatements(corpCode)

            revenueTrend = self.getRevenueTrend(incomeStatement.loc["ifrs-full_Revenue"])
            receivableTurnover = self.getReceivableTurnover(
                                                    incomeStatement.loc["ifrs-full_Revenue"],
                                                    balanceSheet.loc["ifrs-full_CurrentTradeReceivables"])
            operatingCashFlow = self.getOperatingCashFlow(cashFlow.loc["ifrs-full_CashFlowsFromUsedInOperatingActivities"])

            profitDataDict[corpName] = {"revenueTrend": revenueTrend,
                                       "receivableTurnover": receivableTurnover,
                                       "operatingCashFlow":operatingCashFlow}

        self.saveData(profitDataDict, "../data/dart_financial_statements/preprocessed_data_v1")

        return profitDataDict
