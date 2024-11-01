import csv
import itertools
import json
import os
import random
import re
import pandas as pd
from tqdm import tqdm

from interview_preprocessing.repository.interview_preprocessing_corpus_repository_impl import \
    InterviewPreprocessingCorpusRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_file_repository_impl import InterviewPreprocessingFileRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_intent_repository_impl import \
    InterviewPreprocessingIntentRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_keyword_repository_impl import \
    InterviewPreprocessingKeywordRepositoryImpl
from interview_preprocessing.repository.interview_preprocessing_openai_repository_impl import \
    InterviewPreprocessingOpenAIRepositoryImpl
from interview_preprocessing.service.interview_preprocessing_service import InterviewPreprocessingService

class InterviewPreprocessingServiceImpl(InterviewPreprocessingService):
    __instance = None
    PROJECT_EXPERIENCE_FILE = 'assets\\json_data_separated_by_intent\\프로젝트_경험_914.json'

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__interviewPreprocessingFileRepository = InterviewPreprocessingFileRepositoryImpl.getInstance()
            cls.__instance.__interviewPreprocessingCorpusRepository = InterviewPreprocessingCorpusRepositoryImpl.getInstance()
            cls.__instance.__interviewPreprocessingIntentRepository = InterviewPreprocessingIntentRepositoryImpl().getInstance()
            cls.__instance.__interviewPreprocessingOpenAIRepository =InterviewPreprocessingOpenAIRepositoryImpl().getInstance()
            cls.__instance.__interviewPreprocessingKeywordRepository = InterviewPreprocessingKeywordRepositoryImpl().getInstance()
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def saveFile(self, dataList, savePath, silent=False):
        self.__interviewPreprocessingFileRepository.saveFile(savePath, dataList, silent)

    def saveConcatenatedRawJsonFile(self, readFilePath, saveFilePath):
        dataList = self.__interviewPreprocessingFileRepository.readFile(readFilePath)

        os.makedirs(saveFilePath, exist_ok=True)
        savePath = os.path.join(saveFilePath, f'raw_data_concatenated_{len(dataList)}.json')

        print('Save concatenated raw data is done.')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, dataList)

    def separateJsonFileByInfo(self, readFilePath, saveFilePath):
        extractedData = self.__interviewPreprocessingFileRepository.extractColumns(readFilePath)
        self.__interviewPreprocessingFileRepository.separateFileByInfo(extractedData, saveFilePath)

    def transformDataWithPOSTagging(self, sentenceList):
        mecab = self.__interviewPreprocessingCorpusRepository.loadMecab()
        taggedList = \
            [self.__interviewPreprocessingCorpusRepository.posTagging(mecab, sentence) for sentence in sentenceList]

        filteredList = \
            [self.__interviewPreprocessingCorpusRepository.filterWord(taggedSentence) for taggedSentence in taggedList]

        stringList = [' '.join(filteredWord) for filteredWord in filteredList]

        return stringList

    def saveEmbeddedVector(self, stringList):
        sentenceTransformer = self.__interviewPreprocessingCorpusRepository.loadSentenceTransformer()
        embeddedVector = self.__interviewPreprocessingCorpusRepository.getEmbeddingList(sentenceTransformer, stringList)
        return embeddedVector

    def loadSentenceTransformer(self):
        return self.__interviewPreprocessingCorpusRepository.loadSentenceTransformer()

    def cosineSimilarityBySentenceTransformer(self, sentenceTransformer, answerList, questionList):
        embeddedAnswerList = sentenceTransformer.encode(answerList)
        embeddedQuestionList = sentenceTransformer.encode(questionList)

        cosineSimilarityList = (
            self.__interviewPreprocessingCorpusRepository.calculateCosineSimilarity(
                embeddedAnswerList, embeddedQuestionList
            ))

        return cosineSimilarityList

    def cosineSimilarityByNltk(self, answerStringList, questionStringList):
        if not os.path.exists(os.path.join(os.getcwd(), 'assets', 'nltk_data')):
            self.__interviewPreprocessingCorpusRepository.downloadNltkData()

        vectorizer = self.__interviewPreprocessingCorpusRepository.loadVectorizer()
        cosineSimilarityList = self.__interviewPreprocessingCorpusRepository.calculateCosineSimilarityWithNltk(
            vectorizer, answerStringList, questionStringList
        )
        return cosineSimilarityList

    def intentLabeling(self, interviewList, saveFilePath):
        labeledInterviewList = self.__interviewPreprocessingIntentRepository.intentLabelingByRuleBase(interviewList)
        countingData = self.__interviewPreprocessingIntentRepository.countLabeledInterview(labeledInterviewList)
        print('labeling result : ', countingData)

        os.makedirs(saveFilePath, exist_ok=True)
        savePath = os.path.join(saveFilePath, f'total_intent_labeled_{len(labeledInterviewList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, labeledInterviewList)

        labeledInterviewListNotNull = []
        for interview in labeledInterviewList:
            intent = interview.get('rule_based_intent')
            if intent is not None:
                labeledInterviewListNotNull.append(interview)

        savePath = os.path.join(saveFilePath, f'intent_labeled_not_null_{len(labeledInterviewListNotNull)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, labeledInterviewListNotNull)

    def splitIntentLabeledData(self, labeledInterviewList, sampleSize):
        interviewListIntentIsNone, interviewListIntentIsNotNone = (
            self.__interviewPreprocessingIntentRepository.splitInterviewListByIntentIsNone(labeledInterviewList))
        return interviewListIntentIsNone, interviewListIntentIsNotNone

    def samplingAndSaveLabeledData(self,
                                   interviewListIntentIsNone, interviewListIntentIsNotNone, sampleSize, saveFilePath):

        sampledNoneIntentQuestion = (self.__interviewPreprocessingIntentRepository.
                                     sampleRandomQuestionListIntentIsNone(interviewListIntentIsNone, sampleSize))

        sampledIntentQuestions = (self.__interviewPreprocessingIntentRepository.
                                  sampleRandomQuestionListByIntent(interviewListIntentIsNotNone, sampleSize))

        sampledIntentQuestions = self.__interviewPreprocessingIntentRepository.flattenDimensionOfList(sampledIntentQuestions)
        os.makedirs(saveFilePath, exist_ok=True)

        saveIntentNoneLabeledFileName = os.path.join(saveFilePath, f'sample_intent_none_{len(sampledNoneIntentQuestion)}.json')
        saveIntentLabeledFileName = os.path.join(saveFilePath, f'sample_intent_labeled_{len(sampledIntentQuestions)}.json'
                                                    )
        print('Save sampling labeled data is done.')
        self.__interviewPreprocessingFileRepository.saveFile(saveIntentLabeledFileName, sampledIntentQuestions)
        self.__interviewPreprocessingFileRepository.saveFile(saveIntentNoneLabeledFileName, sampledNoneIntentQuestion)

        return sampledNoneIntentQuestion, sampledIntentQuestions

    def readFile(self, filePath):
        interviewList = self.__interviewPreprocessingFileRepository.readFile(filePath)
        return interviewList

    def getLLMIntent(self, inputFile, outputSavePath):
        dataList = self.__interviewPreprocessingFileRepository.readFile(inputFile)

        for data in tqdm(dataList, total=len(dataList), desc='labeling intent by LLM'):
            question = data.get('question')
            intent = self.__interviewPreprocessingOpenAIRepository.generateIntent(question)
            data['llm_intent'] = intent

        saveFilePath = os.path.join(outputSavePath, f'sample_intent_labeled_{len(dataList)}_llm.json')
        print(f'Labeling LLM intent is done. ')
        self.__interviewPreprocessingFileRepository.saveFile(saveFilePath, dataList)

    def comparisonResultToCsv(self, interviewList):
        ruleVsQualitativeRatios = (self.__interviewPreprocessingIntentRepository.
                                      calculateDifferentIntentRatios(interviewList, 'rule_based_intent',
                                                                       'qualitative_eval_intent'))
        try:

            ruleVsLlmRatios = (self.__interviewPreprocessingIntentRepository.
                                  calculateDifferentIntentRatios(interviewList, 'rule_based_intent', 'llm_intent'))

            qualitativeVsLlmRatios = (self.__interviewPreprocessingIntentRepository.
                                         calculateDifferentIntentRatios(interviewList, 'qualitative_eval_intent',
                                                                          'llm_intent'))
        except Exception as e:
            ruleVsLlmRatios = '없음'
            qualitativeVsLlmRatios = '없음'

        comparisonResult = pd.DataFrame({
            'rule_vs_qualitative(%)': ruleVsQualitativeRatios,
            'rule_vs_llm(%)': ruleVsLlmRatios,
            'qualitative_vs_llm(%)': qualitativeVsLlmRatios
        })

        print('comparisonResult : \n', comparisonResult)

        csvPath = os.path.join(os.getcwd(), 'assets', 'csv_data')
        os.makedirs(csvPath, exist_ok=True)

        comparisonResult.to_csv(os.path.join(csvPath, 'intent_comparison_ratios.csv'))
        print('intent_comparison_ratios.csv 생성 완료')

        return comparisonResult

    def countWordAndSave(self, interviewList):
        questionWordList, answerWordList = (
            self.__interviewPreprocessingFileRepository.splitSentenceToWord(interviewList))

        sortedQuestion, sortedAnswer = (
            self.__interviewPreprocessingFileRepository.countWord(questionWordList, answerWordList))

        if not os.path.exists('assets\\csv_data'):
            os.mkdir('assets\\csv_data')

        with open('assets\\csv_data\\question_word_frequencies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["단어", "빈도"])  # 헤더 작성
            for word, count in sortedQuestion:
                writer.writerow([word, count])

        print("File saved at assets\\csv_data\\question_word_frequencies.csv")

        with open('assets\\csv_data\\answer_word_frequencies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["단어", "빈도"])  # 헤더 작성
            for word, count in sortedAnswer:
                writer.writerow([word, count])

        print("File saved at assets\\csv_data\\answer_word_frequencies.csv")

    def filterInterviewDataAndSave(self, interviewList, saveFilePath):
        stopWordList = self.__interviewPreprocessingFileRepository.loadStopWordList()
        filteredInterviewList = (
            self.__interviewPreprocessingFileRepository.filterInterviewData(interviewList, stopWordList))

        os.makedirs(saveFilePath, exist_ok=True)

        saveFilePath = os.path.join(saveFilePath, f'filtered_data_{len(filteredInterviewList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(saveFilePath, filteredInterviewList)

    def getAnswerScoreByLLM(self, inputFilePath):
        interviewList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        if '.json' in inputFilePath:
            interviewList = [interviewList]
        print('length of data : ', len(interviewList))
        for idx, interviews in tqdm(enumerate(interviewList), total=len(interviewList), desc='tagging score'):
            try:
                for interview in interviews:
                    question = interview.get('question')
                    intent = interview.get('rule_based_intent')
                    answer = interview.get('answer')
                    result = self.__interviewPreprocessingOpenAIRepository.scoreAnswer(question, intent, answer)
                    resultList = result.split('<s>')
                    interview['score'] = resultList[0].replace('score:', '').replace('\"', '').strip()
                    interview['feedback'] = resultList[1].replace('feedback:', '').replace('\"', '').strip()
                    interview['alternative_answer'] = resultList[2].replace('example:', '').replace('\"', '').strip()

            except Exception as e:
                interviewList.remove(interviews)
                print(f"Error processing interview, removed from list: {e}")

            savePath = 'assets\\json_data_scored\\'
            os.makedirs(savePath, exist_ok=True)
            saveFilePath = os.path.join(savePath, f'session_scored_{(idx+1)}.json')
            self.__interviewPreprocessingFileRepository.saveFile(saveFilePath, interviews, silent=True)

    def getTechKeywordByLLM(self):
        roles = ['Backend 엔지니어', 'Frontend 엔지니어', 'AI 엔지니어', 'Infra 엔지니어', 'DevOps 엔지니어']
        result = {}
        for role in tqdm(roles, total=len(roles), desc='get keyword'):
            keywords = self.__interviewPreprocessingOpenAIRepository.getTechKeyword(role)
            keywords = keywords.replace('\"', '').strip().split('<s>')
            result[role.replace(' 엔지니어', '')] = keywords
        saveFilePath = "assets\\json_data_job_keyword"
        os.makedirs(saveFilePath, exist_ok=True)
        self.__interviewPreprocessingFileRepository.saveFile(os.path.join(saveFilePath, 'job_keyword_final.json'), result)

    def getGeneratedQuestionByRuleBase(self, inputFilePath):
        keywordList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        resultList = []
        for job, keywords in tqdm(keywordList.items(), total=len(keywordList), desc='generate questions'):
            for keyword in keywords:
                questionList = self.__interviewPreprocessingKeywordRepository.generateQuestion(keyword)
                for question in questionList:
                    resultList.append({'question': question, 'job': job, 'tech_keyword': keyword})

        savePath = 'assets\\json_data_tech_question'
        os.makedirs(savePath, exist_ok=True)
        savePath = os.path.join(savePath, f'tech_question_{len(resultList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, resultList)

    def removeNumberDot(self, text):
        return re.sub(r'\b\d{1,2}\.', '', text)

    def getTechQuestionByLLM(self, inputFilePath):
        keywordList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        resultList = []
        for job, keywords in tqdm(keywordList.items(), total=len(keywordList), desc='generater questions'):
            try:
                for keyword in keywords:
                    questionList = self.__interviewPreprocessingOpenAIRepository.getTechQuestion(keyword, job)
                    questionList = questionList.split('<s>')
                    try:
                        for question in questionList:
                            question = self.removeNumberDot(question).strip()
                            print('question: ', question)
                            resultList.append({"job": job, "keyword": keyword, 'question': question})

                    except Exception as e:
                        continue
            except Exception as e:
                continue
            print('resultList: ', resultList)

        savePath = 'assets\\json_data_tech_question'
        os.makedirs(savePath, exist_ok=True)
        savePath = os.path.join(savePath, f'tech_question_by_llm.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, resultList)

    def preprocessingTechQuestion(self, inputFilePath):
        techQuestionList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        for questionSet in techQuestionList:
            question = questionSet.get('question')
            questionSet['question'] = re.sub(r'질문\d{1,2}:', '', question).strip()
            question = questionSet.get('question')
            if '40' in question :
                if len(question.split('.')) >= 2 and question.split('.')[-1] != '':
                    questionSet['question'] = question.split('.')[-1]
                elif len(question.split(':')) >= 2 and question.split(':')[-1] != '':
                    questionSet['question'] = question.split('.')[-1]
        savePath = 'assets\\json_data_tech_question'
        os.makedirs(savePath, exist_ok=True)
        savePath = os.path.join(savePath, f'tech_question_{len(techQuestionList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, techQuestionList)

    def getTechAnswerAndScoreByLLM(self, inputFilePath):
        questionList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        nameForSave = ''
        for data in tqdm(questionList, total=len(questionList), desc='generate answer score'):
            question = data.get('question')
            job = data.get('job')
            nameForSave = job
            score = random.randint(10, 88)
            answerList = self.__interviewPreprocessingOpenAIRepository.getTechAnswer(question, score, job)
            try:
                answerList = answerList.split('<s>')
                data['answer'] = answerList[0].replace('answer:', '').replace('\"', '').strip()
                data['feedback'] = answerList[1].replace('feedback:', '').replace('\"', '').strip()
                data['score'] = str(score) + "점"
            except:
                try:
                    print('줄바꿈 제거 방법 시도')
                    data['answer'] = answerList[0].replace('answer:', '').replace('\\n', '').replace('\"', '').strip()
                    data['feedback'] = answerList[1].replace('feedback:', '').replace('\"', '').strip()
                    data['score'] = str(score) + "점"

                except:
                    try:
                        answerList = answerList[0].split('feedback:')
                        data['answer'] = answerList[0].replace('answer:', '').replace('\\n', '').replace('\"', '').strip()
                        data['feedback'] = answerList[1].replace('feedback:', '').replace('\\n', '').replace('\"', '').strip()
                        data['score'] = str(score) + "점"
                    except Exception as e:
                        print('처리하지 못함: ', e)
                        continue



        savePath = 'assets\\json_data_tech_answered'
        os.makedirs(savePath, exist_ok=True)
        savePath = os.path.join(savePath, f'qas_{nameForSave}_{len(questionList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, questionList)

    def getStartQuestionList(self, inputFilePath, saveFilePath):
        interviewList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        labeledInterviewList = self.__interviewPreprocessingIntentRepository.getStartQuestion(interviewList)

        os.makedirs(saveFilePath, exist_ok=True)
        savePath = os.path.join(saveFilePath, f'start_question_{len(labeledInterviewList)}.json')
        self.__interviewPreprocessingFileRepository.saveFile(savePath, labeledInterviewList)

    def getQASByLLM(self, inputFilePath):
        startQuestionList = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)[0]
        intentList = ['자기 분석', '대처 능력', '소통 능력', '프로젝트 경험', '자기 개발']
        for i, startQuestion in tqdm(enumerate(startQuestionList),
                                     total=len(startQuestionList), desc='generate total data'):
            try:
                result = (self.__interviewPreprocessingOpenAIRepository.
                          scoreAnswer(startQuestion['question'], startQuestion['intent'], startQuestion['answer']))
                resultList = result.split('<s>')
                score = resultList[0].replace('score:', '').replace('\"', '').strip()
                feedback = resultList[1].replace('feedback:', '').replace('\"', '').strip()
                startQuestion['score'] = score
                startQuestion['feedback'] = feedback
                generatedSession = [startQuestion]


                for idx in range(1, 5):
                    try:
                        beforeQuestion = generatedSession[idx-1].get('question')
                        beforeAnswer = generatedSession[idx-1].get('answer')
                        intent = intentList[idx]
                        rand = random.random()  # 0~1 사이의 값
                        if rand < 0.2:
                            percent = 20
                        elif rand < 0.5:
                            percent = 30
                        else:
                            percent = 50

                        qaSetList = self.__interviewPreprocessingOpenAIRepository.generateQAS(beforeQuestion, beforeAnswer,
                                                                                              intent, percent)
                        qaSetList = qaSetList.split('<s>')
                        question = qaSetList[0].replace('question:', '').replace('\"', '').strip()
                        answer = qaSetList[1].replace('answer:', '').replace('\"', '').strip()
                        score = qaSetList[2].replace('score:', '').replace('\"', '').strip()
                        feedback = qaSetList[3].replace('feedback:', '').replace('\"', '').strip()
                        generatedSession.append({'question': question, 'answer': answer, 'intent': intent,
                                                 'score': score, 'feedback': feedback})
                    except ConnectionError:
                        startQuestionList.remove(startQuestion)
                        print('Connection Error!')
                        continue

                    except Exception as e:
                        startQuestionList.remove(startQuestion)
                        print(f"Wrong output! Ignore session_{i + 1}. error: ", e)
                        continue
                if len(generatedSession) == 5:
                    savePath = 'assets\\json_qas_by_llm'
                    os.makedirs(savePath, exist_ok=True)
                    (self.__interviewPreprocessingFileRepository.
                     saveFile(os.path.join(savePath, f'qas_{i + 1 + 3061}.json'), generatedSession, silent=True))

            except ConnectionError:
                generatedSession = []
                print('Connection Error!')
                continue

            except Exception as e:
                generatedSession = []
                print(e)
                continue

    def splitJob(self, inputFilePath):
        files = self.__interviewPreprocessingFileRepository.readFile(inputFilePath)
        backendList, frontendList, aiList, InfraList, DevOpsList = [], [], [], [], []
        for file in files:
            job = file.get('job')
            if job == 'Backend':
                backendList.append(file)
            elif job == 'Frontend':
                frontendList.append(file)
            elif job == 'AI':
                aiList.append(file)
            elif job == 'Infra':
                InfraList.append(file)
            elif job == 'DevOps':
                DevOpsList.append(file)

        savePath = 'assets\\json_data_tech_question'
        os.makedirs(savePath, exist_ok=True)
        tech_categories = {
            "Backend": backendList,
            "Frontend": frontendList,
            "AI": aiList,
            "Infra": InfraList,
            "DevOps": DevOpsList
        }
        for name, data in tech_categories.items():
            file_name = f'tech_question_{name}_{len(data)}.json'
            file_path = os.path.join(savePath, file_name)
            self.__interviewPreprocessingFileRepository.saveFile(file_path, data)
