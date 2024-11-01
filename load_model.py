import os

from transformers import AutoModelForCausalLM, AutoTokenizer

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