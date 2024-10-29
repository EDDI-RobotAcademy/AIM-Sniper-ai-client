import os
import asyncio

from polyglot_score.service.polyglot_score_service import PolyglotScoreService
from polyglot_score.repository.polyglot_score_repository_impl import PolyglotScoreRepositoryImpl
from template.utility.color_print import ColorPrinter


class PolyglotScoreServiceImpl(PolyglotScoreService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__polyglotScoreRepository = PolyglotScoreRepositoryImpl.getInstance()

            return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def scoreUserAnswer(self, *arg, **kwargs):
        cacheDir = os.path.join("models", "cache")
        if not os.path.exists(cacheDir):
            self.__polyglotScoreRepository.downloadPretrainedModel()

        interviewList = arg

        # 각 인터뷰에 대해 비동기 작업 생성
        tasks = [
            self.__polyglotScoreRepository.scoreUserAnswer(interview[0], interview[1], interview[2])
            for interview in interviewList
        ]
        # 모든 비동기 작업을 병렬로 실행
        resultList = await asyncio.gather(*tasks)
        ColorPrinter.print_important_message(f'resultList: {resultList}')
        return {'resultList': resultList}
