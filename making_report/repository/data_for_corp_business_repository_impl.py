import json, os
from datetime import datetime, timedelta

from dotenv import load_dotenv

import dart_fss as dart
import openai
from bs4 import BeautifulSoup

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
    WANTED_CORP_LIST = ["SK네트웍스", "삼성전자", "현대자동차", "SK하이닉스", "LG전자", "POSCO홀딩스", "NAVER", "현대모비스", "기아", "LG화학", "삼성물산", "롯데케미칼", "SK이노베이션", "S-Oil", "CJ제일제당", "현대건설", "삼성에스디에스", "LG디스플레이", "아모레퍼시픽", "한화솔루션", "HD현대중공업", "LS", "SK텔레콤", "케이티", "LG유플러스", "HJ중공업", "삼성전기", "한화에어로스페이스", "효성", "코웨이", "한샘", "신세계", "이마트", "현대백화점", "LG생활건강", "GS리테일", "오뚜기", "농심", "롯데웰푸드", "CJ ENM", "한화", "LG이노텍", "삼성바이오로직스", "셀트리온"]

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


        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

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

    def getRawBusinessDataFromDart(self):
        rawSummaryDict, rawTableDict = {}, {}
        for corpName in self.WANTED_CORP_LIST:
            filePath = "../assets/company_data/"
            with open(f"{filePath}{corpName}.html", "r", encoding="utf-8-sig") as f:
                companyHtml = f.read()
            companySoup = BeautifulSoup(companyHtml, "html.parser")

            companyData = []
            for tag in companySoup.find_all("h1"):
                companyData.append(tag.find_next())
            rawSummaryDict[corpName] = str(companyData[0])
            rawTableDict[corpName] = {"revenueTable": str(companyData[1])}

        return rawSummaryDict, rawTableDict


    def changeContentStyle(self, businessData):
        maxTokenLength = 128000
        promptEngineering = f"""
        사용자 입력 메시지의 내용은 한국기업의 사업내용이다. 너는 기업을 전문적으로 분석하는 유능한 분석가이다.
        모든 <조건>에 맞춰, <구조>과 같은 구조로 한국기업의 사업내용을 요약하라.

        <조건>
        1. 개조식으로 작성할 것. 
            (예시: [BEFORE] 회사는 지속적인 기술 및 서비스에 대한 투자를 통해 핵심 사업의 경쟁력을 강화하고 있습니다. -> [AFTER] 지속적인 기술 및 서비스에 대한 투자를 통해 핵심 사업의 경쟁력을 강화)
        2. 1500 token 내로 작성을 마무리할 것.
        3. 첫 문단은 취업준비생들을 위해 요청한 사업내용 요약에 대한 전반적인 총평과 기업 공략 포인트에 대해서 정리해서 기재할 것.
        4. 첫 문단 이후에 요청한 사업내용 요약을 기재할 것.
        
        <구조>
        1. 글을 HTML 형식으로 요약할것
        2. 목록은 <ul>과 <li> 태그로 표현할 것.
        3. 태그 사이에 띄어쓰기('\n') 없이 한 줄로 표현할 것.
        예시:
        <p>첫 문단(전반적인 총평과 기업 공략 포인트)</p><ul><li>상위 목록 항목 1<ul><li>하위 목록 항목 1.1</li><li>하위 목록 항목 1.2</li></ul></li><li>상위 목록 항목 2<ul><li>하위 목록 항목 2.1</li><li>하위 목록 항목 2.2</li></ul></li></ul>
        """

        with openai.OpenAI() as client:
            changedContextDict = {}
            for corpName, doc in businessData.items():
                print(f"* CB_AI - {corpName}")
                if len(doc) >= maxTokenLength:
                    print(f"사업내용 토큰 수 초과 -> {corpName}")
                    continue

                messages = [
                    {"role": "system", "content": promptEngineering},
                    {"role": "user", "content": doc}
                ]

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1500,     # <= 16,384
                    temperature=0.8,
                )

                changedContextDict[corpName] = {
                    "businessSummary": response.choices[0].message.content
                }

        return changedContextDict