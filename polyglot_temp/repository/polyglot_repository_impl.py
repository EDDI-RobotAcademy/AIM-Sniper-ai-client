from polyglot_temp.repository.polyglot_repository import PolyglotRepository

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel

import os

class PolyglotRepositoryImpl(PolyglotRepository):
    __instance = None

    # load lora adaptor merged model
    cacheDir = os.path.join("models", "cache")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loraAdapterInterviewName = "polyglot-ko-1.3b/test_20_100"
    loraAdapterScoreName = "polyglot-ko-1.3b/score"

    loraAdapterInterviewPath = os.path.join("models", loraAdapterInterviewName, "checkpoint-100")
    loraAdapterScorePath = os.path.join("models", loraAdapterScoreName, "checkpoint-100")

    config = {
        "pretrained_model_name_or_path": "EleutherAI/polyglot-ko-1.3b",
        "trust_remote_code": True,
        "local_files_only": True,
        "padding_side": "left",
        "max_token_length": 1024,
    }

    # base model and tokenizer load
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=config['pretrained_model_name_or_path'],
        trust_remote_code=config['trust_remote_code'],
        cache_dir=cacheDir,
        local_files_only=config['local_files_only'])

    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=config['pretrained_model_name_or_path'],
                                              trust_remote_code=config['trust_remote_code'],
                                              cache_dir=cacheDir,
                                              local_files_only=config['local_files_only'],
                                              padding_side=config['padding_side'])

    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.model_max_length = config['max_token_length']

    # lora adapter 변화랑 model parameter에 병합 - merge_and_unload() 안해도 되지만, 그러면 추론 속도가 느림
    interviewModel = PeftModel.from_pretrained(model, loraAdapterInterviewPath)
    interviewModel = interviewModel.merge_and_unload()

    interviewModel.eval()
    interviewModel.to(device)

    # lora adapter 변화랑 model parameter에 병합 - merge_and_unload() 안해도 되지만, 그러면 추론 속도가 느림
    scoreModel = PeftModel.from_pretrained(model, loraAdapterScorePath)
    scoreModel = scoreModel.merge_and_unload()

    scoreModel.eval()
    scoreModel.to(device)

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
        prompt = (
            "당신은 면접관입니다. 다음 명령에 따라 적절한 질문을 수행하세요.\n"
            "화자의 응답 기록을 참고하여 주제에 관련된 적절한 질문을 생성하세요.\n"
            "### 주제:\n{intent}\n\n### 화자의 응답 기록:\n{answer}\n\n### 질문 :\n"
        )

        beforeAnswer = userAnswer
        source = prompt.format_map(dict(answer=beforeAnswer,
                                        intent=nextIntent))

        input = self.tokenizer([source], return_tensors="pt", return_token_type_ids=False).to(self.device)
        inputLength = len(source)
        with torch.no_grad():
            output = self.interviewModel.generate(**input, max_new_tokens=200)
            output = self.tokenizer.decode(output[0], skip_special_tokens=True)
            output = output[inputLength:]

        nextQuestion = output

        return {"nextQuestion": nextQuestion}

    def scoreUserAnswer(self, question, userAnswer, intent):
        prompt = (
            "당신은 면접 대상자의 답변을 채점하는 채용 담당자입니다.\n"
            "Question은 당신이 면접 대상자로부터 Intent를 파악하기 위한 질문입니다. "
            "면접 대상자의 답변은 Question에 대한 답변입니다.\n"
            "면접 대상자가 얼마나 Question에 잘 대답했는지를 1~100점 사이에서 평가해주세요.\n"
            "면접 대상자의 답변에 대한 feedback과 당신이 100점이라고 생각하는 Answer를 제공해주세요.\n"
            "Question: {question}\n면접 대상자의 답변: {answer}\nIntent: {intent}\noutput:"
        )
        source = prompt.format_map(dict(question=question, intent=intent, answer=userAnswer))
        input = self.tokenizer([source], return_tensors="pt", return_token_type_ids=False).to(self.device)
        inputLength = len(source)
        with torch.no_grad():
            output = self.interviewModel.generate(**input, max_new_tokens=200)
            output = self.tokenizer.decode(output[0], skip_special_tokens=True)
            output = output[inputLength:]
            score_result = output.split('<s>')

        return {"score result": score_result}
