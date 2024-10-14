from transformers import TrainingArguments, Trainer, AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
import os

from modeling.collator import CustomCollator
from modeling.dataset import CustomDataset
from modeling.preprocess import load_dataset, data_transform


# training Args 객체를 반환하는 함수 - 학습에 사용되는 파라미터
def get_training_args(args):
    training_args = TrainingArguments(
        output_dir=args['output_dir'],
        evaluation_strategy="no",
        learning_rate=args["learning_rate"],
        weight_decay=args["weight_decay"],
        push_to_hub=False,
        do_train=True,
        num_train_epochs=args['num_epochs'],
        per_device_train_batch_size=args["batch_size"],
        logging_steps=args["logging_steps"],
        gradient_accumulation_steps=args["accumulation_steps"],
        save_strategy="steps",
        save_steps=args["save_steps"],
        warmup_ratio=0.03,
        lr_scheduler_type='cosine',
        max_grad_norm=1.0,
        fp16=False,
        report_to=args["report_to"],
        run_name=args["run_name"],
    )

    return training_args

def get_lora_args(args):
    peft_config = LoraConfig(
        lora_alpha=args['lora_r'] * 2,
        lora_dropout=args['lora_dropout'],
        r=args['lora_r'],
        bias=args['bias'],
        task_type="CAUSAL_LM"
    )

    return peft_config

def training(config):
    # model and tokenizer load
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=config['pretrained_model_name_or_path'],
        trust_remote_code=config['trust_remote_code'],
        cache_dir=config['cache_dir'],
        local_files_only=config['local_files_only'])

    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=config['pretrained_model_name_or_path'],
                                              trust_remote_code=config['trust_remote_code'],
                                              cache_dir=config['cache_dir'],
                                              local_files_only=config['local_files_only'],
                                              padding_side=config['padding_side'])

    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.model_max_length = config['max_token_length']

    # LoRA 적용
    lora_config = get_lora_args(config['lora_args'])
    model = get_peft_model(model, lora_config)

    # org dataset load
    train_dataset = load_dataset(config['train_data_path'])
    train_dataset = data_transform(train_dataset)

    # prepare train dataset
    train_dataset = CustomDataset(examples=train_dataset, tokenizer=tokenizer)
    data_collator = CustomCollator(tokenizer=tokenizer)

    # prepare training model
    training_args = get_training_args(config['training_args'])

    trainer = Trainer(model=model,
                      tokenizer=tokenizer,
                      args=training_args,
                      train_dataset=train_dataset,
                      data_collator=data_collator)

    # 학습 수행
    trainer.train()

    # 맨 마지막 - 학습 종료 이후 저장하는 부분
    trainer.save_state()
    trainer.save_model(output_dir=os.path.join(config['output_dir'], "final"))

