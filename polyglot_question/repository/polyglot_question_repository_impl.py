from polyglot_question.repository.polyglot_question_repository import PolyglotQuestionRepository

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel

import os

class PolyglotQuestionRepositoryImpl(PolyglotQuestionRepository):
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

    def generateQuestion(self, userAnswer, nextIntent):

        model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.config['pretrained_model_name_or_path'],
            trust_remote_code=self.config['trust_remote_code'],
            cache_dir=self.cacheDir,
            local_files_only=self.config['local_files_only'])

        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=self.config['pretrained_model_name_or_path'],
                                                  trust_remote_code=self.config['trust_remote_code'],
                                                  cache_dir=self.cacheDir,
                                                  local_files_only=self.config['local_files_only'],
                                                  padding_side=self.config['padding_side'])

        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
        tokenizer.model_max_length = self.config['max_token_length']



        loraAdapterInterviewName = "polyglot-ko-1.3b/interview"
        loraAdapterInterviewPath = os.path.join("models", loraAdapterInterviewName, "final")

        prompt = (
            "당신은 면접관입니다. 다음 명령에 따라 적절한 질문을 수행하세요.\n"
            "화자의 응답 기록을 참고하여 주제에 관련된 적절한 질문을 생성하세요.\n"
            "### 주제:\n{intent}\n\n### 화자의 응답 기록:\n{answer}\n\n### 질문 :\n"
        )

        beforeAnswer = userAnswer
        source = prompt.format_map(dict(answer=beforeAnswer,
                                        intent=nextIntent))

        input = tokenizer([source], return_tensors="pt", return_token_type_ids=False).to(self.device)
        inputLength = len(source)

        interviewModel = PeftModel.from_pretrained(model, loraAdapterInterviewPath)
        interviewModel = interviewModel.merge_and_unload()

        interviewModel.eval()
        interviewModel.to(self.device)

        with torch.no_grad():
            output = interviewModel.generate(**input, max_new_tokens=200)
            output = tokenizer.decode(output[0], skip_special_tokens=True)
            output = output[inputLength:]

        nextQuestion = output

        return {"nextQuestion": nextQuestion}