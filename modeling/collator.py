import transformers
import torch
from dataclasses import dataclass
from modeling.preprocess import IGNORE_INDEX

# batch 단위를 처리하기 위한 collator function으로 배치내 데이터의 길이를 맞춰주는 padding 처리 등을 수행
@dataclass
class CustomCollator(object):
    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, instances):
        input_ids, labels = tuple([instance[key] for instance in instances] for key in ("input_ids", "labels"))
        # 이미 tensor일 거 같긴하지만, 혹시 몰라 tensor로 변환
        input_ids = [torch.tensor(piece) for piece in input_ids]
        labels = [torch.tensor(piece) for piece in labels]

        # 일부로 패딩을 left에 주기 위해 flip을 통해 뒤집기를 수행
        input_ids = torch.nn.utils.rnn.pad_sequence([i.flip(dims=[-1]) for i in input_ids], batch_first=True, padding_value=self.tokenizer.pad_token_id).flip(dims=[1])
        labels = torch.nn.utils.rnn.pad_sequence([i.flip(dims=[-1]) for i in labels], batch_first=True,
                                                            padding_value=IGNORE_INDEX).flip(dims=[1])

        return dict(input_ids=input_ids, labels=labels, attention_mask=input_ids.ne(self.tokenizer.pad_token_id),)