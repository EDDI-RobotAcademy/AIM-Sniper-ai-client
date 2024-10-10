import csv
import itertools
import json
import os

import pandas as pd
from tqdm import tqdm

from interview_preprocessing.repository.interview_preprocessing_corpus_repository_impl import \
    InterviewPreprocessingCorpusRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_file_repository_impl import InterviewPreprocessingFileRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_intent_repository_impl import \
    InterviewPreprocessingIntentRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_openai_repository_impl import \
    InterviewPreprocessingOpenAIRepositoryImpl
from interview_preprocessing.service.interview_preprocessing_service import InterviewPreprocessingService

class InterviewPreprocessingServiceImpl(InterviewPreprocessingService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__interviewPreprocessingFileRepository = InterviewPreprocessingFileRepositoryImpl.getInstance()
            cls.__instance.__interviewPreprocessingCorpusRepository = InterviewPreprocessingCorpusRepositoryImpl.getInstance()
            cls.__instance.__interviewPreprocessingIntentRepository = InterviewPreprocessingIntentRepositoryImpl().getInstance()
            cls.__instance.__interviewPreprocessingOpenAIRepository =InterviewPreprocessingOpenAIRepositoryImpl().getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def saveFile(self, dataList, savePath, silent=False):
        self.__interviewPreprocessingFileRepository.saveFile(savePath, dataList, silent)

    def saveConcatenatedRawJsonFile(self, readFilePath, saveFilePath):
        dataList = self.__interviewPreprocessingFileRepository.readFile(readFilePath)

        os.makedirs(saveFilePath, exist_ok=True)
        savePath = os.path.join(saveFilePath, f'raw_data_concatenated_{len(dataList)}.json')

        print('Save concatenated raw data is done.')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, dataList)

    def separateJsonFileByInfo(self, readFilePath, saveFilePath):
        extractedData = self.__interviewPreprocessingFileRepository.extractColumns(readFilePath)
        self.__interviewPreprocessingFileRepository.separateFileByInfo(extractedData, saveFilePath)

    def transformDataWithPOSTagging(self, sentenceList):
        mecab = self.__interviewPreprocessingCorpusRepository.loadMecab()
        taggedList = \
            [self.__interviewPreprocessingCorpusRepository.posTagging(mecab, sentence) for sentence in sentenceList]

        filteredList = \
            [self.__interviewPreprocessingCorpusRepository.filterWord(taggedSentence) for taggedSentence in taggedList]

        stringList = [' '.join(filteredWord) for filteredWord in filteredList]

        return stringList

    def saveEmbeddedVector(self, stringList):
        sentenceTransformer = self.__interviewPreprocessingCorpusRepository.loadSentenceTransformer()
        embeddedVector = self.__interviewPreprocessingCorpusRepository.getEmbeddingList(sentenceTransformer, stringList)
        return embeddedVector

    def loadSentenceTransformer(self):
        return self.__interviewPreprocessingCorpusRepository.loadSentenceTransformer()

    def cosineSimilarityBySentenceTransformer(self, sentenceTransformer, answerList, questionList):
        embeddedAnswerList = sentenceTransformer.encode(answerList)
        embeddedQuestionList = sentenceTransformer.encode(questionList)

        cosineSimilarityList = (
            self.__interviewPreprocessingCorpusRepository.calculateCosineSimilarity(
                embeddedAnswerList, embeddedQuestionList
            ))

        return cosineSimilarityList

    def cosineSimilarityByNltk(self, answerStringList, questionStringList):
        if not os.path.exists(os.path.join(os.getcwd(), 'assets', 'nltk_data')):
            self.__interviewPreprocessingCorpusRepository.downloadNltkData()

        vectorizer = self.__interviewPreprocessingCorpusRepository.loadVectorizer()
        cosineSimilarityList = self.__interviewPreprocessingCorpusRepository.calculateCosineSimilarityWithNltk(
            vectorizer, answerStringList, questionStringList
        )
        return cosineSimilarityList

    def intentLabeling(self, interviewList, saveFilePath):
        labeledInterviewList = self.__interviewPreprocessingIntentRepository.intentLabelingByRuleBase(interviewList)
        countingData = self.__interviewPreprocessingIntentRepository.countLabeledInterview(labeledInterviewList)
        print('labeling result : ', countingData)

        os.makedirs(saveFilePath, exist_ok=True)
        savePath = os.path.join(saveFilePath, f'total_intent_labeled_{len(labeledInterviewList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, labeledInterviewList)

        labeledInterviewListNotNull = []
        for interview in labeledInterviewList:
            intent = interview.get('rule_based_intent')
            if intent is not None:
                labeledInterviewListNotNull.append(interview)

        savePath = os.path.join(saveFilePath, f'intent_labeled_not_null_{len(labeledInterviewListNotNull)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, labeledInterviewListNotNull)

    def splitIntentLabeledData(self, labeledInterviewList, sampleSize):
        interviewListIntentIsNone, interviewListIntentIsNotNone = (
            self.__interviewPreprocessingIntentRepository.splitInterviewListByIntentIsNone(labeledInterviewList))
        return interviewListIntentIsNone, interviewListIntentIsNotNone

    def samplingAndSaveLabeledData(self,
                                   interviewListIntentIsNone, interviewListIntentIsNotNone, sampleSize, saveFilePath):

        sampledNoneIntentQuestion = (self.__interviewPreprocessingIntentRepository.
                                     sampleRandomQuestionListIntentIsNone(interviewListIntentIsNone, sampleSize))

        sampledIntentQuestions = (self.__interviewPreprocessingIntentRepository.
                                  sampleRandomQuestionListByIntent(interviewListIntentIsNotNone, sampleSize))

        sampledIntentQuestions = self.__interviewPreprocessingIntentRepository.flattenDimensionOfList(sampledIntentQuestions)
        os.makedirs(saveFilePath, exist_ok=True)

        saveIntentNoneLabeledFileName = os.path.join(saveFilePath, f'sample_intent_none_{len(sampledNoneIntentQuestion)}.json')
        saveIntentLabeledFileName = os.path.join(saveFilePath, f'sample_intent_labeled_{len(sampledIntentQuestions)}.json'
                                                    )
        print('Save sampling labeled data is done.')
        self.__interviewPreprocessingFileRepository.saveFile(saveIntentLabeledFileName, sampledIntentQuestions)
        self.__interviewPreprocessingFileRepository.saveFile(saveIntentNoneLabeledFileName, sampledNoneIntentQuestion)

        return sampledNoneIntentQuestion, sampledIntentQuestions

    def readFile(self, filePath):
        interviewList = self.__interviewPreprocessingFileRepository.readFile(filePath)
        return interviewList

    def getLLMIntent(self, inputFile, outputSavePath):
        dataList = self.__interviewPreprocessingFileRepository.readFile(inputFile)

        for data in tqdm(dataList, total=len(dataList), desc='labeling intent by LLM'):
            question = data.get('question')
            intent = self.__interviewPreprocessingOpenAIRepository.generateIntent(question)
            data['llm_intent'] = intent

        saveFilePath = os.path.join(outputSavePath, f'sample_intent_labeled_{len(dataList)}_llm.json')
        print(f'Labeling LLM intent is done. ')
        self.__interviewPreprocessingFileRepository.saveFile(saveFilePath, dataList)

    def comparisonResultToCsv(self, interviewList):
        ruleVsQualitativeRatios = (self.__interviewPreprocessingIntentRepository.
                                      calculateDifferentIntentRatios(interviewList, 'rule_based_intent',
                                                                       'qualitative_eval_intent'))
        try:

            ruleVsLlmRatios = (self.__interviewPreprocessingIntentRepository.
                                  calculateDifferentIntentRatios(interviewList, 'rule_based_intent', 'llm_intent'))

            qualitativeVsLlmRatios = (self.__interviewPreprocessingIntentRepository.
                                         calculateDifferentIntentRatios(interviewList, 'qualitative_eval_intent',
                                                                          'llm_intent'))
        except Exception as e:
            ruleVsLlmRatios = '없음'
            qualitativeVsLlmRatios = '없음'

        comparisonResult = pd.DataFrame({
            'rule_vs_qualitative(%)': ruleVsQualitativeRatios,
            'rule_vs_llm(%)': ruleVsLlmRatios,
            'qualitative_vs_llm(%)': qualitativeVsLlmRatios
        })

        print('comparisonResult : \n', comparisonResult)

        csvPath = os.path.join(os.getcwd(), 'assets', 'csv_data')
        os.makedirs(csvPath, exist_ok=True)

        comparisonResult.to_csv(os.path.join(csvPath, 'intent_comparison_ratios.csv'))
        print('intent_comparison_ratios.csv 생성 완료')

        return comparisonResult

    def countWordAndSave(self, interviewList):
        questionWordList, answerWordList = (
            self.__interviewPreprocessingFileRepository.splitSentenceToWord(interviewList))

        sortedQuestion, sortedAnswer = (
            self.__interviewPreprocessingFileRepository.countWord(questionWordList, answerWordList))

        if not os.path.exists('assets\\csv_data'):
            os.mkdir('assets\\csv_data')

        with open('assets\\csv_data\\question_word_frequencies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["단어", "빈도"])  # 헤더 작성
            for word, count in sortedQuestion:
                writer.writerow([word, count])

        print("File saved at assets\\csv_data\\question_word_frequencies.csv")

        with open('assets\\csv_data\\answer_word_frequencies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["단어", "빈도"])  # 헤더 작성
            for word, count in sortedAnswer:
                writer.writerow([word, count])

        print("File saved at assets\\csv_data\\answer_word_frequencies.csv")

    def filterInterviewDataAndSave(self, interviewList, saveFilePath):
        stopWordList = self.__interviewPreprocessingFileRepository.loadStopWordList()
        filteredInterviewList = (
            self.__interviewPreprocessingFileRepository.filterInterviewData(interviewList, stopWordList))

        os.makedirs(saveFilePath, exist_ok=True)

        saveFilePath = os.path.join(saveFilePath, f'filtered_data_{len(filteredInterviewList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(saveFilePath, filteredInterviewList)

    def getLLMScore(self, inputFilePath):
        interviewList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        if '.json' in inputFilePath:
            interviewList = [interviewList]

        for idx, interviews in enumerate(interviewList):
            for interview in interviews:
                question = interview.get('question')
                intent = interview.get('rule_based_intent')
                answer = interview.get('answer')
                result = self.__interviewPreprocessingOpenAIRepository.scoreAnswer(question, intent, answer)
                resultList = result.split('<s>')
                interview['score'] = resultList[0].replace('score:', '').replace('\"', '').strip()
                interview['feedback'] = resultList[1].replace('feedback:', '').replace('\"', '').strip()
                interview['alternative_answer'] = resultList[2].replace('example:', '').replace('\"', '').strip()

            savePath = 'assets\\json_data_scored\\'
            os.makedirs(savePath, exist_ok=True)
            saveFilePath = os.path.join(savePath, f'session_scored_{(idx+1)}.json')
            self.__interviewPreprocessingFileRepository.saveFile(saveFilePath, interviews)







