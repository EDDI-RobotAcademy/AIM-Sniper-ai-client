import logging
from torch.utils.data import Dataset
from modeling.preprocess import preprocess

# Dataset 객체를 상속한 클래스 - 모델의 입출력을 가져오기 위한 단위? 로 생각하면 편할듯
class CustomDataset(Dataset):
    def __init__(self, examples, tokenizer):
        self.tokenizer = tokenizer

        sources = [example['source'] for example in examples]
        targets = [f"{example['target']}{tokenizer.eos_token}" for example in examples]

        logging.warning(msg="tokenizing...")
        data_dict = preprocess(sources=sources, targets=targets, tokenizer=tokenizer)
        logging.warning(msg="tokenizing finished")

        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]

    def __len__(self):
        return len(self.input_ids)

    def naive__getitem__(self, i):
        return dict(input_ids=self.input_ids[i], labels=self.labels[i])

    def __getitem__(self, idx):
        return dict(input_ids=self.input_ids[idx], labels=self.labels[idx])