import json, os, zipfile
from datetime import datetime, timedelta
from io import BytesIO

from dotenv import load_dotenv

import dart_fss as dart
import openai
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless=new")
import time

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
    # WANTED_CORP_LIST = ["케이티"]
    WANTED_CORP_LIST = ["SK네트웍스", "삼성전자", "현대자동차", "SK하이닉스", "LG전자", "POSCO홀딩스", "NAVER", "현대모비스", "기아", "LG화학", "삼성물산", "롯데케미칼", "SK이노베이션", "S-Oil", "CJ제일제당", "현대건설", "삼성에스디에스", "LG디스플레이", "아모레퍼시픽", "한화솔루션", "HD현대중공업", "LS", "두산에너빌리티", "SK텔레콤", "케이티", "LG유플러스", "HJ중공업", "삼성전기", "한화에어로스페이스", "효성", "코웨이", "한샘", "신세계", "이마트", "현대백화점", "LG생활건강", "GS리테일", "오뚜기", "농심", "롯데웰푸드", "CJ ENM", "한화", "LG이노텍", "삼성바이오로직스", "셀트리온"]

    SEARCH_YEAR_GAP = 1
    WANTED_SEARCH_YEAR = f'{(datetime.today() - timedelta(days=365*SEARCH_YEAR_GAP)).year}0101'
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
                                        if ('사업보고서' in report.report_nm) and (r'[첨부정정]' not in report.report_nm))
                                       , None)

                corpReceiptCodeDict[corpName] = corpReceiptCode

            except Exception as e:
                print(f"[ERROR] {corpName} -> \n {e}")
                pass

        return corpReceiptCodeDict


    def getWebDriverAboutReport(self, receiptCode):
        url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receiptCode}"
        driver = webdriver.Chrome(options=options)
        driver.get(url=url)
        return driver

    def getContentsFromDriver(self, driver):
        dartContent = driver.find_element(By.CSS_SELECTOR, "#listTree")
        return dartContent.find_elements(By.CSS_SELECTOR, "a")

    def getUrlFromWantedContent(self, driver, contentList, wantedContent):
        url = []
        for content in contentList:
            if wantedContent in content.text:
                content.click()
                url.append(driver.find_element(By.CSS_SELECTOR, ".viewWrap iframe").get_attribute("src"))
        return url

    def getTagDataFromRequest(self, wantedContentUrl, wanted_tag):
        tagDataList = []
        for url in wantedContentUrl:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            tagDataList.extend(soup.find_all(wanted_tag))

        return tagDataList

    def getRawDataFromDart(self):
        rawCorpDataDict = {}
        for corpName, receiptCode in self.getCorpReceiptCode().items():
            print(f"* CB_RAW - {corpName}")
            driver = self.getWebDriverAboutReport(receiptCode)
            time.sleep(1)

            contentList = self.getContentsFromDriver(driver)
            wantedContentUrl = self.getUrlFromWantedContent(driver, contentList, "사업의 개요")

            paragraphList = self.getTagDataFromRequest(wantedContentUrl, "p")
            combinedParagraph = " ".join([paragraph.get_text().replace("\xa0", " ")
                                          for paragraph in paragraphList
                                          if paragraph.get_text() != None])

            rawCorpDataDict[corpName] = combinedParagraph

        self.saveData(rawCorpDataDict, "../data/dart_corp_business/preprocessed_data_v2")

        return rawCorpDataDict

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
            print(f"* CB_AI - {corpName}")
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

            changedContextDict[corpName] = {"businessSummary": response.choices[0]['message']['content']}

        self.saveData(changedContextDict, "../data/dart_corp_business/preprocessed_data_v3")

        return changedContextDict