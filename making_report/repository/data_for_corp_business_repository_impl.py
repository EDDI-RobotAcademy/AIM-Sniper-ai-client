import json
import os
import zipfile
from io import BytesIO

import dart_fss as dart

from datetime import datetime

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

from making_report.repository.data_for_corp_business_repository import DataForCorpBusinessRepository

load_dotenv()

dartApiKey = os.getenv('DART_API_KEY')
if not dartApiKey:
    raise ValueError("Dart API Key가 준비되어 있지 않습니다.")

openaiApiKey = os.getenv('OPENAI_API_KEY')
if not openaiApiKey:
    raise ValueError('API Key가 준비되어 있지 않습니다!')


class DataForCorpBusinessRepositoryImpl(DataForCorpBusinessRepository):
    __instance = None
    WANTED_CORP_LIST = [
        'SK네트웍스', 'SK이노베이션', 'SK텔레콤', 'SK하이닉스', '삼성전자', 'LG에너지솔루션', 'NAVER', '삼성바이오로직스',
        '삼성SDI', 'LG화학', '기아', 'POSCO홀딩스', '대한항공', '삼성물산', '현대모비스', 'LG전자', '한국전력공사', '셀트리온',
        'LG생활건강', 'HMM', '삼성생명', '하이브', '삼성전기', 'SK바이오사이언스', 'LG', 'S-Oil', '고려아연', '케이티앤지', '우리금융지주',
        '삼성에스디에스', '엔씨소프트', '삼성화재해상보험', '아모레퍼시픽', '포스코퓨처엠']

    WANTED_SEARCH_YEAR = 20230101
    WANTED_SEARCH_DOC = 'A'



    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            dart.set_api_key(api_key=dartApiKey)
            openai.api_key = openaiApiKey
            cls.__instance.__totalCorpList = dart.get_corp_list()
            cls.__instance.__wantedCorpCodeDict = cls.__instance.getCorpCode()
            cls.__instance.__wantedReceiptCodeDict = cls.__instance.getCorpReceiptCode()


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

    def getCorpCodeDict(self):
        return self.__wantedCorpCodeDict

    def alarmWrongRegisteredCorpName(self, name, corp):
        if not corp:
            print(f'기업명 입력 오류 "{name}"')
            expectedCorp = self.__totalCorpList.find_by_corp_name(name, exactly=False, market="YKN")

            if expectedCorp:
                print(f'-> 예상 변경 이름 {[corp.corp_name for corp in expectedCorp]}')

        return name

    def alarmMultiRegisteredCorpNames(self, name, corp):
        if isinstance(corp, list) and len(corp) >= 2:
            raise ValueError(f'기업명 "{name}" {len(corp)} 개 검색이 됩니다.')

    def getCorpCode(self):
        corpCodeDict = {}
        wrongInput = []

        for name in self.WANTED_CORP_LIST:
            corp = self.__totalCorpList.find_by_corp_name(name, exactly=True, market="YKN")
            if not corp:
                wrongInput.append(
                    self.alarmWrongRegisteredCorpName(name, corp))
            else:
                if wrongInput:
                    continue
                corpCodeDict[name] = corp[0].corp_code

            self.alarmMultiRegisteredCorpNames(name, corp)

        if wrongInput:
            raise ValueError(f"기업명 입력이 잘못되었습니다. {wrongInput}")

        return corpCodeDict

    def getCorpReceiptCode(self):
        corpReceiptCodeDict = {}
        for corpName, corpCode in self.__wantedCorpCodeDict.items():
            try:
                corpReportList = dart.filings.search(
                                    corp_code=corpCode,
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

    def apiResponseOfCorpDocument(self, receiptCode):
        url = 'https://opendart.fss.or.kr/api/document.xml'
        params = {
            'crtfc_key': dartApiKey,
            'rcept_no': receiptCode}

        return requests.get(url, params=params)

    def getDataFromZipFile(self, response):
        file = BytesIO(response.content)
        zfile = zipfile.ZipFile(file, 'r')
        corpDocuList = sorted(zfile.namelist(), key=lambda x: len(x))

        return zfile, corpDocuList

    def getOverviewDataFromXml(self, xmlFile, corpName, receiptCode):
        try:
            soup = BeautifulSoup(xmlFile, 'lxml-xml').find_all("SECTION-2")
            index = 0
            for idx, data in enumerate(soup):
                if data.find("TITLE").text[:15] == "1. 사업의 개요":
                    index = idx
                    break

            return soup[index]

        except Exception as e:
            print(f"\n*** getOverviewDataFromXml '{corpName}-{receiptCode}' -> {e}")
            pass

    def getAllDataFromXml(self, xmlFile, wanted_tag):
        soup = BeautifulSoup(xmlFile, 'lxml-xml')
        return soup.find_all(wanted_tag)

    def getRawDataFromDart(self):
        rawDataDict = {}
        rawCorpDataDict = {}
        for corpName, receiptCode in tqdm(self.getCorpReceiptCode().items(), desc="get_raw_data"):
            response = self.apiResponseOfCorpDocument(receiptCode)
            zipFile, corpDocuList = self.getDataFromZipFile(response)
            xmlFile = zipFile.read(corpDocuList[0])

            rawDataDict[corpName] = str(xmlFile)
            rawCorpDataDict[corpName] = str(self.getOverviewDataFromXml(xmlFile, corpName, receiptCode))

        self.saveData(rawDataDict, "../data/dart_corp_business/raw_data")
        self.saveData(rawCorpDataDict, "../data/dart_corp_business/preprocessed_data_v1")

        return rawCorpDataDict

    def preprocessTaginParagraph(self, paragraph):
        return paragraph.get_text().replace("\n", "")

    def preprocessRawData(self, rawData):
        preprocessDataDict = {}

        for corpName, corpData in tqdm(rawData.items(), desc="preprocess_data"):
            paragraphList = self.getAllDataFromXml(corpData, "P")

            result = [self.preprocessTaginParagraph(paragraph)
                      for paragraph in paragraphList]

            preprocessDataDict[corpName] = "\n".join(result)

        self.saveData(preprocessDataDict, "../data/dart_corp_business/preprocessed_data_v2")

        return preprocessDataDict

    def changeContentStyle(self, preprocessedData):
        maxTokenLength = 16385
        promptEngineering = f"""
        사용자 입력 메시지의 내용을 <조건>에 맞춰 5가지 포인트로 정리하라.

        <조건>
        1. 개조식으로 작성할 것.
        2. bullet point로 작성할 것.
        3. 800 token 내로 작성을 마무리할 것.
        """

        changedContextDict = {}
        for corpName, doc in preprocessedData.items():
            if len(doc) >= maxTokenLength:
                print(f"사업내용 토큰 수 초과 -> {corpName}")
                continue

            messages = [
                {"role": "system", "content": promptEngineering},
                {"role": "user", "content": doc}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )

            changedContextDict[corpName] = response.choices[0]['message']['content']

        self.saveData(changedContextDict, "../data/dart_corp_business/preprocessed_data_v3")

        return changedContextDict