import pickle

from making_report.repository.report_about_corp_business_repository_impl import ReportAboutCorpBusinessRepositoryImpl
from making_report.repository.report_about_finance_repository_impl import ReportAboutFinanceRepositoryImpl
from making_report.service.making_report_service import MakingReportService


class MakingReportServiceImpl(MakingReportService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__corpBusinessRepository = ReportAboutCorpBusinessRepositoryImpl.getInstance()
            cls.__instance.__financeRepository = ReportAboutFinanceRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def makingReport(self):
        corpCodeDict = self.__corpBusinessRepository.getCorpCodeDict()

        corpBusinessRawData = self.__corpBusinessRepository.getRawDataFromDart()
        corpBusinessPreprocessedData = self.__corpBusinessRepository.preprocessRawData(corpBusinessRawData)
        corpBusinessSummary = self.__corpBusinessRepository.changeContentStyle(corpBusinessPreprocessedData)

        financeProfitDict = self.__financeRepository.getProfitDataFromDart(corpCodeDict)
