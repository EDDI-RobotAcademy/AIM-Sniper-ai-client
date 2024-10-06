import glob
import json
import os
import random
import numpy as np

from tqdm import tqdm
from datetime import datetime

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

def compareCosineSimilarity(filePath):
    sentenceTransformer = interview.loadSentenceTransformer()
    startIntent = '협업 능력'
    nextIntentList = ['대처 능력', '적응력', '기술적 역량', '프로젝트 경험', '자기 개발']
    labeledInterviewList = interview.readFile(filePath)

    startInterviewList = [data for data in labeledInterviewList
                                  if data.get('rule_based_intent') == startIntent]

    for i, data in enumerate(tqdm(startInterviewList, total=len(startInterviewList), desc='compareCosineSimilarity')):
        currentInterview = data
        sessionData = []
        sessionData.append(currentInterview)

        for idx, nextIntent in enumerate(nextIntentList):
            nextIntentInterviewList = [data for data in labeledInterviewList
                                       if data.get('rule_based_intent') == nextIntent]

            nextQuestionList = [data.get('question') for data in nextIntentInterviewList]

            transformedAnswer = interview.transformDataWithPOSTagging(currentInterview.get('answer'))
            transformedQuestionList = interview.transformDataWithPOSTagging(nextQuestionList)

            similarityList = interview.cosineSimilarityBySentenceTransformer(
                sentenceTransformer,
                np.array(transformedAnswer).reshape(1, -1),
                transformedQuestionList
            )

            sortedSimilarityList = sorted(enumerate(similarityList[0]), key=lambda x: x[1], reverse=True)

            top10PercentCount = int(len(sortedSimilarityList) * 0.1)

            top10percentSimilarity = sortedSimilarityList[:top10PercentCount]

            selectedIdx, similarity = random.choice(top10percentSimilarity)
            nextInterview = nextIntentInterviewList[selectedIdx]
            nextInterview['similarity'] = float(similarity)
            sessionData.append(nextInterview)
            currentInterview = nextInterview

        currentTime = datetime.now().strftime("%m%d%H%M%S%f")
        os.makedirs('assets\\json_data_session', exist_ok=True)
        interview.saveFile(sessionData, f'assets\\json_data_session\\result_{currentTime}.json', silent=True)

def filterInterviewData(filePath):
    interviewList = interview.readFile(filePath)
    interview.countWordAndSave(interviewList)
    interview.filterInterviewDataAndSave(interviewList)

if __name__ == '__main__':
    # rawFilePath = 'assets\\json_data_raw\\'
    # concatenatedFilePath = 'assets\\json_data_concatenated\\'
    # concatenateRawData(rawFilePath, concatenatedFilePath)
    #
    # separatedFilePath = 'assets\\json_data_separated\\'
    # separateData(concatenatedFilePath, separatedFilePath)

    # filterInterviewData(separatedFilePath)
    filteredFilePath = 'assets\\json_data_filtered\\'

    labeledFilePath = 'assets\\json_data_intent_labeled\\'
    # saveSampledLabeledInterview(filteredFilePath, labeledFilePath)

    # 전체 데이터로 세션 만들기
    # finalIntentPath = os.path.join(labeledFilePath, 'intent_labeled_not_none_21463.json')
    # separateFileByIntent(finalIntentPath)
    # labelSeparatedFilePath = 'assets\\json_data_intent_separated\\'
    # labelSeparatedFiles = glob.glob(os.path.join(labelSeparatedFilePath, '*.json'))
    compareCosineSimilarity('assets\\json_data_intent_labeled\\intent_labeled_not_none_21463.json')


    # 안해도 되는 것들
    # labeledInputFile = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_qualitative_eval.json')
    # getLLMIntent(labeledInputFile, labeledFilePath)
    # compareLabelFilePath = os.path.join(labeledFilePath, 'sample_intent_labeled_1091_llm.json')
    # comparisonRatioResultToCsv(compareLabelFilePath, '산사태')

