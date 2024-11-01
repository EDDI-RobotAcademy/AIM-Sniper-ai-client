from abc import ABC, abstractmethod


class InterviewPreprocessingService(ABC):

    @abstractmethod
    def saveFile(self, dataList, savePath, silent):
        pass

    @abstractmethod
    def saveConcatenatedRawJsonFile(self, readFilePath, saveFilePath):
        pass

    @abstractmethod
    def separateJsonFileByInfo(self, readFilePath, saveFilePath):
        pass

    @abstractmethod
    def transformDataWithPOSTagging(self, sentenceList):
        pass

    @abstractmethod
    def saveEmbeddedVector(self, filePath):
        pass

    @abstractmethod
    def loadSentenceTransformer(self):
        pass

    @abstractmethod
    def cosineSimilarityBySentenceTransformer(self, sentenceTransformer, answerList, questionList):
        pass

    @abstractmethod
    def cosineSimilarityByNltk(self, answerStringList, questionStringList):
        pass

    @abstractmethod
    def intentLabeling(self, interviewList, saveFilePath):
        pass

    @abstractmethod
    def splitIntentLabeledData(self, labeledInterviewList, sampleSize):
        pass

    @abstractmethod
    def samplingAndSaveLabeledData(
            self, interviewListIntentIsNone, interviewListIntentIsNotNone, sampleSize, saveFilePath):
        pass

    @abstractmethod
    def readFile(self, filePath):
        pass

    @abstractmethod
    def getLLMIntent(self, inputFile, outputSavePath):
        pass

    @abstractmethod
    def comparisonResultToCsv(self, interviewList):
        pass

    @abstractmethod
    def countWordAndSave(self, interviewList):
        pass

    @abstractmethod
    def filterInterviewDataAndSave(self, interviewList, saveFilePath):
        pass

    @abstractmethod
    def getAnswerScoreByLLM(self, inputFilePath):
        pass

    @abstractmethod
    def getTechKeywordByLLM(self):
        pass

    @abstractmethod
    def getGeneratedQuestionByRuleBase(self, inputFilePath):
        pass

    @abstractmethod
    def removeNumberDot(self, text):
        pass
    @abstractmethod
    def getTechQuestionByLLM(self, inputFilePath):
        pass

    @abstractmethod
    def getTechAnswerAndScoreByLLM(self, inputFilePath):
        pass

    @abstractmethod
    def getStartQuestionList(self, inputFilePath, saveFilePath):
        pass

    @abstractmethod
    def getQASByLLM(self, inputFilePath):
        pass

    @abstractmethod
    def splitJob(self, inputFilePath):
        pass