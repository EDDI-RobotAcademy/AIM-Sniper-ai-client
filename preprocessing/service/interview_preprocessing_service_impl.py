import glob
import itertools
import json
import os
import random

import nltk
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from preprocessing.repository.interview_preprocessing_repository_impl import InterviewPreprocessingRepositoryImpl
from preprocessing.service.interview_preprocessing_service import InterviewPreprocessingService


class InterviewPreprocessingServiceImpl(InterviewPreprocessingService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__interviewPreprocessingRepository = InterviewPreprocessingRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def separateDataByInfo(self):
        rawData = self.__interviewPreprocessingRepository.readJsonFile()
        dataList = self.__interviewPreprocessingRepository.extractColumns(rawData)
        self.__interviewPreprocessingRepository.separateFileByInfo(dataList)

    def sampleInterviewData(self, nAnswer, mQuestion):
        interviewList = self.__interviewPreprocessingRepository.readJsonFile(filePath='assets/interview/')
        interviewList = list(itertools.chain(*interviewList))
        print(f"인터뷰 수: {len(interviewList)}")

        sampledAnswerIndex, sampledQuestionIndex = (
            self.__interviewPreprocessingRepository.sampleAnswerAndQuestionIndex(
                len(interviewList), nAnswer, mQuestion))
        answerList = [interviewList[idx]['answer'] for idx in sampledAnswerIndex]
        realQuestionList = [interviewList[idx]['question'] for idx in sampledAnswerIndex]
        questionList = [interviewList[idx]['question'] for idx in sampledQuestionIndex]

        return answerList, realQuestionList, questionList

    def transformSampledData(self, answerList, questionList):
        mecab = self.__interviewPreprocessingRepository.loadMecab()
        taggedAnswerList = [self.__interviewPreprocessingRepository.posTagging(mecab, answer)
                            for answer in answerList]
        taggedQuestionList = [self.__interviewPreprocessingRepository.posTagging(mecab, question)
                              for question in questionList]

        filteredAnswerList = [self.__interviewPreprocessingRepository.filterWord(taggedAnswer)
                              for taggedAnswer in taggedAnswerList]
        filteredQuestionList = [self.__interviewPreprocessingRepository.filterWord(taggedQuestion)
                                for taggedQuestion in taggedQuestionList]

        answerStringList = [' '.join(filteredAnswer) for filteredAnswer in filteredAnswerList]
        questionStringList = [' '.join(filteredQuestion) for filteredQuestion in filteredQuestionList]

        return answerStringList, questionStringList

    def cosineSimilarityBySentenceTransformer(self, answerStringList, questionStringList):
        sentenceTransformer = self.__interviewPreprocessingRepository.loadSentenceTransformer()
        cosineSimilarityList = (
            self.__interviewPreprocessingRepository.calculateCosineSimilarityWithSentenceTransformer(
                sentenceTransformer, answerStringList, questionStringList
            ))

        return cosineSimilarityList

    def cosineSimilaritiyByNltk(self, answerStringList, questionStringList):
        if not os.path.exists(os.path.join(os.getcwd(), 'assets', 'nltk_data')):
            self.__interviewPreprocessingRepository.downloadNltkData()

        vectorizer = self.__interviewPreprocessingRepository.loadVectorizer()
        cosineSimilarityList = self.__interviewPreprocessingRepository.calculateCosineSimilarityWithNltk(
            vectorizer, answerStringList, questionStringList
        )

        return cosineSimilarityList

