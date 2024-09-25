import glob
import json
import os
import numpy as np
from tqdm import tqdm

from interview_preprocessing.repository.interview_preprocessing_file_repository import \
    InterviewPreprocessingFileRepository


class InterviewPreprocessingFileRepositoryImpl(InterviewPreprocessingFileRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def readFile(self, filePath):
        if '.json' not in filePath: # len(filePath.split('.')) != 2
            jsonFiles = glob.glob(os.path.join(filePath, '**', '*.json'), recursive=True)
            dataList = []

            for jsonFilePath in tqdm(jsonFiles, total=len(jsonFiles), desc=f' read json files in {filePath}'):
                with open(jsonFilePath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    dataList.append(data)
            return dataList

        else:
            with open(filePath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data


    def saveFile(self, filePath, data):
        try:
            with open(filePath, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f'Saved at {filePath}.')

        except PermissionError as e:
            print(f"PermissionError: {e}")
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")

    def extractColumns(self, filePath):
        filePath = glob.glob(os.path.join(filePath, '*.json'))
        rawDataList = self.readFile(filePath[0])
        extractedData = {}

        for data in tqdm(rawDataList, total=len(rawDataList), desc='extracting columns'):
            info = data['dataSet']['info']
            infoKey = '_'.join([info['occupation'], info['experience']])

            if infoKey not in extractedData:
                extractedData[infoKey] = []

            extractedData[infoKey].append({
                'question': data['dataSet']['question']['raw']['text'],
                'answer': data['dataSet']['answer']['raw']['text'],
                'occupation': data['dataSet']['info']['occupation'],
                'experience': data['dataSet']['info']['experience'],
            })
        return extractedData

    def separateFileByInfo(self, extractedData, filePath):
        os.makedirs(filePath, exist_ok=True)

        for info_key, data in tqdm(extractedData.items(), total=len(extractedData), desc='separate and save json files'):
            filename = f'{filePath}/{info_key}.json'
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f'Separate Done. Saved at {filePath} .')

        return True

    def samplingAnswerAndQuestionIndex(self, totalSize, n, m):
        # 전체 인덱스 생성 (0부터 total_size-1까지)
        allIndices = np.arange(totalSize)

        # n개의 인덱스 랜덤 샘플링
        sampledAnswerIndex = np.random.choice(allIndices, size=n, replace=False)

        # n개의 인덱스를 제외한 나머지 인덱스 추출
        remainingIndices = np.setdiff1d(allIndices, sampledAnswerIndex)

        # 나머지 인덱스에서 m개의 인덱스 랜덤 샘플링
        sampledQuestionIndex = np.random.choice(remainingIndices, size=m, replace=False)

        return sampledAnswerIndex, sampledQuestionIndex