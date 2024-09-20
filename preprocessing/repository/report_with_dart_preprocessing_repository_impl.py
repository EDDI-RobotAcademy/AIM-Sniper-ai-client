import os, requests
import zipfile
from io import BytesIO

import dart_fss as dart

from dotenv import load_dotenv
from preprocessing.repository.report_with_dart_preprocessing_repository import ReportWithDartPreprocessingRepository

load_dotenv()

dartApiKey = os.getenv('DART_API_KEY')
if not dartApiKey:
    raise ValueError("Dart API Key가 준비되어 있지 않습니다.")

class ReportWithDartPreprocessingRepositoryImpl(ReportWithDartPreprocessingRepository):
    __instance = None
    WANTED_CORP_LIST = [
        '삼성전자', 'LG에너지솔루션', 'SK하이닉스', 'NAVER', '삼성바이오로직스', '카카오',
        '삼성SDI', '현대자동차', 'LG화학', '기아', 'POSCO홀딩스', 'KB금융', '카카오뱅크', '셀트리온',
        '신한지주', '삼성물산', '현대모비스', 'SK이노베이션', 'LG전자', '카카오페이', 'SK', '한국전력공사',
        '크래프톤', '하나금융지주', 'LG생활건강', 'HMM', '삼성생명', '하이브', '두산에너빌리티', 'SK텔레콤',
        '삼성전기', 'SK바이오사이언스', 'LG', 'S-Oil', '고려아연', '케이티앤지', '우리금융지주', '대한항공',
        '삼성에스디에스', 'HD현대중공업', '엔씨소프트', '삼성화재해상보험', '아모레퍼시픽', '케이티', '포스코퓨처엠',
        '넷마블', 'SK아이이테크놀로지', 'LG이노텍', '기업은행']

    WANTED_SEARCH_YEAR = 20230101
    WANTED_SEARCH_DOC = 'A'  # A : 정기공시, B : 주요사항보고, C : 발행공시, D : 지분공시, E : 기타공시, F : 외부감사관련, G : 펀드공시, H : 자산유동화, I : 거래소공시, J : 공정위공시

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            dart.set_api_key(api_key=dartApiKey)
            cls.__instance.__totalCorpList = dart.get_corp_list()
            cls.__instance.__wantedCorpCorpCodeDict = cls.__instance.checkRegisteredCorpInDart()
            cls.__instance.__wantedCorpReportDict = cls.__instance.getCorpDocument()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def checkRegisteredCorpInDart(self):
        corpCodeDict = {}
        wrongInput = []
        for name in self.WANTED_CORP_LIST:
            corp = self.__totalCorpList.find_by_corp_name(name, exactly=True, market="YKN")

            if not corp:
                wrongInput.append(name)
                print(f'기업명 입력 오류 "{name}"')
                expectedCorp = self.__totalCorpList.find_by_corp_name(name, exactly=False, market="YKN")
                if expectedCorp:
                    print(f'-> 예상 변경 이름 {[corp.corp_name for corp in expectedCorp]}')
            else:
                corpCodeDict[name] = corp[0].corp_code

            if isinstance(corp, list) and len(corp) >= 2:
                raise ValueError(f'기업명 "{name}" {len(corp)} 개 검색이 됩니다.')

        if wrongInput:
            raise ValueError(f"기업명 입력이 잘못되었습니다. {wrongInput}")

        return corpCodeDict

    def getCorpReceiptCode(self):
        corpReceiptCodeDict = {}
        for corpName, stockCode in self.__wantedCorpCorpCodeDict.items():
            try:
                corpReportList = dart.filings.search(
                                    corp_code=stockCode,
                                    bgn_de=self.WANTED_SEARCH_YEAR,
                                    pblntf_ty=self.WANTED_SEARCH_DOC
                                ).report_list

                corpReceiptCode = next((report.rcept_no
                                         for report in corpReportList
                                         if '사업보고서' in report.report_nm), None)

                corpReceiptCodeDict[corpName] = corpReceiptCode

            except Exception as e:
                print(f"[ERROR] {corpName} -> \n {e}")
                pass

        return corpReceiptCodeDict

    def apiResponseForCorpDocument(self, receiptCode):
        url = 'https://opendart.fss.or.kr/api/document.xml'
        params = {
            'crtfc_key': dartApiKey,
            'rcept_no': receiptCode}

        return requests.get(url, params=params)

    def getFileListFromZipFile(self, response):
        file = BytesIO(response.content)
        zfile = zipfile.ZipFile(file, 'r')
        corpDocuList = sorted(zfile.namelist(), key=lambda x: len(x))
        return zfile, corpDocuList


    def getCorpDocument(self):
        corpRawReportDict = {}
        for corpName, receiptCode in self.getCorpReceiptCode().items():
            response = self.apiResponseForCorpDocument(receiptCode)
            zfile, corpDocuList = self.getFileListFromZipFile(response)

            with zfile.open(corpDocuList[0]) as f:
                content = f.read()

            corpRawReportDict[corpName] = content

        return corpRawReportDict

    def printCorpDocumentList(self):
        print(self.__wantedCorpReportDict.keys())