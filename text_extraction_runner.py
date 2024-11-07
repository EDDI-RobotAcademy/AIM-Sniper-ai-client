from text_extraction.service.text_extraction_service_impl import TextExtractionServiceImpl

textExtractionService = TextExtractionServiceImpl()

def Dataload():
    summary = textExtractionService.loadAndPreprocessing()
    return summary  # 요약 데이터를 반환

def preprocess(summary):
    tagged_word_counts = textExtractionService.wordTagging(summary)  # summary를 인자로 전달
    return tagged_word_counts  # 태그별 단어의 빈도수 반환

def save_to_csv(tagged_word_counts):
    textExtractionService.save_to_csv(tagged_word_counts)

if __name__ == '__main__':
    # 데이터 로드 및 전처리
    summary = Dataload()
    print("전처리된 요약 데이터:")
    print(summary)  # 전처리된 요약 데이터 출력

    # 단어 태깅
    tagged_word_counts = preprocess(summary)
    print("\n태그별 단어와 빈도수 (빈도 높은 순):")
    for tag, word_counts in tagged_word_counts.items():
        print(f"{tag}: {word_counts}")  # 태그별로 단어와 빈도수 출력

    # 태그 결과를 파일로 저장
    save_to_csv(tagged_word_counts)
