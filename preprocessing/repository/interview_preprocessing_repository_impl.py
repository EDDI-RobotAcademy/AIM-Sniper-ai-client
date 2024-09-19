import glob
import json
import os
from preprocessing.repository.interview_preprocessing_repository import InterviewPreprocessingRepository

class InterviewPreprocessingRepositoryImpl(InterviewPreprocessingRepository):
    __instance = None
    FILE_PATH = 'assets/raw_json_data/'

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def readRawJson(self):
        jsonFiles = glob.glob(os.path.join(self.FILE_PATH, '**', '*.json'), recursive=True)
        dataList = []
        for file_path in jsonFiles:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    dataList.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error reading {file_path}: {e}")
        return dataList
