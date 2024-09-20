import os

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

    # SentenceTransformer로 코사인 유사도 계산
    allInterviewList = list(itertools.chain(*allInterviewList))
    # print(f"인터뷰 개수: {len(allInterviewList)}")

    allCosineSimilarityList = []

    startTime = time.time()

    for i in range(len(allInterviewList)):
        if i == 5: break
        answer = allInterviewList[i]['answer']
        posTaggingAnswer = interviewPreprocessingRepository.posTagging(mecab, answer)
        filteredAnswer = interviewPreprocessingRepository.filterWord(posTaggingAnswer)

        cosineSimilarityList = []

        for j in range(len(allInterviewList)):
            if j == 1000: break
            if i == j:
                cosineSimilarityList.append(np.array([[0]], dtype=np.float32))
                continue

            question = allInterviewList[j]['question']
            posTaggingQuestion = interviewPreprocessingRepository.posTagging(mecab, question)
            filteredQuestion = interviewPreprocessingRepository.filterWord(posTaggingQuestion)
            cosineSimilarity = (
                interviewPreprocessingRepository.calculateCosineSimilarityWithSentenceTransformer(
                    filteredAnswer, filteredQuestion))
            cosineSimilarityList.append(cosineSimilarity)

        allCosineSimilarityList.append(cosineSimilarityList)

    with open('output_sentence_transformer.txt', 'w', encoding='utf-8') as f:
        f.write("Sentence Transformer\n\n")
        for i, cosineSimilarityList in enumerate(allCosineSimilarityList):
            cosineSimilarityValueList = np.array([cosSimilarity[0][0] for cosSimilarity in cosineSimilarityList])
            topFiveIndexList = np.argsort(cosineSimilarityValueList)[-5:][::-1]

            f.write(f"**실제 질문**: {allInterviewList[i]['question']}\n")
            f.write(f"**답변**: {allInterviewList[i]['answer']}\n")
            f.write("\n")

            for j, idx in enumerate(topFiveIndexList):
                f.write(f"**질문{j+1}**: {allInterviewList[idx]['question']}\n")
                f.write(f"**질문{j+1} 코사인 유사도**: {cosineSimilarityValueList[idx]}\n")
            f.write("-------------------------------------------------------------------\n")

    endTime = time.time()
    print(f"Sentence Transformer 소요 시간: {endTime - startTime}")

    # nltk로 코사인 유사도 계산
    nltkDataPath = os.path.join(os.getcwd(), 'assets', 'nltk_data')
    if not os.path.exists(nltkDataPath):
        interviewPreprocessingRepository.downloadNltkData(nltkDataPath)

    # allInterviewList = list(itertools.chain(*allInterviewList))
    # print(f"인터뷰 개수: {len(allInterviewList)}")

    allCosineSimilarityList = []

    startTime = time.time()

    for i in range(len(allInterviewList)):
        if i == 5: break
        answer = allInterviewList[i]['answer']
        posTaggingAnswer = interviewPreprocessingRepository.posTagging(mecab, answer)
        filteredAnswer = interviewPreprocessingRepository.filterWord(posTaggingAnswer)
        questionList = [interview['question'] for j, interview in enumerate(allInterviewList) if i != j and j < 1000]
        posTaggingQuestionList = [interviewPreprocessingRepository.posTagging(mecab, question)
                                  for question in questionList]
        filteredQuestionList = [interviewPreprocessingRepository.filterWord(posTaggingQuestion)
                                for posTaggingQuestion in posTaggingQuestionList]
        filteredTextList = [filteredAnswer] + filteredQuestionList
        cosineSimilarityList = interviewPreprocessingRepository.calculateCosineSimilarityWithNltk(filteredTextList)
        allCosineSimilarityList.append(cosineSimilarityList)

    with open('output_nltk.txt', 'w', encoding='utf-8') as f:
        f.write("nltk\n\n")
        for i, cosineSimilarityArray in enumerate(allCosineSimilarityList):
            CosineSimilarityArray = cosineSimilarityArray.flatten()
            topFiveIndexList = np.argsort(CosineSimilarityArray)[-5:][::-1]

            f.write(f"**실제 질문**: {allInterviewList[i]['question']}\n")
            f.write(f"**답변**: {allInterviewList[i]['answer']}\n")
            f.write("\n")

            for j, idx in enumerate(topFiveIndexList):
                f.write(f"**질문{j + 1}**: {allInterviewList[idx]['question']}\n")
                f.write(f"**질문{j + 1} 코사인 유사도**: {CosineSimilarityArray[idx]}\n")
            f.write("-------------------------------------------------------------------\n")
            f.write("\n")

    endTime = time.time()
    print(f"nltk 소요 시간: {endTime - startTime}")