import itertools
import random
from abc import ABC, abstractmethod

class InterviewPreprocessingIntentRepositoryImpl(ABC):
    __instance = None
    RANDOM_SEED = 42
    ADAPTABILITY_KEYWORD = ['변화', '대처', '도전', '예기치 못한 문제', '유연성', '새로운 환경', '빠르게 적응']

    PROJECT_KEYWORD = ['프로젝트', '역할', '책임', '팀워크', '리더십', '일정 관리', '목표 설정', '협업 과정', '성과 도출']

    SELF_DEVELOPMENT_KEYWORD = ['학습', '성장', '자기 주도', '새로운 기술 학습', '트렌드 파악', '자격증',
                                '교육 참여', '개인 목표', '스킬 향상', '공부', '스터디']

    COMMUNICATION_KEYWORD = ['의견 교환', '피드백', '대화', '갈등 해결', '상사와의 소통', '팀원 간 협력',
                             '논의', '토론', '명확한 전달', '커뮤니케이션 스킬', '상사', '타 부서']

    SKILL_KEYWORD = ['프로그래밍 언어', '개발 도구', '시스템 설계', '코드 최적화', '알고리즘', '데이터베이스',
                     '성능 향상', '기술 스택', '소프트웨어 개발', '테스트 자동화', '애자일 방법론', 'CI/CD',
                     '클라우드 컴퓨팅', '버전 관리', 'API 설계', '프레임워크', '보안', '데이터 분석', '분석']

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def intentLabelingByRuleBase(self, interviewList):
        for interview in interviewList:
            question = interview['question']
            interview['rule_based_intent'] = None

            if any(keyword in question for keyword in self.COMMUNICATION_KEYWORD):
                interview['rule_based_intent'] = '의사 소통'
            elif any(keyword in question for keyword in self.ADAPTABILITY_KEYWORD):
                interview['rule_based_intent'] = '적응력'
            elif any(keyword in question for keyword in self.PROJECT_KEYWORD):
                if all(keyword not in question for keyword in ['게임', '창의성', '산사태']):
                    interview['rule_based_intent'] = '프로젝트 경험'
            elif any(keyword in question for keyword in self.SELF_DEVELOPMENT_KEYWORD):
                interview['rule_based_intent'] = '자기 개발'
            elif any(keyword in question for keyword in self.SKILL_KEYWORD):
                interview['rule_based_intent'] = '기술적 역량'

        return interviewList

    def countLabeledInterview(self, labeledInterviewList):
        labelCountDict = {
            '적응력': 0,
            '프로젝트 경험': 0,
            '자기 개발': 0,
            '의사 소통': 0,
            '기술적 역량': 0,
            'None': 0
        }
        for interview in labeledInterviewList:
            intent = interview['rule_based_intent']

            if intent in labelCountDict:
                labelCountDict[intent] += 1
            else:
                labelCountDict['None'] += 1

        return labelCountDict

    def splitInterviewListByIntentIsNone(self, labeledInterviewList):
        interviewListIntentIsNotNone = []
        interviewListIntentIsNone = []
        for interview in labeledInterviewList:
            if interview['rule_based_intent'] is not None:
                interviewListIntentIsNotNone.append({
                    'question': interview['question'],
                    'rule_based_intent': interview['rule_based_intent']
                })
            else:
                interviewListIntentIsNone.append({
                    'question': interview['question'],
                    'rule_based_intent': interview['rule_based_intent']
                })

        return interviewListIntentIsNone, interviewListIntentIsNotNone

    def sampleRandomQuestionListIntentIsNone(self, interviewListIntentIsNone, sampleSize):
        random.seed(self.RANDOM_SEED)
        sampledInterviewListIntentIsNone = random.sample(interviewListIntentIsNone, sampleSize)

        return sampledInterviewListIntentIsNone

    def sampleRandomQuestionListByIntent(self, labeledInterviewList, sampleSize):
        random.seed(self.RANDOM_SEED)

        intentDict = {
            '적응력': [],
            '프로젝트 경험': [],
            '자기 개발': [],
            '의사 소통': [],
            '기술적 역량': []
        }

        # 각 의도별로 질문을 분류
        for interview in labeledInterviewList:
            intent = interview['rule_based_intent']
            if intent in intentDict:
                intentDict[intent].append({
                    "question": interview['question'],
                    "rule_based_intent": interview['rule_based_intent']
                })

        # 각 의도 별로 랜덤 샘플링
        sampledQuestionList = []
        for intent, questionList in intentDict.items():
            sampledQuestionList.append(random.sample(questionList, min(sampleSize, len(questionList))))

        return sampledQuestionList

    def flattenDimensionOfList(self, doublyLinkedList):
        flattenedList = list(itertools.chain.from_iterable(doublyLinkedList))

        return flattenedList
