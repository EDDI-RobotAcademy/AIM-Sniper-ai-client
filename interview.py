import time

from preprocessing.service.interview_preprocessing_service_impl import InterviewPreprocessingServiceImpl

if __name__ == '__main__':
    interviewPreprocessingService = InterviewPreprocessingServiceImpl.getInstance()

    def separateData():
        startTime = time.time()
        interviewPreprocessingService.separateDataByInfo()
        endTime = time.time()
        print(f"소요 시간: {endTime - startTime}")

    def countKeyword(*args):
        countedKeywordDict = dict()
        for keyword in args:
            countedKeywordDict[keyword] = interviewPreprocessingService.countWantToData(keyword)
            print(f"{keyword}: {countedKeywordDict[keyword]}")

        return countedKeywordDict

    def calculateCosineSimilarityBySentenceTransformer(nAnswer, mQuestion):
        answerList, realQuestionList, questionList = (
            interviewPreprocessingService.sampleInterviewData(nAnswer, mQuestion))

        answerStringList, questionStringList = (
            interviewPreprocessingService.transformSampledData(answerList, questionList))

        startTime = time.time()
        print("유사도 계산 시작")
        sentenceTransformerCosineSimilarityList = (
            interviewPreprocessingService.cosineSimilarityBySentenceTransformer(
                answerStringList, questionStringList))

        endTime = time.time()
        print(f"Sentence Transformer 소요 시간: {endTime - startTime}")

        outputFilename = 'output_sentence_transformer.txt'
        with open(outputFilename, 'w', encoding='utf-8') as f:
            for idx, cosineSimilarity in enumerate(sentenceTransformerCosineSimilarityList):
                topFiveIndex = sorted(range(len(cosineSimilarity)),
                                      key=lambda i: cosineSimilarity[i], reverse=True)[:5]
                topFiveValue = [cosineSimilarity[i] for i in topFiveIndex]

                f.write(f"**실제 질문**: {realQuestionList[idx]}\n")
                f.write(f"**답변**: {answerList[idx]}\n")
                f.write("\n")

                for i, index in enumerate(topFiveIndex):
                    f.write(f"**질문{i + 1}**: {questionList[index]}\n")
                    f.write(f"**유사도**: {topFiveValue[i]}\n")
                f.write("-------------------------------------------------------------------\n")
            print(f"{outputFilename} 생성")

    def calculateCosineSimilarityByNltk(nAnswer, mQuestion):
        answerList, realQuestionList, questionList = (
            interviewPreprocessingService.sampleInterviewData(nAnswer, mQuestion))

        answerStringList, questionStringList = (
            interviewPreprocessingService.transformSampledData(answerList, questionList))

        startTime = time.time()

        nltkCosineSimilarityList = interviewPreprocessingService.cosineSimilarityByNltk(
            answerStringList, questionStringList
        )

        endTime = time.time()
        print(f"nltk 소요 시간: {endTime - startTime}")

        outputFilename = 'output_nltk.txt'
        with open(outputFilename, 'w', encoding='utf-8') as f:
            for idx, cosineSimilarity in enumerate(nltkCosineSimilarityList):
                topFiveIndex = sorted(range(len(cosineSimilarity)),
                                      key=lambda i: cosineSimilarity[i], reverse=True)[:5]
                topFiveValue = [cosineSimilarity[i] for i in topFiveIndex]

                f.write(f"**실제 질문**: {realQuestionList[idx]}\n")
                f.write(f"**답변**: {answerList[idx]}\n")
                f.write("\n")

                for i, index in enumerate(topFiveIndex):
                    f.write(f"**질문{i + 1}**: {questionList[index]}\n")
                    f.write(f"**유사도**: {topFiveValue[i]}\n")
                f.write("-------------------------------------------------------------------\n")
            print(f"{outputFilename} 생성")

    countKeyword("FEMALE", "MALE", "EXPERIENCED", "NEW")
