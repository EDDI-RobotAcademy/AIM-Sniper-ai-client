import json
import time

from preprocessing.service.interview_preprocessing_service_impl import InterviewPreprocessingServiceImpl

if __name__ == '__main__':
    interviewPreprocessingService = InterviewPreprocessingServiceImpl.getInstance()

    def separateData(filePath):
        startTime = time.time()
        interviewPreprocessingService.separateDataByInfo(filePath)
        endTime = time.time()
        print(f"소요 시간: {endTime - startTime}")

    def countKeyword(*args, interviewDataPath):
        countedKeywordDict = dict()
        for keyword in args:
            countedKeywordDict[keyword] = interviewPreprocessingService.countWantToData(keyword, interviewDataPath)
            print(f"{keyword}: {countedKeywordDict[keyword]}")

        return countedKeywordDict

    def calculateCosineSimilarityBySentenceTransformer(nAnswer, mQuestion, filePath):
        interviewList = interviewPreprocessingService.getInterviewData()
        interviewList = interviewPreprocessingService.flattenInterviewData(interviewList)

        answerList, realQuestionList, questionList = (
            interviewPreprocessingService.sampleInterviewData(interviewList, nAnswer, mQuestion, filePath))

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

    def calculateCosineSimilarityByNltk(nAnswer, mQuestion, filePath):
        interviewList = interviewPreprocessingService.getInterviewData()
        interviewList = interviewPreprocessingService.flattenInterviewData(interviewList)

        answerList, realQuestionList, questionList = (
            interviewPreprocessingService.sampleInterviewData(interviewList, nAnswer, mQuestion, filePath))

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

    # separateData('assets/interview_v2')

    def labelingQuestionByRuleBase():
        interviewList = interviewPreprocessingService.getInterviewData('assets/interview')
        interviewList = interviewPreprocessingService.flattenInterviewData(interviewList)
        adaptabilityKeywordList = [
            '변화', '대처', '도전', '예기치 못한 문제',
            '유연성', '새로운 환경', '빠르게 적응'
        ]
        projectKeywordList = [
            '프로젝트', '역할', '책임', '팀워크', '리더십',
            '일정 관리', '목표 설정', '협업 과정', '성과 도출'
        ]
        selfDevelopmentKeywordList = [
            '학습', '성장', '자기 주도', '새로운 기술 학습', '트렌드 파악', '자격증',
            '교육 참여', '개인 목표', '스킬 향상', '공부', '스터디'
        ]
        communicationKeywordList = [
            '의견 교환', '피드백', '대화', '갈등 해결', '상사와의 소통', '팀원 간 협력',
            '논의', '토론', '명확한 전달', '커뮤니케이션 스킬', '상사', '타 부서'
        ]
        skillKeywordList = [
            '프로그래밍 언어', '개발 도구', '시스템 설계', '코드 최적화', '알고리즘',
            '데이터베이스', '성능 향상', '기술 스택', '소프트웨어 개발',
            '테스트 자동화', '애자일 방법론', 'CI/CD', '클라우드 컴퓨팅',
            '버전 관리', 'API 설계', '프레임워크', '보안', '데이터 분석', '분석'
        ]

        for interview in interviewList:
            question = interview['question']
            interview['intent'] = None

            if any(keyword in question for keyword in communicationKeywordList):
                interview['intent'] = '의사 소통'
            elif any(keyword in question for keyword in adaptabilityKeywordList):
                interview['intent'] = '적응력'
            elif any(keyword in question for keyword in projectKeywordList):
                if all(keyword not in question for keyword in ['게임', '창의성', '산사태']):
                    interview['intent'] = '프로젝트 경험'
            elif any(keyword in question for keyword in selfDevelopmentKeywordList):
                interview['intent'] = '자기 개발'
            elif any(keyword in question for keyword in skillKeywordList):
                interview['intent'] = '기술적 역량'

        return interviewList

    def countLabeledInterview(interviewList):
        labelCountDict = {
            '적응력': 0,
            '프로젝트 경험': 0,
            '자기 개발': 0,
            '의사 소통': 0,
            '기술적 역량': 0,
            'None': 0
        }

        for interview in interviewList:
            intent = interview['intent']

            if intent in labelCountDict:
                labelCountDict[intent] += 1
            else:
                labelCountDict['None'] += 1

        return labelCountDict

    labeledInterviewList = labelingQuestionByRuleBase()
    labelCountDict = countLabeledInterview(labeledInterviewList)
    print(labelCountDict)

    interviewListNotNone = []
    for interview in labeledInterviewList:
        if interview['intent'] is not None:
            interviewListNotNone.append(interview)

    with open('assets/interview_labeling_rule_base.json', 'w', encoding='utf-8') as f:
        json.dump(labeledInterviewList, f, ensure_ascii=False, indent=4)

    with open('assets/interview_labeling_rule_base_not_none.json', 'w', encoding='utf-8') as f:
        json.dump(interviewListNotNone, f, ensure_ascii=False, indent=4)
