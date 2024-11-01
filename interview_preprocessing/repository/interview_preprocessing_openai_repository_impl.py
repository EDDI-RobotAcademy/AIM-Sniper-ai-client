import os

import httpx
import openai
from openai import OpenAI
from dotenv import load_dotenv

from interview_preprocessing.repository.interview_preprocessing_openai_repository import \
    InterviewPreprocessingOpenAIRepository

load_dotenv()
openaiApiKey = os.getenv('OPENAI_API_KEY')
if not openaiApiKey:
    raise ValueError("API KEY가 준비되어 있지 않습니다!")

client = OpenAI(api_key=openaiApiKey)


class InterviewPreprocessingOpenAIRepositoryImpl(InterviewPreprocessingOpenAIRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generateIntent(self, question):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistance for labeling intent of question."},
                {"role": "user",
                 "content": """
                    [Question] """+question+"""
                    
                    [Note]
                    1. Only one intent is extracted.
                    2. The intent is selected from ['협업 능력', '적응력', '대처 능력', '프로젝트 경험', '자기 개발', '기술적 역량'].
                    3. '협업 능력' refers to the intent of understanding the role a person has played within an organization.
                    4. '적응력' refers to the intent of assessing how well a person can adjust to new situations.
                    5. '대처 능력' refers to the intent of understanding how a person handles crises or conflicts.
                    6. '프로젝트 경험' refers to the intent of understanding the types of projects a person has worked on, but if the question is about what role they played in the project, the intent is '협업 능력'.
                    7. '자기 개발' refers to the intent of assessing the person’s study plans, future goals, and personal learning strategies.
                    8. '기술적 역량' refers to the intent of assessing the person's abilities in programming languages, analysis, development processes, and operating systems.
                    9. The output must be one of the words from the given intents, with no additional explanation—only the word written by korean.
                    10. If there is no matching intent, output null.
                """
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def getTechKeyword(self, role):
        question = f"{role}가 알아야 할 핵심 기술 50가지를 알려줘."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 {role}야."},
                {"role": "user",
                 "content": f'{question} output은 "키워드<s>키워드<s>키워드<s>...키워드" 형식으로만 작성해줘.'
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def getTechQuestion(self, keyword, job):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 {job} 엔지니어 채용 면접을 진행 중이야. 존댓말을 사용해줘."},
                {"role": "user",
                 "content":
                     f"""{job} 엔지니어가 알아야 할 지식인 {keyword}와 관련된 기술 면접 질문 40개를 생성해줘.
                     output은 부가적인 설명이나 인덱싱 없이 "질문1<s>질문2<s>질문3<s>질문4"처럼 각 질문을 "<s>"로 분리하여 생성해줘.
                     """
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def getTechAnswer(self, question, score, job):
        if score <= 55:
            under50Prompt = '조금 잘못된 '
        elif score <=67:
            under50Prompt = '다소 애매한'
        else:
            under50Prompt = ''

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 {job} 엔지니어 채용 면접을 진행 중이야."},
                {"role": "user",
                 "content":
                     """[Question] """ + question +
                     f"""[Note]
                     1. [Question]에 대해 {score}점짜리 {under50Prompt}예상 답변과 그 예상 답변에 대한 피드백을 작성해줘.
                     2. 예상 답변은 실제로 면접자가 말하는 듯이 작성해줘.
                     3. output은 "answer:예상 답변<s>feedback:예상 답변에 대한 피드백"처럼 각각을 "<s>"로 분리하여 생성해줘.
                     """

                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def scoreAnswer(self, question, intent, answer):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 면접 대상자의 답변을 채점하는 유용한 채용 담당자야."},
                {"role": "user",
                 "content":
                    f""" [Question]{question} 
                    [Intent]{intent} 
                    [Answer]{answer}
                    [Note]
                    1. [Answer]는 면접관이 면접 대상자의 [Intent]를 파악하기 위한 [Question]에 대한 면접 대상자의 답변이야.
                    2. 면접자가 면접관의 질문에 대해 얼마나 잘 대답했는지를 1~100점으로 채점하고, 답변에 대한 feedback을 제공해줘.
                    3. 답변에 아쉬운 점이 존재한다면 점수를 낮게 주었으면 해.
                    3. output은 "score:~점<s>feedback:답변에 대한 피드백"처럼 각각을 "<s>"로 분리하여 생성해줘.
                """
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def generateQAS(self, beforeQuestion, beforeAnswer, intent, percent): # 20 30 50
        if intent == '프로젝트 경험':
            context = '"프로젝트 경험"을 파악하기 위한 질문은 지원자가 프로젝트 경험을 설명하게 하기 위한 질문이야. 따라서, 프로젝트 진행 중에 발생한 문제나 어려움, 지원자의 역할 및 기여도가 아닌, 그 프로젝트가 어떤 내용이었는지를 중점적으로 설명하도록 유도하는 질문이어야 해.'
        else:
            context = ('질문 생성시 "프로젝트 경험"을 파악하기 위한 것이 아니기 때문에 프로젝트 관련 질문을 하면 안돼.\n'
                       '예상 답변 생성시에도 프로젝트에 대한 언급은 최대한 제외하고 생성해줘.')

        if percent == 20 :
            answerText = '답변에 대한 채점 점수가 50점 미만으로 나오도록 조금 잘못된 답변을 생성해봐.'
        elif percent == 30:
            answerText = ' 답변에 대한 채점 점수가 65점 정도로 나오도록 조금 애매한 답변을 생성해봐'
        else:
            answerText = ''

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 1:1 면접을 진행하는 면접관이야."},
                {"role": "user",
                 "content":
                 f"""질문 의도: ['자기 분석', '대처 능력', '소통 능력', '프로젝트 경험', '자기 개발']
                     이전 질문: "{beforeQuestion}"
                     이전 답변: "{beforeAnswer}"
                     [Note]
                     1. 질문 의도는 면접관이 질문해야 할 질문 리스트들이야. 이중 너는 {intent}에 관한 질문을 생성할 거야.
                     2. 이전 답변은 면접자가 이전 질문에 답변한 내용이야.
                     3. 질문 생성시 면접자의 이전 답변을 참고하여 만들어줘.
                     4. 단, 이전 질문과 유사하지 않고, 면접자의 "{intent}"을 파악할 수 있도록 면접 질문을 생성하고, 그 질문에 대한 예상 답변까지도 생성하고 그 답변에 대해 0~100점으로 채점하고, 답변에 대한 피드백도 함께 알려줘.
                     5. {context}
                     6. {answerText}
                     7. 질문, 예상 답변, 피드백은 각각 3문장으로 생성해줘. 
                     8. output은 "question:너가 생성한 질문<s>answer:질문에 대한 예상 답변<s>score:~점<s>feedback:답변에 대한 피드백"처럼 각각을 "<s>"로 분리하여 생성해줘.
                  """
                 }
            ]
        )
        return response.choices[0].message.content.strip()
