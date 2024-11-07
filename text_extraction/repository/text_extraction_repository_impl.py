
from mecab import MeCab
import pandas as pd
import re
import numpy as np
from collections import Counter
from nltk import ngrams
import json
import tkinter as tk
from tkinter import filedialog

from text_extraction.repository.text_extraction_repository import TextExtractionRepository


class TextExtractionRepositoryImpl(TextExtractionRepository):
    __instance = None
    tagged_word_counts = {
        'NNG': Counter(),  # 일반 명사
        'NNP': Counter(),  # 고유 명사
        'VV': Counter(),  # 동사
        'VA': Counter(),  # 형용사
        'bigrams': Counter()  # 바이그램 카운트
    }
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def loadData(self):
        # Tkinter로 파일 선택 창 열기
        root = tk.Tk()
        root.withdraw()  # Tkinter 창 숨기기

        # 파일 탐색기에서 파일 선택
        file_path = filedialog.askopenfilename(
            title="Select a JSON file",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )

        if file_path:  # 파일을 선택했으면
            with open(file_path, encoding='utf-8-sig') as json_file:
                data = json.load(json_file)

            # 각 회사의 'businessSummary' 필드만 추출
            summaries = [company['businessSummary'] for company in data.values()]
            return summaries
        else:
            return None  # 파일을 선택하지 않으면 None 반환

    def clean_text(self, data):
        # 리스트의 각 항목에 대해 텍스트 클리닝 작업 수행
        cleaned_data = [re.sub(r'(\*\*|\*|-|\\n|\n)', '', str(text)).strip() for text in data]
        return cleaned_data

    def loadMecab(self):
        mecab = MeCab()
        return mecab

    def posTag(self, mecab, text):
        posTag = mecab.pos(text)
        return posTag

    def filterWord(self, posTag):
        targetTags = ['NNG', 'NNP', 'VV', 'VA']

        # 특정 태그에 포함된 단어들만 리스트에 저장
        filteredWords = [word for word, tag in posTag if any(t in tag for t in targetTags)]
        return filteredWords

    def Tagging(self, tagged):

        for word, tag in tagged:
            if tag in self.tagged_word_counts:
                self.tagged_word_counts[tag][word] += 1  # 단어 카운트 증가

        # 바이그램 생성 및 카운트
        words = [word for word, tag in tagged if tag in self.tagged_word_counts]
        bigrams_list = ngrams(words, 2)  # 단어 리스트에서 바이그램 생성

        for bigram in bigrams_list:
            # 바이그램을 공백 없이 결합한 문자열로 변환 (단어 사이 공백 제거)
            bigram_str = ''.join(bigram).replace(' ', '')
            self.tagged_word_counts['bigrams'][bigram_str] += 1  # 바이그램 카운트 증가

    def save_result(self):
        # 태그별로 단어와 빈도수를 내림차순으로 정렬하여 튜플로 묶어서 반환
        result = {
            tag: sorted([(word, count) for word, count in counts.items()], key=lambda x: x[1], reverse=True)
            for tag, counts in self.tagged_word_counts.items()
        }

        return result