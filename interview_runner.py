import random
from tqdm import tqdm
import os

from interview_preprocessing.service.interview_preprocessing_service_impl import InterviewPreprocessingServiceImpl

interview = InterviewPreprocessingServiceImpl()

def concatenateRawData(rawFilePath, concatenatedFilePath):
    interview.saveConcatenatedRawJsonFile(rawFilePath, concatenatedFilePath)

def separateDataByInfo(concatenatedFilePath, separatedFilePath):
    interview.separateJsonFileByInfo(concatenatedFilePath, separatedFilePath)

def filterInterviewData(separatedFilePath, filteredFilePath):
    interviewList = interview.readFile(separatedFilePath)
    interview.countWordAndSave(interviewList)
    interview.filterInterviewDataAndSave(interviewList, filteredFilePath)

def labelingIntentByRuleBase(filteredFilePath, labeledFilePath):
    interviewList = interview.readFile(filteredFilePath)[0]
    interview.intentLabeling(interviewList, labeledFilePath)

def saveSampledLabeledInterview(totalLabeledFile, labeledFilePath):
    labeledInterviewList = interview.readFile(totalLabeledFile)
    interviewListIntentIsNone, interviewListIntentIsNotNone = interview.splitIntentLabeledData(labeledInterviewList,
                                                                                               200)
    interview.samplingAndSaveLabeledData(interviewListIntentIsNone, interviewListIntentIsNotNone, 200, labeledFilePath)


def createSessionData(filePath, iteration):
    sentenceTransformer = interview.loadSentenceTransformer()
    labeledInterviewList = interview.readFile(filePath)

    intentList = ['협업 능력', '대처 능력', '적응력', '기술적 역량', '프로젝트 경험', '자기 개발']

    allSortedSimilarityList = []
    for idx, intent in enumerate(tqdm(intentList, total=len(intentList) - 1, desc='similarity')):
        if idx == len(intentList) - 1:
            break

        currentIntentInterviewList = [data for data in labeledInterviewList
                                if data.get('rule_based_intent') == intent]
        nextIntentInterviewList = [data for data in labeledInterviewList
                                   if data.get('rule_based_intent') == intentList[idx + 1]]

        currentAnswerList = [data.get('answer') for data in currentIntentInterviewList]
        nextQuestionList = [data.get('question') for data in nextIntentInterviewList]

        transformedAnswerList = interview.transformDataWithPOSTagging(currentAnswerList)
        transformedQuestionList = interview.transformDataWithPOSTagging(nextQuestionList)

        similarityList = interview.cosineSimilarityBySentenceTransformer(
            sentenceTransformer,
            transformedAnswerList,
            transformedQuestionList
        )

        sortedSimilarityList = []
        for similarity in similarityList:
            sortedSimilarity = sorted(enumerate(similarity), key=lambda x: x[1], reverse=True)
            top5PercentCount = int(len(sortedSimilarity) * 0.05)
            top5percentSimilarity = sortedSimilarity[:top5PercentCount]
            sortedSimilarityList.append(top5percentSimilarity)

        allSortedSimilarityList.append(sortedSimilarityList)

    startIntent = intentList[0]
    nextIntentList = intentList[1:]

    startInterviewList = [data for data in labeledInterviewList
                          if data.get('rule_based_intent') == startIntent]

    for i in range(iteration):
        for j, startInterview in enumerate(tqdm(startInterviewList, total=len(startInterviewList), desc='session')): #
            sessionData = []
            sessionData.append(startInterview)
            selectedIdx, similarity = random.choice(allSortedSimilarityList[0][j])
            nextIntentInterviewList = [data for data in labeledInterviewList
                                       if data.get('rule_based_intent') == nextIntentList[0]]
            nextIntentInterview = nextIntentInterviewList[selectedIdx]
            nextIntentInterview['similarity'] = float(similarity)
            sessionData.append(nextIntentInterview)
            for idx, intent in enumerate(nextIntentList[1:]):
                selectedIdx, similarity = random.choice(allSortedSimilarityList[idx+1][selectedIdx])
                nextIntentInterviewList = [data for data in labeledInterviewList
                                           if data.get('rule_based_intent') == intent]
                nextIntentInterview = nextIntentInterviewList[selectedIdx]
                nextIntentInterview['similarity'] = float(similarity)
                sessionData.append(nextIntentInterview)

            savePath = f'assets\\json_data_session\\data_set_{i+1}'
            os.makedirs(savePath, exist_ok=True)
            interview.saveFile(sessionData, os.path.join(savePath, f'session_{j+1}.json'), silent=True)

def scoreAnswer(sessionDataPath):
    interview.getAnswerScoreByLLM(sessionDataPath)

def getLLMIntent(inputFile, labeledFilePath):
    interview.getLLMIntent(inputFile, labeledFilePath)

def comparisonRatioResultToCsv(filePath):
    labeledInterviewList = interview.readFile(filePath)
    interview.comparisonResultToCsv(labeledInterviewList)

def getTechKeyword():
    interview.getTechKeywordByLLM()

def getTechQuestions(keywordFilePath):
    # interview.getGeneratedQuestionByRuleBase(keywordFilePath)
    interview.getTechQuestionByLLM(keywordFilePath)

def preprocessingTechQuestion(techQuestionFilePath):
    interview.preprocessingTechQuestion(techQuestionFilePath)
def getTechAnswerAndScore(techQuestionFilePath):
    interview.getTechAnswerAndScoreByLLM(techQuestionFilePath)

def getQASData(sessionDataPath):
    interview.getQASByLLM(sessionDataPath)

def getStartQuestion(filteredFilePath, startQuestionFilePath):
    interview.getStartQuestionList(filteredFilePath, startQuestionFilePath)

def splitJob(techQuestionFilePath):
    interview.splitJob(techQuestionFilePath)

if __name__ == '__main__':
    # rawFilePath = 'assets\\json_data_raw\\'
    # concatenatedFilePath = 'assets\\json_data_concatenated\\'
    # concatenateRawData(rawFilePath, concatenatedFilePath)

    # separatedFilePath = 'assets\\json_data_separated\\'
    # separateDataByInfo(concatenatedFilePath, separatedFilePath)

    # filteredFilePath = 'assets\\json_data_filtered\\'
    # filterInterviewData(separatedFilePath, filteredFilePath)

    # labeledFilePath = 'assets\\json_data_intent_labeled\\intent_labeled_not_null_21445.json'
    # labelingIntentByRuleBase(filteredFilePath, labeledFilePath)

    # 자기 분석 질문 추출
    startQuestionFilePath = 'assets\\json_data_start_question\\'
    # getStartQuestion(filteredFilePath, startQuestionFilePath)

    # 면접 세션 만들기
    # finalIntentPath = os.path.join(labeledFilePath, 'intent_labeled_not_null_21474.json')
    # createSessionData(finalIntentPath, 3)

    # 채점 및 피드백
    # sessionDataPath = 'assets\\json_data_session\\data_set_1' #  (total 3578)
    # sessionDataPath = 'assets\\json_data_session\\data_set_2' # start : 3579 (total 3578) +1 옆에 + 3578해주기
    # sessionDataPath = 'assets\\json_data_session\\data_set_3'
    # sessionDataPath = 'assets\\json_data_session\\'
    # scoreAnswer(sessionDataPath)


    # all session by LLM
    # getQASData(startQuestionFilePath)

    # LLM 기반 키워드 추출
    # getTechKeyword()

    # 키워드 기반 기술 면접 question 생성
    # keywordFilePath = "assets\\json_data_job_keyword\\job_keyword_final.json"
    # getTechQuestions(keywordFilePath)
    # techQuestionFilePath = "assets\\json_data_tech_question\\tech_question_by_llm.json"
    # preprocessingTechQuestion(techQuestionFilePath)
    # LLM 기반 기술 면접 question의 답변 및 점수/피드백 생성
    # techQuestionFilePath = "assets\\json_data_tech_question\\tech_question_10570.json"
    # splitJob(techQuestionFilePath)
    backendFilePath = "assets\\json_data_tech_question\\tech_question_Backend_2178.json"
    frontendFilePath = "assets\\json_data_tech_question\\tech_question_Frontend_2364.json"
    aiFilePath = "assets\\json_data_tech_question\\tech_question_AI_2014.json"
    infraFilePath = "assets\\json_data_tech_question\\tech_question_Infra_2129.json"
    devOpsFilePath = "assets\\json_data_tech_question\\tech_question_DevOps_1884.json"
    getTechAnswerAndScore(backendFilePath)

    # 기술 면접 세션 생성
    # 'assets\\json_data_tech_answered'

    # LLM 의도 라벨링
    # labeledInputFile = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_qualitative_eval.json')
    # getLLMIntent(labeledInputFile, labeledFilePath)

    # 불일치 정도 비교
    # compareLabelFilePath = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_llm.json')
    # comparisonRatioResultToCsv(compareLabelFilePath)
