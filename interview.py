import numpy as np
import itertools
import time

from preprocessing.repository.interview_preprocessing_repository_impl import InterviewPreprocessingRepositoryImpl

if __name__ == '__main__':

    interviewPreprocessingRepository = InterviewPreprocessingRepositoryImpl()
    # rawData = c1.readJsonFile()
    # dataList = c1.extractColumns(rawData)
    # c1.separateFileByInfo(dataList)
    allInterviewList = interviewPreprocessingRepository.readJsonFile(filePath='assets/interview/')
    mecab = interviewPreprocessingRepository.loadMecab()

    # 답변:질문을 1:전체로 유사도 계산
    allInterviewList = list(itertools.chain(*allInterviewList))
    print(f"인터뷰 개수: {len(allInterviewList)}")

    allCosineSimilarityList = []

    startTime = time.time()

    for i in range(len(allInterviewList)):
        if i == 1: break
        answer = allInterviewList[i]['answer']
        posTaggingAnswer = interviewPreprocessingRepository.posTagging(mecab, answer)
        filteredAnswer = interviewPreprocessingRepository.filterWord(posTaggingAnswer)

        cosineSimilarityList = []

        for j in range(len(allInterviewList)):
            if j == 5000: break
            if i == j:
                cosineSimilarityList.append(np.array([[0]], dtype=np.float32))
                continue

            question = allInterviewList[j]['question']
            posTaggingQuestion = interviewPreprocessingRepository.posTagging(mecab, question)
            filteredQuestion = interviewPreprocessingRepository.filterWord(posTaggingQuestion)
            cosineSimilarity = interviewPreprocessingRepository.calculateCosineSimilarity(
                filteredAnswer, filteredQuestion)
            cosineSimilarityList.append(cosineSimilarity)

        allCosineSimilarityList.append(cosineSimilarityList)

    with open('output_all.txt', 'w', encoding='utf-8') as f:
        for i, cosineSimilarityList in enumerate(allCosineSimilarityList):
            cosineSimilarityValueList = np.array([cosSimilarity[0][0] for cosSimilarity in cosineSimilarityList])
            topFiveIndexList = np.argsort(cosineSimilarityValueList)[-5:][::-1]

            f.write(f"**실제 질문**: {allInterviewList[i]['question']}\n")
            f.write(f"**답변**: {allInterviewList[i]['answer']}\n")

            for j, idx in enumerate(topFiveIndexList):
                f.write(f"**질문{j+1}**: {allInterviewList[idx]['question']}\n")
                f.write(f"**질문{j+1} 코사인 유사도**: {cosineSimilarityValueList[idx]}")
                f.write("-------------------------------------------------------------------\n")

    endTime = time.time()
    print(f"소요 시간: {endTime - startTime}")