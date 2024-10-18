from polyglot_temp.repository.polyglot_repository import PolyglotRepository

import transformers
from transformers import TrainingArguments, Trainer, AutoTokenizer, AutoModelForCausalLM
import torch
from torch.utils.data import Dataset
from peft import LoraConfig, get_peft_model, PeftModel
from dataclasses import dataclass
import json, os, random, logging, math, copy
import numpy as np

class PolyglotRepositoryImpl(PolyglotRepository):
    __instance = None

    # load lora adaptor merged model
    cacheDir = os.path.join("models", "cache")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loraAdapterName = "polyglot-ko-1.3b/test_20_100"

    loraAdapterPath = os.path.join("models", loraAdapterName, "checkpoint-100")

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
    model = PeftModel.from_pretrained(model, loraAdapterPath)
    model = model.merge_and_unload()

    model.eval()
    model.to(device)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generateQuestion(self, userAnswer, nextIntent):
        prompt = (
            "당신은 면접관입니다. 다음 명령에 따라 적절한 질문을 수행하세요.\n"
            "화자의 응답 기록을 참고하여 주제에 관련된 적절한 질문을 생성하세요.\n"
            "### 주제:\n{intent}\n\n### 화자의 응답 기록:\n{answer}\n\n"
        )

        beforeAnswer = userAnswer
        source = prompt.format_map(dict(answer=beforeAnswer,
                                        intent=nextIntent))

        input = self.tokenizer([source], return_tensors="pt", return_token_type_ids=False).to(self.device)
        inputLength = len(source)
        with torch.no_grad():
            output = self.model.generate(**input, max_new_tokens=200)
            output = self.tokenizer.decode(output[0], skip_special_tokens=True)
            output = output[inputLength:]

        nextQuestion = output

        return {"nextQuestion": nextQuestion}
