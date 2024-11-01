from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel
import os

from polyglot_score.repository.polyglot_score_repository import PolyglotScoreRepository


class PolyglotScoreRepositoryImpl(PolyglotScoreRepository):
    __instance = None

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

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def downloadPretrainedModel(self):
        cacheDir = os.path.join("models", "cache")  # 원하는 경로로 변경 가능

        # 모델 다운로드
        model = AutoModelForCausalLM.from_pretrained(
            "EleutherAI/polyglot-ko-1.3b",
            cache_dir=cacheDir,
            trust_remote_code=True
        )

        # 토크나이저 다운로드
        tokenizer = AutoTokenizer.from_pretrained(
            "EleutherAI/polyglot-ko-1.3b",
            cache_dir=cacheDir,
            trust_remote_code=True
        )

    async def loadScoreModel(self):
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

        loraAdapterScoreName = "polyglot-ko-1.3b/score"
        loraAdapterScorePath = os.path.join("models", loraAdapterScoreName, "r512-epoch100")

        scoreModel = PeftModel.from_pretrained(model, loraAdapterScorePath)
        scoreModel = scoreModel.merge_and_unload()

        scoreModel.eval()
        scoreModel.to(self.device)

        return scoreModel, tokenizer

    async def scoreUserAnswer(self, question, userAnswer, intent, scoreModel, tokenizer):
        prompt = (
            "당신은 면접 대상자의 답변을 채점하는 면접관입니다.\n"
            "면접 질문은 당신이 면접 대상자로부터 질문 의도인 '{intent}'에 대한 정보를 파악하기 위한 질문입니다. "
            "면접 대상자의 답변은 면접 질문에 대한 답변입니다.\n"
            "면접 대상자가 면접관의 질문에 대해 얼마나 잘 대답했는지를 1~100점으로 채점하고, 답변에 대한 feedback을 제공해주세요.\n"
            "면접 질문: {question}\n면접 대상자의 답변: {answer}\n질문 의도: {intent}\noutput:"
        )

        source = prompt.format_map(dict(question=question, intent=intent, answer=userAnswer))
        input = tokenizer([source], return_tensors="pt", return_token_type_ids=False).to(self.device)
        inputLength = len(source)

        with torch.no_grad():
            output = scoreModel.generate(**input, max_new_tokens=512)
            output = tokenizer.decode(output[0], skip_special_tokens=True)
            output = output[inputLength:]
        result = output

        return result