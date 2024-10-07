from making_report.repository.data_for_corp_business_repository_impl import DataForCorpBusinessRepositoryImpl
from making_report.repository.data_for_corp_overview_repository_impl import DataForCorpOverviewRepositoryImpl
from making_report.repository.data_for_finance_repository_impl import DataForFinanceRepositoryImpl
from making_report.repository.making_report_repository_impl import MakingReportRepositoryImpl
from making_report.service.making_report_service import MakingReportService


class MakingReportServiceImpl(MakingReportService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__corpBusinessRepository = DataForCorpBusinessRepositoryImpl.getInstance()
            cls.__instance.__corpOverviewRepository = DataForCorpOverviewRepositoryImpl.getInstance()
            cls.__instance.__financeRepository = DataForFinanceRepositoryImpl.getInstance()
            cls.__instance.__reportRepository = MakingReportRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def makingReport(self):
        corpCodeDict = self.__corpBusinessRepository.getCorpCodeDict()

        print(f"* CORP_OVERVIEW start ----------------")
        corpOverviewRawData = self.__corpOverviewRepository.getRawOverviewDataFromDart(corpCodeDict)
        corpOverviewPreprocessedData = self.__corpOverviewRepository.preprocessRawData(corpOverviewRawData)

        print(f"* CORP_BUSINESS start ----------------")
        corpBusinessRawData = self.__corpBusinessRepository.getRawDataFromDart()
        corpBusinessPreprocessedData = self.__corpBusinessRepository.preprocessRawData(corpBusinessRawData)
        corpBusinessSummary = self.__corpBusinessRepository.changeContentStyle(corpBusinessPreprocessedData)

        print(f"* FINANCIAL_STATEMENTS start ----------------")
        financeProfitDict = self.__financeRepository.getFinancialDataFromDart(corpCodeDict)

        print(f"* REPORT start ----------------")
        makeReport = self.__reportRepository.gatherData(corpCodeDict.keys(),
                                                        corpOverviewPreprocessedData, financeProfitDict, corpBusinessSummary)