import os
import random
import numpy as np
import glob
import json

import nltk
import torch

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from mecab import MeCab

from interview_preprocessing.repository.interview_preprocessing_corpus_repository import \
    InterviewPreprocessingCorpusRepository


class InterviewPreprocessingCorpusRepositoryImpl(InterviewPreprocessingCorpusRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def loadMecab(self):
        mecab = MeCab()
        return mecab

    def posTagging(self, mecab, text):
        posTagging = mecab.pos(text)
        # 일반 명사,
        return posTagging

    def filterWord(self, posTagging):
        # targetTags = ['NNG']
        targetTags = ['NNG', 'NNP', 'VV', 'VA']

        # 특정 태그에 포함된 단어들만 리스트에 저장
        filteredWords = [word for word, tag in posTagging if any(t in tag for t in targetTags)]
        return filteredWords

    def loadSentenceTransformer(self):
        torch.manual_seed(42)
        np.random.seed(42)
        random.seed(42)
        sentenceTransformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        return sentenceTransformer

    def getEmbeddingList(self, sentenceTransformer, stringList):
        embeddedList = sentenceTransformer.encode(stringList)
        return embeddedList


    def calculateCosineSimilarity(self, embeddedAnswerList, embeddedQuestionList):
        cosineSimilarityList = cosine_similarity(embeddedAnswerList, embeddedQuestionList)

        return cosineSimilarityList

    def downloadNltkData(self, nltkDataPath):
        os.mkdir(nltkDataPath)
        nltk.data.path.append(nltkDataPath)
        nltk.download('punkt', download_dir=nltkDataPath)

    def loadVectorizer(self):
        vectorizer = TfidfVectorizer(tokenizer=lambda x: x, lowercase=False)
        return vectorizer

    def calculateCosineSimilarityWithNltk(self, vectorizer, answerStringList, questionStringList):
        answerAndQuestionList = answerStringList + questionStringList

        # TF-IDF 벡터라이저로 텍스트 벡터화
        tfidfMatrix = vectorizer.fit_transform(answerAndQuestionList)

        # 답변과 나머지 질문들 간의 코사인 유사도 계산
        cosineSimilarityList = cosine_similarity(
            tfidfMatrix[0:len(answerStringList)], tfidfMatrix[len(answerStringList):])

        return cosineSimilarityList

    def countWantToData(self, keyword, interviewDataPath):
        filePath = os.path.join(os.getcwd(), interviewDataPath)
        jsonFileList = glob.glob(os.path.join(filePath, '**', '*.json'), recursive=True)
        totalKeywordCount = 0

        if keyword == "MALE":
            for file in jsonFileList:
                fileName = os.path.basename(file)  # 파일명 추출
                if keyword in fileName:
                    if "FEMALE" not in fileName:
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                totalKeywordCount += len(data)  # 각 파일 내 데이터 개수를 더함
                        except json.JSONDecodeError as e:
                            print(f"Error reading {file}: {e}")
            return totalKeywordCount

        for file in jsonFileList:
            fileName = os.path.basename(file)  # 파일명 추출
            if keyword in fileName:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        totalKeywordCount += len(data)  # 각 파일 내 데이터 개수를 더함
                except json.JSONDecodeError as e:
                    print(f"Error reading {file}: {e}")

        return totalKeywordCount

