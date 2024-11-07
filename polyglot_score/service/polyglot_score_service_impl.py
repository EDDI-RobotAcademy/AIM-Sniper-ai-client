import os
import asyncio
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from polyglot_score.service.polyglot_score_service import PolyglotScoreService
from polyglot_score.repository.polyglot_score_repository_impl import PolyglotScoreRepositoryImpl
from template.utility.color_print import ColorPrinter


class PolyglotScoreServiceImpl(PolyglotScoreService):
    __instance = None
    # load lora adaptor merged model
    cacheDir = os.path.join("models", "cache")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    config = {
        "pretrained_model_name_or_path": "EleutherAI/polyglot-ko-1.3b",
        "trust_remote_code": True,
        "local_files_only": True,
        "padding_side": "left",
        "max_token_length": 1024,
    }
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

        q1, q2, q3, q4, q5, q6 = (interviewList[0], interviewList[1], interviewList[2],
                              interviewList[3], interviewList[4], interviewList[5])

        scoreModel, tokenizer = await self.__polyglotScoreRepository.loadScoreModel()

        # 각 인터뷰에 대해 비동기 작업 생성
        result1 = await self.__polyglotScoreRepository.scoreUserAnswer(q1[0], q1[1], q1[2], scoreModel, tokenizer)
        result2 = await self.__polyglotScoreRepository.scoreUserAnswer(q2[0], q2[1], q2[2], scoreModel, tokenizer)
        result3 = await self.__polyglotScoreRepository.scoreUserAnswer(q3[0], q3[1], q3[2], scoreModel, tokenizer)
        result4 = await self.__polyglotScoreRepository.scoreUserAnswer(q4[0], q4[1], q4[2], scoreModel, tokenizer)
        result5 = await self.__polyglotScoreRepository.scoreUserAnswer(q5[0], q5[1], q5[2], scoreModel, tokenizer)
        result6 = await self.__polyglotScoreRepository.scoreUserAnswer(q6[0], q6[1], q6[2], scoreModel, tokenizer)

        # 모든 비동기 작업을 병렬로 실행
        resultList = [result1, result2, result3, result4, result5, result6]
        ColorPrinter.print_important_message(f'resultList: {resultList}')
        return {'resultList': resultList}
