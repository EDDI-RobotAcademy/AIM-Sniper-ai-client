import glob
import time
import os
import json
import numpy as np
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


def match_vecs():
    sequence = ['협업_능력', '대처_능력', '적응력', '기술적_역량', '프로젝트_경험', '자기_개발']
    startAnswerList = interview.readFile(f'assets\\json_data_embedding\\{sequence[0]}_embedded.json')

    cnt = 0
    used_question_vecs = []
    for startAnswer in tqdm(startAnswerList, total=len(startAnswerList), desc='match_vecs'):
        matched_data = []

        currentAnswerVec = tuple(startAnswer.get('answer_vec'))
        matched_data.append({
            "question": startAnswer['question'],
            "answer": startAnswer["answer"],
            "summary": startAnswer["summary"],
            "occupation": startAnswer['occupation'],
            "experience": startAnswer.get('experience', 'NEW'),
            "intent": startAnswer['rule_based_intent'],
        })

        for i in range(1, len(sequence)):
            nextQuestionList = interview.readFile(f'assets\\json_data_embedding\\{sequence[i]}_embedded.json')
            highest_similarity = -1
            best_match = None

            for nextQuestion in nextQuestionList:
                if nextQuestion.get('question') not in used_question_vecs:
                    questionVec = tuple(nextQuestion.get('question_vec'))


                    similarity = interview.cosineSimilarityBySentenceTransformer(
                        np.array(currentAnswerVec).reshape(1, -1),
                        np.array(questionVec).reshape(1, -1)
                    )

                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        best_match = {
                            "question": nextQuestion.get('question'),
                            "answer": nextQuestion.get('answer'),
                            "summary": nextQuestion.get('summary'),
                            "occupation": nextQuestion.get('occupation'),
                            "experience": nextQuestion.get('experience'),
                            "intent": nextQuestion.get('rule_based_intent'),
                            "similarity": highest_similarity.tolist()[0][0],
                        }
                        currentAnswerVec = nextQuestion.get('answer_vec')
            if best_match:
                matched_data.append(best_match)
                used_question_vecs.append(best_match["question"])
                print('used list : ', used_question_vecs)

        cnt += 1
        os.makedirs('assets\\json_qa_pair', exist_ok=True)
        interview.saveFile(matched_data, f'assets\\json_qa_pair\\result_{cnt}.json', silent=True)

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
    separateData(concatenatedFilePath, separatedFilePath)
    saveSampledLabeledInterview(separatedFilePath, labeledFilePath)
    separateFileByIntent(finalIntentPath)
    labelSeparatedFiles = glob.glob(os.path.join(labelSeparatedFilePath, '*.json'))
    for file in labelSeparatedFiles:
        getKeyword(file)
    match_vecs()


    # 안해도 되는 것들
    # getLLMIntent(labeledInputFile, labeledFilePath)
    # comparisonRatioResultToCsv(compareLabelFilePath, '산사태')
