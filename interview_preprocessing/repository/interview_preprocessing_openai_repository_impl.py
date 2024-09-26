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