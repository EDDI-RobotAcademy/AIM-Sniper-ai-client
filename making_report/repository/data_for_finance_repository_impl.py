import json
import os
import dart_fss as dart
from datetime import datetime, timedelta

from dotenv import load_dotenv
from tqdm import tqdm

from making_report.repository.data_for_finance_repository import DataForFinanceRepository

load_dotenv()

dartApiKey = os.getenv('DART_API_KEY')
if not dartApiKey:
    raise ValueError("Dart API Key가 준비되어 있지 않습니다.")

class DataForFinanceRepositoryImpl(DataForFinanceRepository):
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
            df.set_index(["label_ko", "label_en"], inplace=True)
            df.drop(columns=[col for col in df.columns if col not in numerical_cols], axis=1, inplace=True)

        return dfs

    def selectIncomeDocument(self, incomeDf, comprehensiveIncomeDf):
        if comprehensiveIncomeDf is None:
            return incomeDf

        if incomeDf is None:
            return comprehensiveIncomeDf

        return incomeDf

    def getFinancialStatements(self, corpCode):
        print(os.getcwd())
        fs = dart.fs.extract(
            corp_code=corpCode, report_tp='annual',
            bgn_de=self.SEARCH_START_YEAR, end_de=self.SEARCH_END_YEAR,
            dataset="web", progressbar=False)

        # [TODO] raw_data local에 저장

        balance, income, cashFlow = \
            self.preprocessFSFromDart(fs['bs'], self.selectIncomeDocument(fs['is'], fs['cis']), fs['cf'])

        return balance, income, cashFlow

    def checkLabelNameInFS(self, df, *probableNames):
        for index in df.index:
            if any(keyword in "".join(index) for keyword in probableNames):
                return index
            else:
                continue

        return 0

    def checkLabelComboNameInFS(self, df, *comboNames):
        for index in df.index:
            if all(keyword in "".join(index) for keyword in comboNames):
                return index
            else:
                continue

        return 0

    def getRevenueTrend(self, income):
        name = self.checkLabelNameInFS(
            income, "매출액", "영업수익", "수익(매출액)", "Revenue", "Sales")

        return income.loc[name].to_dict()

    def getReceivableTurnover(self, income, balance):
        revenueName = self.checkLabelNameInFS(income, "매출액", "영업수익", "수익(매출액)", "Revenue", "Sales")
        receivableName = self.checkLabelNameInFS(balance, "매출채권", "trade receivables")

        revenue = income.loc[revenueName]
        tradeReceivables = balance.loc[receivableName]

        revenue.index = revenue.index.map(lambda x: x[:4])
        tradeReceivables.index = tradeReceivables.index.map(lambda x: x[:4])

        receivableTturnover = (revenue / tradeReceivables)
        averagedReceivableTurnover = revenue / ((tradeReceivables.shift(1) + tradeReceivables) / 2)

        return receivableTturnover.to_dict()

    def getOperatingCashFlow(self, cashFlow):
        name = self.checkLabelComboNameInFS(cashFlow, "영업활동", "현금흐름")

        return cashFlow.loc[name].to_dict()

    def getProfitDataFromDart(self, corpCodeDict):
        profitDataDict = {}

        for corpName, corpCode in corpCodeDict.items():
            try:
                balance, income, cashFlow = self.getFinancialStatements(corpCode)
            except Exception as e:
                print(f"[NOT_PASS '{corpName}({corpCode})-FSDocu'] => {e}")
                pass

            try:
                revenueTrend = self.getRevenueTrend(income)
                receivableTurnover = self.getReceivableTurnover(income, balance)
                operatingCashFlow = self.getOperatingCashFlow(cashFlow)

            except Exception as e:
                print(f"[NOT_PASS '{corpName}({corpCode})-FSValue'] => {e}")
                pass

            profitDataDict[corpName] = {"revenueTrend": revenueTrend,
                                       "receivableTurnover": receivableTurnover,
                                       "operatingCashFlow":operatingCashFlow}

            print(f"*** '{corpName}' finish - {profitDataDict}")

        # self.saveData(profitDataDict, "../data/dart_financial_statements/preprocessed_data_v1")

        return profitDataDict
