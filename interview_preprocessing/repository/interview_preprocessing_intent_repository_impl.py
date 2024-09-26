import itertools
import random
from abc import ABC, abstractmethod

class InterviewPreprocessingIntentRepositoryImpl(ABC):
    __instance = None
    RANDOM_SEED = 42
    OVERCOME_KEYWORD = ['상사', '대처', '어떻게 해결', '예기치', '문제', '예상', '다르', '노하우', '극복', '동료',
                        '갈등', '타 부서와', '다른 부서와', '분쟁' '위기', '산사태']

    ADAPTABILITY_KEYWORD = ['변화', '새로운 환경', '적응', '부서에 배치', '다른 부서에']

    COWORKING_KEYWORD = ['어떤 사람', '조직 내', '어떤 역할', '어떠한 역할', '포지션', '무슨 역할', '다를 경우', '사교성']

    PROJECT_KEYWORD = ['프로젝트', '책임', '팀워크', '리더십', '일정 관리', '목표 설정', '협업 과정', '성과 도출']

    SELF_DEVELOPMENT_KEYWORD = ['학습', '성장', '자기 주도', '새로운 기술', '트렌드 파악', '자격증',
                                '교육 참여', '개인 목표', '스킬 향상', '공부', '스터디']

    SKILL_KEYWORD = ['새로운 언어', '프로그래밍 언어', '개발 도구', '시스템 설계', '코드 최적화', '알고리즘', '데이터베이스',
                     '성능 향상', '기술 스택', '소프트웨어 개발', '테스트 자동화', '애자일 방법론', 'CI/CD',
                     '클라우드 컴퓨팅', '버전 관리', 'API 설계', '프레임워크', '보안', '커널 분석', '데이터 분석', '분석 기법']

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

            if any(keyword in question for keyword in self.COWORKING_KEYWORD):
                if all(keyword not in question for keyword in ['캐릭터', '게임', '창의성', '산사태', '존경하는 인물']):
                    interview['rule_based_intent'] = '협업 능력'
            elif any(keyword in question for keyword in self.OVERCOME_KEYWORD):
                interview['rule_based_intent'] = '대처 능력'
            elif any(keyword in question for keyword in self.ADAPTABILITY_KEYWORD):
                if all(keyword not in question for keyword in ['교번 근무', '배치', '물류를 둘러싼 환경', '최근 물류 산업']):
                    interview['rule_based_intent'] = '적응력'
            elif any(keyword in question for keyword in self.PROJECT_KEYWORD):
                if all(keyword not in question for keyword in ['창의성과 팀워크', '산사태', '역할', '경영을 책임', '아이디어', '기법']):
                    interview['rule_based_intent'] = '프로젝트 경험'
            elif any(keyword in question for keyword in self.SELF_DEVELOPMENT_KEYWORD):
                interview['rule_based_intent'] = '자기 개발'
            elif any(keyword in question for keyword in self.SKILL_KEYWORD):
                if all(keyword not in question for keyword in ['이슈']):
                    interview['rule_based_intent'] = '기술적 역량'

        return interviewList

    def countLabeledInterview(self, labeledInterviewList):
        labelCountDict = {
            '협업 능력': 0,
            '대처 능력': 0,
            '적응력': 0,
            '프로젝트 경험': 0,
            '자기 개발': 0,
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
                    'answer': interview['answer'],
                    'summary': interview['summary'],
                    'occupation': interview['occupation'],
                    'experience': interview['experience'],
                    'rule_based_intent': interview['rule_based_intent']
                })
            else:
                interviewListIntentIsNone.append({
                    'question': interview['question'],
                    'answer': interview['answer'],
                    'summary': interview['summary'],
                    'occupation': interview['occupation'],
                    'experience': interview['experience'],
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
            '협업 능력': [],
            '대처 능력': [],
            '적응력': [],
            '프로젝트 경험': [],
            '자기 개발': [],
            '기술적 역량': []
        }

        # 각 의도별로 질문을 분류
        for interview in labeledInterviewList:
            intent = interview['rule_based_intent']
            if intent in intentDict:
                intentDict[intent].append({
                    "question": interview['question'],
                    "rule_based_intent": interview['rule_based_intent'],
                    'answer': interview['answer'],
                    'summary': interview['summary'],
                    'occupation': interview['occupation'],
                    'experience': interview['experience']
                })

        # 각 의도 별로 랜덤 샘플링
        sampledQuestionList = []
        for intent, questionList in intentDict.items():
            sampledQuestionList.append(random.sample(questionList, min(sampleSize, len(questionList))))

        return sampledQuestionList

    def flattenDimensionOfList(self, doublyLinkedList):
        flattenedList = list(itertools.chain.from_iterable(doublyLinkedList))

        return flattenedList