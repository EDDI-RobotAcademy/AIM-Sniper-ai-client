import os
import numpy as np
import random
import torch
import wandb


def login_to_wandb(project_name):
    wandb.login()
    os.environ['WANDB_PROJECT'] = project_name  # wandb project 이름 설정

# random seed 설정 함수
def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if use multi-GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)

def set_config(model_name, cache_dir, input_dir, output_dir):
    config = {
        "training_args": {
            "output_dir": output_dir,
            "learning_rate": 2e-5,
            "weight_decay": 0.001,
            "batch_size": 8,
            "accumulation_steps": 32,
            "logging_steps": 1,
            "save_steps": 100,
            "num_epochs": 20,
            "report_to": "wandb",
            "run_name": "session_10000"
        },
        "lora_args": {
            "lora_r": 128,
            "lora_dropout": 0.05,
            "bias": "none"
        },

        "pretrained_model_name_or_path": model_name,
        "trust_remote_code": True,
        "cache_dir": cache_dir,
        "local_files_only": False,
        "padding_side": "left",
        "max_token_length": 1024,

        "train_data_path": input_dir,
        "output_dir": output_dir

    }
    return config