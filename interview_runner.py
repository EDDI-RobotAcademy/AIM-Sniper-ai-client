import time
import os

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
    labeledFilePath = 'assets\\json_data_intent_labeled\\'

    # interview.saveConcatenatedRawJsonFile(rawFilePath, concatenatedFilePath)
    interview.separateJsonFileByInfo(concatenatedFilePath, separatedFilePath)

    interviewList = interview.flattenFileToList(separatedFilePath)

    # interviewList = interview.flattenFileToList(os.path.join(separatedFilePath, 'ICT.json'))
# sample_intent_labeled_808.json :
# {'협업 능력': 83, '대처 능력': 1192, '적응력': 177, '프로젝트 경험': 75, '자기 개발': 303, '기술적 역량': 73, 'None': 3942}

    # 룰베이스 의도 라벨링
    labeledInterviewList = interview.intentLabeling(interviewList)

    interviewListIntentIsNone, interviewListIntentIsNotNone = (
        interview.splitIntentLabeledData(labeledInterviewList, 200))

    sampledNoneIntentQuestion, sampledIntentQuestions = (
        interview.samplingAndSaveLabeledData(
            interviewListIntentIsNone, interviewListIntentIsNotNone, 200, labeledFilePath))

# sample_intent_labeled_1091.json
# {'협업 능력': 751, '대처 능력': 11440, '적응력': 1711, '프로젝트 경험': 1670, '자기 개발': 2848, '기술적 역량': 91, 'None': 39273}


    # # 유사도 계산
    # answerList, realQuestionList, questionList = (
    #     interview.samplingData(separatedFilePath, nAnswer=50, mQuestion=10000))

    # answerStringList, questionStringList = (
    #     interview.transformDataWithPOSTagging(answerList, questionList))

    # sentenceTransformerCosineSimilarityList = (
    #     interviewPreprocessingService.cosineSimilarityBySentenceTransformer(answerStringList, questionStringList))
    #
    # saveFilePath = 'assets\\question_answer_similarity'
    # interviewPreprocessingService.saveSimilarityResult(sentenceTransformerCosineSimilarityList, answerList, realQuestionList, questionList,
    #                      saveFilePath)
