import os
import asyncio
import torch
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
        model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.config['pretrained_model_name_or_path'],
            trust_remote_code=self.config['trust_remote_code'],
            cache_dir=self.cacheDir,
            local_files_only=self.config['local_files_only'])

        tokenizer = (AutoTokenizer.
                     from_pretrained(pretrained_model_name_or_path=self.config['pretrained_model_name_or_path'],
                                     trust_remote_code=self.config['trust_remote_code'],
                                     cache_dir=self.cacheDir,
                                     local_files_only=self.config['local_files_only'],
                                     padding_side=self.config['padding_side']))

        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
        tokenizer.model_max_length = self.config['max_token_length']

        # 각 인터뷰에 대해 비동기 작업 생성
        tasks = [
            self.__polyglotScoreRepository.scoreUserAnswer(interview[0], interview[1], interview[2], model, tokenizer)
            for interview in interviewList
        ]
        # 모든 비동기 작업을 병렬로 실행
        resultList = await asyncio.gather(*tasks)
        ColorPrinter.print_important_message(f'resultList: {resultList}')
        return {'resultList': resultList}
