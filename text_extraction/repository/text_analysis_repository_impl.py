import re
import pandas as pd
import json


class TextAnalysisImpl:
    __instance = None

    LABEL_KEYWORDS = {
        '플랫폼': {
            'keywords': ['플랫폼'],
            'exclude': []
        },
        '빅데이터': {
            'keywords': ['빅데이터', '머신러닝', '딥러닝'],
            'exclude': []
        },
        '정보보안': {
            'keywords': ['정보보안'],
            'exclude': []
        },
        '소프트웨어': {
            'keywords': ['소프트웨어'],
            'exclude': ['반도체']
        },
        '하드웨어': {
            'keywords': ['제조 서비스', '하드웨어'],
            'exclude': ['자동차', 'AI']
        },
        '클라우드': {
            'keywords': ['클라우드'],
            'exclude': ['슈퍼마켓']
        },
        '제조': {
            'keywords': ['제조'],
            'exclude': ['백화점', '오뚜기', '개인정보']
        },
        '컨설팅': {
            'keywords': ['솔루션 제공'],
            'exclude': []
        },
        '헬스케어': {
            'keywords': ['헬스케어'],
            'exclude': ['카카오']
        },
        '게임': {
            'keywords': ['게임'],
            'exclude': ['웹툰', '신세계']
        },
        '메타버스': {
            'keywords': ['메타버스'],
            'exclude': []
        },
        'IT 인프라': {
            'keywords': ['IT 인프라', '정보시스템'],
            'exclude': []
        },
        '반도체': {
            'keywords': ['반도체'],
            'exclude': []
        },
        '화학': {
            'keywords': ['화학'],
            'exclude': []
        },
        '의약품': {
            'keywords': ['의약품'],
            'exclude': []
        },
        '인공지능': {
            'keywords': ['인공지능'],
            'exclude': ['광고', '세일즈']
        },
        '디스플레이': {
            'keywords': ['디스플레이'],
            'exclude': ['광고']
        },
        '광고': {
            'keywords': ['광고'],
            'exclude': []
        },
        '영상': {
            'keywords': ['영상'],
            'exclude': ['광고']
        },
        '네트워크': {
            'keywords': ['네트워크'],
            'exclude': ['전자부품', '항체의약품', '부품 제조', '방사선', '핵융합']
        },
        '식품': {
            'keywords': ['식품'],
            'exclude': ['건강기능식품']
        },
        '쇼핑': {
            'keywords': ['쇼핑'],
            'exclude': ['IT']
        },
        '배터리': {
            'keywords': ['배터리'],
            'exclude': []
        },
        '건설': {
            'keywords': ['건설'],
            'exclude': ['마트']
        },
        '호텔': {
            'keywords': ['호텔'],
            'exclude': []
        },
        '금융': {
            'keywords': ['금융'],
            'exclude': ['반도체', '음반', '금융권', '건강기능식품']
        }
    }

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def load_data(self, file_path):
        """JSON 파일에서 데이터를 불러옴"""
        with open(file_path, encoding='utf-8-sig') as json_file:
            data = json.load(json_file)

        # 회사 이름(key)과 'businessSummary'를 추출
        summaries = [{'companyName': company,
                      'businessSummary': details.get('businessSummary', '')}
                     for company, details in data.items()]
        return summaries

    def clean_text(self, data):
        """텍스트 클리닝 작업"""
        cleaned_data = [re.sub(r'(\*\*|\*|-|\\n|\n)', '', str(text)).strip() for text in data]
        return cleaned_data

    def label_intent(self, text):
        """주어진 텍스트에 대해 규칙 기반으로 다중 라벨을 반환"""
        labels = []
        for label, rules in self.LABEL_KEYWORDS.items():
            keywords = rules['keywords']
            exclude = rules['exclude']

            if any(keyword in text for keyword in keywords) and not any(exclusion in text for exclusion in exclude):
                labels.append(label)
        return labels if labels else ["기타"]

    def intent_labeling_by_rule_base(self, summaries):
        """주어진 데이터 리스트에 대해 intent 라벨링"""
        labeled_count = 0
        unlabeled_count = 0

        for summary in summaries:
            labels = self.label_intent(summary['businessSummary'])
            summary['rule_based_intent'] = labels
            if labels and "기타" not in labels:
                labeled_count += 1
            else:
                unlabeled_count += 1

        return summaries, labeled_count, unlabeled_count

    def save_to_csv(self, labeled_data, output_file='labeled_output_with_company.csv'):
        """라벨링 결과를 CSV 파일로 저장"""
        df = pd.DataFrame(labeled_data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"라벨링 결과가 {output_file} 파일로 저장되었습니다.")

    def run_analysis(self, file_path):
        """전체 분석 흐름을 한 번에 처리"""
        data = self.load_data(file_path)
        if data:
            cleaned_data = [
                {'companyName': d['companyName'], 'businessSummary': self.clean_text([d['businessSummary']])[0]} for d
                in data]
            labeled_data, labeled_count, unlabeled_count = self.intent_labeling_by_rule_base(cleaned_data)
            return labeled_data, labeled_count, unlabeled_count
        else:
            return None, 0, 0
