import os, json, copy, math

IGNORE_INDEX = -100

def load_dataset(directory_path):
    filenames = os.listdir(directory_path)
    datas = []
    for filename in filenames:
        with open(os.path.join(directory_path, filename), 'r', encoding='utf8') as f:
            datas.append(json.loads(f.read()))

    print(f"loading finished : {len(datas)} datas")
    return datas

def data_transform(datas):
    prompt = (
        "당신은 면접관입니다. 다음 명령에 따라 적절한 질문을 수행하세요.\n"
        "화자의 응답 기록을 참고하여 주제에 관련된 적절한 질문을 생성하세요.\n"
        "### 주제:\n{intent}\n\n### 화자의 응답 기록:\n{answer}\n\n### 질문 :\n"
    )

    dataset = []
    for session in datas:
        before_answer = None

        for turn in session:
            if before_answer is None:
                before_answer = turn['answer']
                continue
            else:
                source = prompt.format_map(dict(
                    answer=before_answer,
                    intent=turn['rule_based_intent']
                ))
                target = turn['question']
                dataset.append(dict(
                    source=source,
                    target=target
                ))

                before_answer = turn['answer']

    print(f"total data samples : {len(dataset)}")

    return dataset

# tokenizing, label설정 등과 같은 전처리를 수행하는 함수
def preprocess(sources, targets, tokenizer):
    # 입력 및 출력을 하나로 연결해서 example을 생성
    examples = [s + t for s, t in zip(sources, targets)]

    # 토크나이징 수행
    input_ids = tokenizer(text=examples, padding=False, return_attention_mask=False, return_length=False,
                          max_length=tokenizer.model_max_length, truncation=True, verbose=False)["input_ids"]
    # 입력 부분을 복사하여 target으로 사용할 label 생성
    labels = copy.deepcopy(input_ids)

    # 오류 체크
    for pieces in input_ids:
        assert not any([math.isnan(piece) or math.isinf(piece) for piece in pieces])

    # 입력을 토크나이징하여, 입력부분의 길이를 계산
    source_lens = tokenizer(text=sources, padding=False, return_attention_mask=False, return_length=True,
                            max_length=tokenizer.model_max_length, truncation=True, verbose=False)["length"]

    # label의 입력 부분에 대해 loss계산을 하지 않도록 IGNORE_INDEX로 설정
    for example_index in range(len(examples)):
        for index in range(source_lens[example_index]):
            labels[example_index][index] = IGNORE_INDEX

    return dict(input_ids=input_ids, labels=labels)



