import os
import zipfile
from io import BytesIO

import requests
from dotenv import load_dotenv

import dart_fss as dart

load_dotenv()
dartApiKey = os.getenv('DART_API_KEY')

CORP_LIST = ['삼성전자', 'LG에너지솔루션', 'SK하이닉스', 'NAVER', '삼성바이오로직스', '삼성전자우', '카카오',
             '삼성SDI', '현대차', 'LG화학', '기아', 'POSCO홀딩스', 'KB금융', '카카오뱅크', '셀트리온',
             '신한지주', '삼성물산', '현대모비스', 'SK이노베이션', 'LG전자', '카카오페이', 'SK', '한국전력',
             '크래프톤', '하나금융지주', 'LG생활건강', 'HMM', '삼성생명', '하이브', '두산중공업', 'SK텔레콤',
             '삼성전기', 'SK바이오사이언스', 'LG', 'S-Oil', '고려아연', 'KT&G', '우리금융지주', '대한항공',
             '삼성에스디에스', '현대중공업', '엔씨소프트', '삼성화재', '아모레퍼시픽', 'KT', '포스코케미칼',
             '넷마블', 'SK아이이테크놀로지', 'LG이노텍', '기업은행']


class CorpInfo:
    SEARCH_YEAR = 20230101
    SEARCH_DOC = 'A'  # A : 정기공시, B : 주요사항보고, C : 발행공시, D : 지분공시, E : 기타공시, F : 외부감사관련, G : 펀드공시, H : 자산유동화, I : 거래소공시, J : 공정위공시

    def __init__(self):
        dart.set_api_key(api_key=dartApiKey)
        # self.__corpList = dart.get_corp_list()

    def getStockCode(self, searchCorpList):
        corpData = {}
        for name in searchCorpList:
            corp = self.__corpList.find_by_corp_name(name, exactly=True)  # 정확하게 이름으로 검색
            if isinstance(corp, list) and len(corp) > 0:  # 리스트인 경우 첫 번째 항목 선택
                corp = corp[0]
            if corp is not None and corp.stock_code:  # 주식코드가 있는지 확인
                corpData[corp.corp_name] = corp.stock_code

        return corpData

    def getCorpCode(self, searchCorpList):
        corpData = {}
        for name in searchCorpList:
            corp = self.__corpList.find_by_corp_name(name, exactly=True)  # 정확하게 이름으로 검색
            if isinstance(corp, list) and len(corp) > 0:  # 리스트인 경우 첫 번째 항목 선택
                # [TODO] 종목코드 불일치 -> 동일이름이 존재하여 발생함
                corp = corp[0]
            if corp is not None:
                corpData[corp.corp_name] = corp.corp_code

        return corpData

    def getCorpReceiptCode(self, corp_name, corpCode):
        try:
            corpReportList = dart.filings.search(
                            corp_code=corpCode,
                            bgn_de=self.SEARCH_YEAR,
                            pblntf_ty=self.SEARCH_DOC
                        ).report_list

            corpReceiptCode = next((report.rcept_no
                                     for report in corpReportList
                                     if '사업보고서' in report.report_nm), None)

            return corpReceiptCode

        except Exception as e:
            print(f"[ERROR] {corp_name} -> \n {e}")
            pass

    def getCorpDocu(self, corp_name, receipt_code):
        url = 'https://opendart.fss.or.kr/api/document.xml'
        params = {
            'crtfc_key': dartApiKey,
            'rcept_no': receipt_code}
        response = requests.get(url, params=params)

        file = BytesIO(response.content)  # 바이너리 스트림형태로 메모리에 저장
        zfile = zipfile.ZipFile(file, 'r')
        corpDocuName = sorted(zfile.namelist(), key=lambda x: len(x))[0]

        with zfile.open(corpDocuName) as f:
            content = f.read()

        return content


if __name__ == '__main__':
    dartApiKey = os.getenv('DART_API_KEY')
    if not dartApiKey:
        raise ValueError('API Key가 준비되어 있지 않습니다!')

    corpInfo = CorpInfo()
    # corpCodeDict = corpInfo.getCorpCode(CORP_LIST)
    # stockCodeDict = corpInfo.getStockCode(CORP_LIST)
    # corpCodeDict = {'삼성전자': '00126380', 'LG에너지솔루션': '01515323', 'SK하이닉스': '00164779', 'NAVER': '00266961', '삼성바이오로직스': '00877059', '카카오': '00918444', '삼성SDI': '00126362', 'LG화학': '00356361', '기아': '01664948', 'POSCO홀딩스': '00155319', 'KB금융': '00688996', '카카오뱅크': '01133217', '셀트리온': '00421045', '신한지주': '00382199', '삼성물산': '00126229', '현대모비스': '00164788', 'SK이노베이션': '00631518', 'LG전자': '00401731', '카카오페이': '01244601', 'SK': '00144155', '크래프톤': '00760971', '하나금융지주': '00547583', 'LG생활건강': '00356370', 'HMM': '00164645', '삼성생명': '00126256', '하이브': '01204056', 'SK텔레콤': '00159023', '삼성전기': '00126371', 'SK바이오사이언스': '01319899', 'LG': '00120021', 'S-Oil': '00138279', '고려아연': '00102858', '우리금융지주': '00375302', '대한항공': '00113526', '삼성에스디에스': '00126186', '엔씨소프트': '00261443', '아모레퍼시픽': '00583424', '넷마블': '00441854', 'SK아이이테크놀로지': '01386916', 'LG이노텍': '00105961', '기업은행': '00149646'}
    stockCodeDict = {'삼성전자': '005930', 'LG에너지솔루션': '373220', 'SK하이닉스': '000660', 'NAVER': '035420', '삼성바이오로직스': '207940', '삼성SDI': '006400', 'LG화학': '051910', 'POSCO홀딩스': '005490', 'KB금융': '105560', '카카오뱅크': '323410', '신한지주': '055550', '삼성물산': '000830', '현대모비스': '012330', 'SK이노베이션': '096770', 'LG전자': '066570', '카카오페이': '377300', 'SK': '003600', '크래프톤': '259960', '하나금융지주': '086790', 'LG생활건강': '051900', 'HMM': '011200', '삼성생명': '032830', '하이브': '352820', 'SK텔레콤': '017670', '삼성전기': '009150', 'SK바이오사이언스': '302440', 'LG': '003550', 'S-Oil': '010950', '고려아연': '010130', '우리금융지주': '053000', '대한항공': '003490', '삼성에스디에스': '018260', '엔씨소프트': '036570', '아모레퍼시픽': '090430', 'SK아이이테크놀로지': '361610', 'LG이노텍': '011070', '기업은행': '024110'}
    # docuDict = {'삼성전자': '20240312000736', 'LG에너지솔루션': '20240314001110', 'SK하이닉스': '20240319000684', 'NAVER': '20240318000844', '삼성바이오로직스': '20240307000835', '삼성SDI': '20240312000853', 'LG화학': '20240315000957', 'POSCO홀딩스': '20240322000986', 'KB금융': '20240326000894', '카카오뱅크': '20240320001487', '신한지주': '20240502000081', '삼성물산': None, '현대모비스': '20240319000626', 'SK이노베이션': '20240320000950', 'LG전자': '20240318000755', '카카오페이': '20240418000360', 'SK': None, '크래프톤': '20240318000420', '하나금융지주': '20240516001695', 'LG생활건강': '20240318000511', 'HMM': '20240328001188', '삼성생명': '20240612000329', '하이브': '20240322001002', 'SK텔레콤': '20240318000570', '삼성전기': '20240329002895', 'SK바이오사이언스': '20240315000914', 'LG': '20240319000703', 'S-Oil': '20240320001242', '고려아연': '20240328001400', '우리금융지주': None, '대한항공': '20240313001650', '삼성에스디에스': '20240329003204', '엔씨소프트': '20240322000989', '아모레퍼시픽': '20240307000545', 'SK아이이테크놀로지': '20240318000831', 'LG이노텍': '20240313000953', '기업은행': '20240430000630'}

    # for corp_name, corp_code in corpCodeDict.items():
    #     print(corpInfo.getCorpReceiptCode(corp_code))
    corpReceiptCodeDict = {corp_name: corpInfo.getCorpReceiptCode(corp_name, stock_code)
                            for corp_name, stock_code in stockCodeDict.items()}

    corpDocuDict = {corp_name: corpInfo.getCorpDocu(corp_name, receipt_code)
                           for corp_name, receipt_code in corpReceiptCodeDict.items()}

    print(corpDocuDict)



