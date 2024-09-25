import time

from interview_preprocessing.service.interview_preprocessing_service_impl import InterviewPreprocessingServiceImpl
def calculateCosineSimilarityByNltk(nAnswer, mQuestion, filePath, interviewList):
    interviewPreprocessingService = InterviewPreprocessingServiceImpl.getInstance()
    answerList, realQuestionList, questionList = (
        interviewPreprocessingService.samplingData(interviewList, nAnswer, mQuestion, filePath))

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

if __name__ == '__main__':
    interview = InterviewPreprocessingServiceImpl()
    rawFilePath = 'assets\\json_data_raw\\'
    concatenatedFilePath = 'assets\\json_data_concatenated\\'
    separatedFilePath = 'assets\\json_data_separated\\'

    interview.saveConcatenatedRawJsonFile(rawFilePath, concatenatedFilePath)
    interview.separateJsonFileByInfo(concatenatedFilePath, separatedFilePath)
    interviewList = interview.flattenFileToList(separatedFilePath)
    
    # 랜덤으로 답변 리스트, 답변에 대한 실제 응답들, 답변 리스트와 비교할 질문 리스트 추출
    answerList, realQuestionList, questionList = (
        interview.samplingData(separatedFilePath, nAnswer=50, mQuestion=10000))

    answerStringList, questionStringList = (
        interview.transformDataWithPOSTagging(answerList, questionList))

    # print("유사도 계산-----------------------")
    # sentenceTransformerCosineSimilarityList = (
    #     interviewPreprocessingService.cosineSimilarityBySentenceTransformer(answerStringList, questionStringList))
    #
    # saveFilePath = 'assets\\question_answer_similarity'
    # interviewPreprocessingService.saveSimilarityResult(sentenceTransformerCosineSimilarityList, answerList, realQuestionList, questionList,
    #                      saveFilePath)

    # 룰베이스 의도 라벨링
    labeledInterviewList = interview.intentLabeling(interviewList)

    interviewListIntentIsNone, interviewListIntentIsNotNone = (
        interview.splitIntentLabeledData(labeledInterviewList, 200))

    saveFilePath = 'assets\\json_data_intent_labeled'
    sampledNoneIntentQuestion, sampledIntentQuestions = (
        interview.samplingAndSaveLabeledData(
            interviewListIntentIsNone, interviewListIntentIsNotNone, 200, saveFilePath))
