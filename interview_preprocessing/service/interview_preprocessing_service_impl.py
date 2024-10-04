import itertools
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

    def flattenFileToList(self, filePath):
        separatedJsonFiles = self.__interviewPreprocessingFileRepository.readFile(filePath)
        if '.json' in filePath:
            return separatedJsonFiles
        interviewList = list(itertools.chain(*separatedJsonFiles))

        return interviewList

    def samplingData(self, filePath, nAnswer, mQuestion):
        separatedJsonFiles = self.__interviewPreprocessingFileRepository.readFile(filePath)
        interviewList = list(itertools.chain(*separatedJsonFiles))

        sampledAnswerIndex, sampledQuestionIndex = (
            self.__interviewPreprocessingFileRepository.
            samplingAnswerAndQuestionIndex(len(interviewList), nAnswer, mQuestion))

        sampledAnswerList = [interviewList[idx]['answer'] for idx in sampledAnswerIndex]
        sampledRealQuestionList = [interviewList[idx]['question'] for idx in sampledAnswerIndex]
        sampledQuestionList = [interviewList[idx]['question'] for idx in sampledQuestionIndex]

        return sampledAnswerList, sampledRealQuestionList, sampledQuestionList

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

    def cosineSimilarityBySentenceTransformer(self, embeddedAnswerStringList, embeddedQuestionStringList):
        cosineSimilarityList = (
            self.__interviewPreprocessingCorpusRepository.calculateCosineSimilarityWithSentenceTransformer(
                embeddedAnswerStringList, embeddedQuestionStringList
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

    def countWantToData(self, keyword, interviewDataPath):
        return self.__interviewPreprocessingCorpusRepository.countWantToData(keyword, interviewDataPath)

    def saveSimilarityResult(self, sentenceTransformerCosineSimilarityList, answerList, realQuestionList, questionList, saveFilePath):
        os.makedirs(saveFilePath, exist_ok=True)
        outputFilename = 'similarity_sentence_transformer.txt'
        saveFilePath = os.path.join(saveFilePath, outputFilename)
        with open(saveFilePath, 'w', encoding='utf-8') as file:
            for idx, cosineSimilarity in enumerate(sentenceTransformerCosineSimilarityList):
                topFiveIndex = sorted(range(len(cosineSimilarity)),
                                      key=lambda i: cosineSimilarity[i], reverse=True)[:5]
                topFiveValue = [cosineSimilarity[i] for i in topFiveIndex]

                file.write(f"**실제 질문**: {realQuestionList[idx]}\n")
                file.write(f"**답변**: {answerList[idx]}\n")
                file.write("\n")

                for i, index in enumerate(topFiveIndex):
                    file.write(f"**질문{i + 1}**: {questionList[index]}\n")
                    file.write(f"**유사도**: {topFiveValue[i]}\n")
                file.write("-------------------------------------------------------------------\n")
            print(f"File saved at {saveFilePath}.")

    def intentLabeling(self, interviewList):
        labeledInterviewList = self.__interviewPreprocessingIntentRepository.intentLabelingByRuleBase(interviewList)
        countingData = self.__interviewPreprocessingIntentRepository.countLabeledInterview(labeledInterviewList)
        print('labeling result : ', countingData)
        savePath = f'assets\\json_data_intent_labeled\\total_intent_labeled_{len(labeledInterviewList)}.json'
        self.__interviewPreprocessingFileRepository.saveFile(savePath, labeledInterviewList)
        return labeledInterviewList

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

    def readFile(self, filePath, keyword=None):
        interviewList = self.__interviewPreprocessingFileRepository.readFile(filePath)
        if keyword != None:
            interviewList = self.__interviewPreprocessingIntentRepository.removeQuestionIfKeywordIn(keyword, interviewList)

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

        ruleVsLlmRatios = (self.__interviewPreprocessingIntentRepository.
                              calculateDifferentIntentRatios(interviewList, 'rule_based_intent', 'llm_intent'))

        qualitativeVsLlmRatios = (self.__interviewPreprocessingIntentRepository.
                                     calculateDifferentIntentRatios(interviewList, 'qualitative_eval_intent',
                                                                      'llm_intent'))

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

    def separateFileByIntent(self, filePath):
        interviewDataList = self.__interviewPreprocessingFileRepository.readFile(filePath)

        extractedData = self.__interviewPreprocessingFileRepository.extractIntent(interviewDataList)

        savePath = 'assets\\json_data_intent_separated\\'
        self.__interviewPreprocessingFileRepository.separateFileByInfo(extractedData, savePath)








