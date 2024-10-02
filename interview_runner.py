import glob
import time
import os

from tqdm import tqdm

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

interview = InterviewPreprocessingServiceImpl()

def concatenateRawData(rawFilePath, concatenatedFilePath):
    interview.saveConcatenatedRawJsonFile(rawFilePath, concatenatedFilePath)

def separateData(concatenatedFilePath, separatedFilePath):
    interview.separateJsonFileByInfo(concatenatedFilePath, separatedFilePath)

# 룰 베이스 의도 라벨링
def labelingIntentByRuleBase(separatedFilePath):
    interviewList = interview.flattenFileToList(separatedFilePath)
    labeledInterviewList = interview.intentLabeling(interviewList)

    return labeledInterviewList

def saveSampledLabeledInterview(separatedFilePath, labeledFilePath):
    labeledInterviewList = labelingIntentByRuleBase(separatedFilePath)
    interviewListIntentIsNone, interviewListIntentIsNotNone = (
        interview.splitIntentLabeledData(labeledInterviewList, 200))

    interview.samplingAndSaveLabeledData(
            interviewListIntentIsNone, interviewListIntentIsNotNone, 200, labeledFilePath)

def getLLMIntent(inputFile, labeledFilePath):
    interview.getLLMIntent(inputFile, labeledFilePath)

# 규칙 기반 라벨링 vs 정성 평가 라벨링
def comparisonRatioResultToCsv(filePath, keywordForRemove=None):
    labeledInterviewList = interview.readFile(filePath, keywordForRemove)
    interview.comparisonResultToCsv(labeledInterviewList)

def separateFileByIntent(filePath):
    interview.separateFileByIntent(filePath)

def getKeyword(inputFilePath):
    interviewList = interview.readFile(inputFilePath)
    answerList, questionList = [], []
    for data in interviewList:
        answer = data.get('summary')
        question = data.get('question')
        answerList.append(answer)
        questionList.append(question)

    answerStringList = interview.transformDataWithPOSTagging(answerList)
    questionStringList = interview.transformDataWithPOSTagging(questionList)

    answerVec = interview.saveEmbeddedVector(answerStringList)
    questionVec = interview.saveEmbeddedVector(questionStringList)

    for i in range(len(interviewList)):
        interviewList[i]['question_vec'] = questionVec[i].tolist()
        interviewList[i]['answer_vec'] = answerVec[i].tolist()

    savePath = 'assets\\json_data_embedding\\'
    os.makedirs(savePath, exist_ok=True)
    savePath = os.path.join(savePath, f'{inputFilePath.split('\\')[-1][:-5]}_embedded.json')
    interview.saveFile(interviewList, savePath)


from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

# 코사인 유사도 계산 함수

# 유사도 비교 함수
def match_vecs():
    sequence = ['협업_능력', '대처_능력', '적응력', '기술적_역량', '프로젝트_경험']
    startAnswerList = interview.readFile(f'assets\\json_data_embedding\\{sequence[0]}_embedded.json')

    # 결과 저장을 위한 카운터 초기화
    cnt = 0

    # 협업 능력 파일 안의 각 answer_vec에 대해 처리
    for startAnswer in tqdm(startAnswerList, total=len(startAnswerList), desc='match_vecs'):
        # 매칭 결과를 저장할 리스트
        matched_data = []
        used_question_vecs = set()  # 사용된 question_vec을 저장할 집합

        # 협업 능력 정보 먼저 저장
        currentAnswerVec = tuple(startAnswer.get('answer_vec'))  # 협업_능력 파일의 answer_vec으로 시작
        matched_data.append({
            "question": startAnswer['question'],  # 협업 능력 질문
            "answer": startAnswer["answer"],  # 협업 능력 답변
            "occupation": startAnswer['occupation'],  # 직업
            "experience": startAnswer.get('experience', 'NEW'),  # 경험
            "intent": startAnswer['rule_based_intent'],  # 의도
        })

        # 이후 대처 능력, 적응력, 기술적 역량, 프로젝트 경험 순으로 비교
        for i in range(1, len(sequence)):
            nextQuestionList = interview.readFile(f'assets\\json_data_embedding\\{sequence[i]}_embedded.json')
            highest_similarity = -1
            best_match = None

            # 현재 answer_vec와 비교할 다음 파일의 question_vec들
            for nextQuestion in nextQuestionList:
                questionVec = tuple(nextQuestion.get('question_vec'))

                if nextQuestion.get('question') in used_question_vecs:
                    continue  # 이미 사용된 질문은 비교에서 제외

                similarity = interview.cosineSimilarityBySentenceTransformer(
                    np.array(currentAnswerVec).reshape(1, -1),
                    np.array(questionVec).reshape(1, -1)
                )

                # 유사도가 가장 높은 question_vec 선택
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = {
                        "question": nextQuestion['question'],  # 유사한 질문
                        "answer": nextQuestion.get('answer'),  # 해당 질문의 답변
                        "occupation": nextQuestion.get('occupation'),  # 직업
                        "experience": nextQuestion.get('experience'),  # 경험
                        "intent": nextQuestion.get('rule_based_intent'),  # 의도
                        "similarity": highest_similarity.tolist(),
                        "answer_vec": nextQuestion.get('answer_vec')
                    }

                # 가장 유사한 질문을 찾았다면 matched_data에 추가하고, 다음 비교를 위해 answer_vec 갱신
            if best_match:
                matched_data.append(best_match)
                used_question_vecs.add(best_match["question"])
                currentAnswerVec = tuple(best_match.get('answer_vec'))  # 다음 비교를 위한 answer_vec 업데이트
        print(matched_data)

        cnt += 1
        os.makedirs('assets\\json_qa_pair', exist_ok=True)
        interview.saveFile(matched_data, f'assets\\json_qa_pair\\result_{cnt}.json')

if __name__ == '__main__':
    rawFilePath = 'assets\\json_data_raw\\'
    concatenatedFilePath = 'assets\\json_data_concatenated\\'
    separatedFilePath = 'assets\\json_data_separated\\'
    labeledFilePath = 'assets\\json_data_intent_labeled\\'

    labeledInputFile = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_qualitative_eval.json')
    compareLabelFilePath = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_llm.json')
    finalIntentPath = os.path.join(labeledFilePath, 'sample_intent_labeled_1200.json')

    labelSeparatedFilePath = 'assets\\json_data_intent_separated\\'

    # concatenateRawData(rawFilePath, concatenatedFilePath)
    # separateData(concatenatedFilePath, separatedFilePath))
    # saveSampledLabeledInterview(separatedFilePath, labeledFilePath)
    # separateFileByIntent(finalIntentPath)
    # labelSeparatedFiles = glob.glob(os.path.join(labelSeparatedFilePath, '*.json'))
    # for file in labelSeparatedFiles:
    #     getKeyword(file)
    match_vecs()


    # 안해도 되는 것들
    # getLLMIntent(labeledInputFile, labeledFilePath)
    # comparisonRatioResultToCsv(compareLabelFilePath, '산사태')




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
