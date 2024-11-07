import pandas as pd


import pandas as pd

from text_extraction.repository.text_extraction_repository_impl import TextExtractionRepositoryImpl
from text_extraction.service.text_extraction_service import TextExtractionService


class TextExtractionServiceImpl(TextExtractionService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__TextExtractionRepository = TextExtractionRepositoryImpl.getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def loadAndPreprocessing(self):
        data = self.__instance.__TextExtractionRepository.loadData()
        summary = self.__TextExtractionRepository.clean_text(data)
        return summary

    def wordTagging(self, summary):
        mecab = self.__instance.__TextExtractionRepository.loadMecab()

        # 각 요약 데이터에 대해 태깅 수행
        for text in summary:
            tagged = self.__TextExtractionRepository.posTag(mecab, text)
            self.__TextExtractionRepository.Tagging(tagged)

        result = self.__TextExtractionRepository.save_result()

        return result  # 딕셔너리 형태로 반환

    def save_to_csv(self, tagged_word_counts, filename="tagged_word_counts_1.csv"):
        data = []
        for tag, word_counts in tagged_word_counts.items():
            for word, count in word_counts:
                if isinstance(word, tuple):  # 바이그램일 경우
                    word = ' '.join(word)
                data.append([tag, word, count])

        # 데이터프레임으로 변환
        df = pd.DataFrame(data, columns=['Tag', 'Word', 'Count'])

        # CSV 파일로 저장
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # UTF-8 인코딩으로 저장
        print(f"단어 태그 결과가 '{filename}' 파일로 저장되었습니다.")

