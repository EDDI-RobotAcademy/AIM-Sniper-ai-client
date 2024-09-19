from preprocessing.repository.interview_preprocessing_repository_impl import InterviewPreprocessingRepositoryImpl

if __name__ == '__main__':
    c1 = InterviewPreprocessingRepositoryImpl()
    rawData = c1.readRawJson()