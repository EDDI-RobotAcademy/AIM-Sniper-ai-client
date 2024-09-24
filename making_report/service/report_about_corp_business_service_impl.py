from making_report.repository.report_about_corp_business_repository_impl import ReportAboutCorpBusinessRepositoryImpl
from making_report.service.report_about_corp_business_service import ReportAboutCorpBusinessService


class ReportAboutCorpBusinessServiceImpl(ReportAboutCorpBusinessService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__corpBusinessRepository = ReportAboutCorpBusinessRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def makingReportAboutCorpBusiness(self):
        rawData = self.__corpBusinessRepository.getRawDataFromDart()
        preprocessedData = self.__corpBusinessRepository.preprocessRawData(rawData)
