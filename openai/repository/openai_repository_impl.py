import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
import openai
from openai.repository.openai_repository import OpenAIRepository

load_dotenv()

openaiApiKey = os.getenv('OPENAI_API_KEY')
if not openaiApiKey:
    raise ValueError('API Key가 준비되어 있지 않습니다!')

class OpenAIRepositoryImpl(OpenAIRepository):
    headers = {
        'Authorization': f'Bearer {openaiApiKey}',
        'Content-Type': 'application/json'
    }

    OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__openaiApiTestRepositoryImpl = OpenAIRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateQuestion(self, userInput):
        maxTokenLength = 128000
        promptEngineering = f"""
                사용자 입력 메시지의 내용은 면접 질문에 대한 답변이다. 너는 면접을 진행하는 면접관이다.
                모든 <조건1>에 맞춰, <구조1>과 같은 구조로 면접 질문을 생성하고
                면접 결과를 <조건2>에 맞춰 <구조2>와 같은 구조로 면접 결과를 생성해라.

                <조건1>
                1. 면접 시작 이라는 단어가 나오면 면접을 시작할 것
                2. 사용자 면접 질문에 대한 답변을 바탕으로 다음 질문을 말할 것
                3. 1500 token 내로 작성을 마무리 할 것.
                4. 질문은 5개를 할 것
                5. 질문 5개가 끝나면 면접 결과를 생성할 것

                <구조2>
                1. 면접 질문이 너무 길지 않을 것(2문장 이내)
                2. 면접 분위기 처럼 공식 적인 말투를 사용할 것
                3. 문장과 문장 사이에는 띄어 쓰기를 추가할 것
                
                <조건2>
                1. 면접이 끝나면 면접에 대한 평가를 생성하여 결과를 알려줄 것
                2. 면접에 대한 평가는 평가 조건에 따라 1~100점으로 평가할 것
                    2-1. 면접 질문의 의도를 잘 파악했는가?
                    2-2. 성실하게 대답 했는가?
                
                <구조2>
                1. 면접 결과를 HTML 형식으로 표현할 것
                2. 면접 질문과 답변에 대한 구분은 질문은 <b>태그를 사용 하고 답변은 사용 하지 않을 것
                3. 보고서처럼 전체 결과를 한 페이지로 표시할 것
        """

        messages = [
            {"role": "system", "content": promptEngineering},
            {"role": "user", "content": userInput}
        ]

        with openai.OpenAI() as client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1500,  # <= 16,384
                    temperature=0.8,
                )

                return {"answer":response.json()['choices'][0]['message']['content'].strip()}

            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {str(e)}")
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Text: {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail=f"HTTP Error: {e}")

            except (httpx.RequestError, ValueError) as e:
                print(f"Request Error: {e}")
                raise HTTPException(status_code=500, detail=f"Request Error: {e}")
