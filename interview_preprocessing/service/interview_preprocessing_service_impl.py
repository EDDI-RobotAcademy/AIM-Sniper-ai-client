import itertools
import os

from interview_preprocessing.repository.interview_preprocessing_corpus_repository_impl import \
    InterviewPreprocessingCorpusRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_file_repository_impl import InterviewPreprocessingFileRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_intent_repository_impl import \
    InterviewPreprocessingIntentRepositoryImpl
from interview_preprocessing.service.interview_preprocessing_service import InterviewPreprocessingService

class InterviewPreprocessingServiceImpl(InterviewPreprocessingService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__interviewPreprocessingFileRepository = InterviewPreprocessingFileRepositoryImpl.getInstance()
            cls.__instance.__interviewPreprocessingCorpusRepository = InterviewPreprocessingCorpusRepositoryImpl.getInstance()
            cls.__instance.__interviewPreprocessingIntentRepository = InterviewPreprocessingIntentRepositoryImpl().getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

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

    def transformDataWithPOSTagging(self, answerList, questionList):
        mecab = self.__interviewPreprocessingCorpusRepository.loadMecab()
        taggedAnswerList = [self.__interviewPreprocessingCorpusRepository.posTagging(mecab, answer)
                            for answer in answerList]
        taggedQuestionList = [self.__interviewPreprocessingCorpusRepository.posTagging(mecab, question)
                              for question in questionList]

        filteredAnswerList = [self.__interviewPreprocessingCorpusRepository.filterWord(taggedAnswer)
                              for taggedAnswer in taggedAnswerList]
        filteredQuestionList = [self.__interviewPreprocessingCorpusRepository.filterWord(taggedQuestion)
                                for taggedQuestion in taggedQuestionList]

        answerStringList = [' '.join(filteredAnswer) for filteredAnswer in filteredAnswerList]
        questionStringList = [' '.join(filteredQuestion) for filteredQuestion in filteredQuestionList]

        return answerStringList, questionStringList

    def cosineSimilarityBySentenceTransformer(self, answerStringList, questionStringList):
        sentenceTransformer = self.__interviewPreprocessingCorpusRepository.loadSentenceTransformer()
        cosineSimilarityList = (
            self.__interviewPreprocessingCorpusRepository.calculateCosineSimilarityWithSentenceTransformer(
                sentenceTransformer, answerStringList, questionStringList
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

    def readFile(self, filePath):
        return self.__interviewPreprocessingFileRepository.readFile(filePath)

    def compareLabeledIntent(self, labeledInterviewList):
        return self.__interviewPreprocessingIntentRepository.compareLabeledIntent(labeledInterviewList)







