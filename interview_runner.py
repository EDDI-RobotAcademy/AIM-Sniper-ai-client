import glob
import json
import os
import random
import numpy as np

from tqdm import tqdm

from interview_preprocessing.service.interview_preprocessing_service_impl import InterviewPreprocessingServiceImpl

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
            similarity_list = []
            for nextQuestion in nextQuestionList:
                questionVec = tuple(nextQuestion.get('question_vec'))

                similarity = interview.cosineSimilarityBySentenceTransformer(
                    np.array(currentAnswerVec).reshape(1, -1),
                    np.array(questionVec).reshape(1, -1)
                )
                similarity_list.append({
                    "question": nextQuestion.get('question'),
                    "answer": nextQuestion.get('answer'),
                    "summary": nextQuestion.get('summary'),
                    "occupation": nextQuestion.get('occupation'),
                    "experience": nextQuestion.get('experience'),
                    "intent": nextQuestion.get('rule_based_intent'),
                    "similarity": similarity.tolist()[0][0],
                    "answer_vec": nextQuestion.get('answer_vec'),
                })

            # 유사도를 기준으로 내림차순 정렬
            similarity_list.sort(key=lambda x: x["similarity"], reverse=True)

            # 상위 10% 추출
            top_10_percent_count = int(len(similarity_list) * 0.1)
            top_10_percent_questions = similarity_list[:top_10_percent_count]

            # 상위 10% 중에서 랜덤하게 하나 선택
            if top_10_percent_questions:
                best_match = random.choice(top_10_percent_questions)
                currentAnswerVec = best_match.get("answer_vec")
                best_match.pop("answer_vec", None)
                matched_data.append(best_match)

        cnt += 1
        os.makedirs('assets\\json_qa_pair', exist_ok=True)
        interview.saveFile(matched_data, f'assets\\json_qa_pair\\result_{cnt}.json', silent=True)

def filterInterviewData(filePath):
    interviewList = interview.readFile(filePath)
    interview.countWordAndSave(interviewList)
    interview.filterInterviewDataAndSave(interviewList)

if __name__ == '__main__':
    # rawFilePath = 'assets\\json_data_raw\\'
    # concatenatedFilePath = 'assets\\json_data_concatenated\\'
    # concatenateRawData(rawFilePath, concatenatedFilePath)
    #
    separatedFilePath = 'assets\\json_data_separated\\'
    # separateData(concatenatedFilePath, separatedFilePath)

    filterInterviewData(separatedFilePath)
    filteredFilePath = 'assets\\json_data_filtered\\'

    labeledFilePath = 'assets\\json_data_intent_labeled\\'
    saveSampledLabeledInterview(filteredFilePath, labeledFilePath)

    finalIntentPath = os.path.join(labeledFilePath, 'sample_intent_labeled_1200.json')
    separateFileByIntent(finalIntentPath)

    labelSeparatedFilePath = 'assets\\json_data_intent_separated\\'
    labelSeparatedFiles = glob.glob(os.path.join(labelSeparatedFilePath, '*.json'))
    for file in labelSeparatedFiles:
        getKeyword(file)
    match_vecs()


    # 안해도 되는 것들
    # labeledInputFile = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_qualitative_eval.json')
    # getLLMIntent(labeledInputFile, labeledFilePath)
    # compareLabelFilePath = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_llm.json')
    # comparisonRatioResultToCsv(compareLabelFilePath, '산사태')

