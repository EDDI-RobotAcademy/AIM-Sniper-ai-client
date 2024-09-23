import glob
import json
import os
import random

import nltk
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from mecab import MeCab
from preprocessing.repository.interview_preprocessing_repository import InterviewPreprocessingRepository

class InterviewPreprocessingRepositoryImpl(InterviewPreprocessingRepository):
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

    def readJsonFile(self, filePath='assets/raw_json_data/'):
        os.makedirs(filePath, exist_ok=True)
        jsonFiles = glob.glob(os.path.join(filePath, '**', '*.json'), recursive=True)
        dataList = []

        for file_path in jsonFiles:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    dataList.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error reading {file_path}: {e}")

        return dataList

    def extractColumns(self, rawDataList):
        extractedData = {}

        for data in rawDataList:
            info = data['dataSet']['info']
            infoKey = '_'.join(list(info.values()))

            if infoKey not in extractedData:
                extractedData[infoKey] = []

            extractedData[infoKey].append({
                'question': data['dataSet']['question']['raw']['text'],
                'answer': data['dataSet']['answer']['raw']['text'],
                'occupation': data['dataSet']['info']['occupation'],
                'gender': data['dataSet']['info']['gender'],
                'ageRange': data['dataSet']['info']['ageRange'],
                'experience': data['dataSet']['info']['experience'],
            })
        return extractedData

    def extractColumns_2(self, rawDataList):
        extractedData = {}

        for data in rawDataList:
            info = data['dataSet']['info']
            infoKey = '_'.join([info['occupation'], info['experience']])

            if infoKey not in extractedData:
                extractedData[infoKey] = []

            extractedData[infoKey].append({
                'question': data['dataSet']['question']['raw']['text'],
                'answer': data['dataSet']['answer']['raw']['text'],
                'occupation': data['dataSet']['info']['occupation'],
                'experience': data['dataSet']['info']['experience'],
            })
        return extractedData

    def separateFileByInfo(self, extractedData, filePath):
        os.makedirs(filePath, exist_ok=True)

        for info_key, data in extractedData.items():
            filename = f'{filePath}/{info_key}.json'
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f'Saved at {filePath}/*')

        return True

    def loadMecab(self):
        mecab = MeCab()
        return mecab

    def posTagging(self, mecab, text):
        posTagging = mecab.pos(text)
        # print(posTagging)
        # 일반 명사,
        return posTagging

    def filterWord(self, posTagging):
        targetTags = ['NNG']
        # targetTags = ['NNG', 'NNP', 'VV', 'VA']

        # 특정 태그에 포함된 단어들만 리스트에 저장
        filteredWords = [word for word, tag in posTagging if any(t in tag for t in targetTags)]
        # print(list(set(filtered_words)))
        return filteredWords

    def loadSentenceTransformer(self):
        torch.manual_seed(42)
        np.random.seed(42)
        random.seed(42)
        sentenceTransformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        return sentenceTransformer

    def sampleAnswerAndQuestionIndex(self, totalSize, n, m):
        # 전체 인덱스 생성 (0부터 total_size-1까지)
        allIndices = np.arange(totalSize)

        # n개의 인덱스 랜덤 샘플링
        sampledAnswerIndex = np.random.choice(allIndices, size=n, replace=False)

        # n개의 인덱스를 제외한 나머지 인덱스 추출
        remainingIndices = np.setdiff1d(allIndices, sampledAnswerIndex)

        # 나머지 인덱스에서 m개의 인덱스 랜덤 샘플링
        sampledQuestionIndex = np.random.choice(remainingIndices, size=m, replace=False)

        return sampledAnswerIndex, sampledQuestionIndex

    def calculateCosineSimilarityWithSentenceTransformer(
            self, sentenceTransformer, answerList, questionList):
        embeddingAnswerList = sentenceTransformer.encode(answerList)
        embeddingQuestionList = sentenceTransformer.encode(questionList)

        cosineSimilarityList = cosine_similarity(embeddingAnswerList, embeddingQuestionList)

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

