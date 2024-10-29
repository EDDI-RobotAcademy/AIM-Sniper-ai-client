import os
import asyncio
from polyglot_temp.repository.polyglot_repository_impl import PolyglotRepositoryImpl
from polyglot_temp.service.polyglot_service import PolyglotService


class PolyglotServiceImpl(PolyglotService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__polyglotRepository = PolyglotRepositoryImpl.getInstance()

            return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateNextQuestion(self, *arg, **kwargs):
        cacheDir = os.path.join("models", "cache")
        if not os.path.exists(cacheDir):
            self.__polyglotRepository.downloadPretrainedModel()

        userAnswer = arg[0]
        nextIntent = arg[1]

        return self.__polyglotRepository.generateQuestion(userAnswer, nextIntent)

    async def scoreUserAnswer(self, *arg, **kwargs):
        cacheDir = os.path.join("models", "cache")
        if not os.path.exists(cacheDir):
            self.__polyglotRepository.downloadPretrainedModel()

        interviewList = arg
        print("interviewList: ", interviewList)

        resultList = []

        # 각 인터뷰에 대해 비동기 작업 생성
        tasks = [
            self.__polyglotRepository.scoreUserAnswer(interview[0], interview[1], interview[2])
            for interview in interviewList
        ]

        # 모든 비동기 작업을 병렬로 실행
        results = await asyncio.gather(*tasks)
        print('results: ', results)
        # resultList = []
        # for interview in interviewList:
        #     question, userAnswer, intent = interview[0], interview[1], interview[2]
        #     print(f"question: {question}\nuserAnswer: {userAnswer}\nintent: {intent}")
        #     result = await self.__polyglotRepository.scoreUserAnswer(question, userAnswer, intent)
        #     resultList.append(result)

        return {'resultList': results}
