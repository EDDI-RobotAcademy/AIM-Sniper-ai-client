from preprocessing.repository.interview_preprocessing_repository_impl import InterviewPreprocessingRepositoryImpl

if __name__ == '__main__':
    c1 = InterviewPreprocessingRepositoryImpl()
    # rawData = c1.readJsonFile()
    # dataList = c1.extractColumns(rawData)
    # c1.separateFileByInfo(dataList)
    data = c1.readJsonFile(filePath='assets/interview/')
    print(data)
    # mecab = c1.loadMecab()
    # taggedList = c1.posTagging(mecab)
