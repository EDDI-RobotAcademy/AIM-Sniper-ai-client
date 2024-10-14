import os
from modeling.train import training
from modeling.config import login_to_wandb, set_seed, set_config

if __name__ == '__main__':
    root_dir = os.path.abspath("../drive/MyDrive/LoRA_tuning")
    input_dir = os.path.join(root_dir, "inputs")

    # 반드시 경로 알잘딱 바꿔주기
    model_name = "EleutherAI/polyglot-ko-1.3b" # beomi/llama-2-ko-7b , EleutherAI/polyglot-ko-1.3b
    output_dir = os.path.join(root_dir, "outputs", "이름(interview or score)", model_name.split("/")[1], "test")
    os.makedirs(output_dir, exist_ok=True)

    cache_dir = os.path.join(root_dir, 'cache')
    login_to_wandb('TEST')
    set_seed(seed=42)

    config = set_config(model_name, cache_dir, input_dir, output_dir)

    training(config)