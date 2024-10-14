from interview_preprocessing.repository.interview_preprocessing_keyword_repository import \
    InterviewPreprocessingKeywordRepository


class InterviewPreprocessingKeywordRepositoryImpl(InterviewPreprocessingKeywordRepository):
    __instance = None
    QUESTIONS = ['<k> 관련 경험이 있으신가요?', '<k> 관련 경험이 있으십니까', '<k> 관련 경험이 있다면 말씀 부탁드립니다.',
                 '<k>에 대해 설명해 보세요', '<k>에 대해 알고 계신가요?', '<k>에 대해 알고 있는 것까지 설명해 보세요.',
                 '<k>을 알고 계시다면 설명해주십시오.', '<k>에 대해 설명해주시고, 관련 경험이 있다면 말씀 부탁드립니다.',
                 '귀하께서는 <k>을 이해하고 활용하는 데 능숙한 편이신가요?', '<k>을 어느정도까지 활용할 수 있으신가요?',
                 '<k>을 능숙하게 사용하실 수 있나요?', '<k> 활용에 자신이 있으십니까?', '왜 <k>을 사용하시는 지 알고 계신가요?',
                 '<k>의 장점에 대해 설명해 보세요.', '<k>에 대해서 본인이 아시는 대로 설명해 주십시오',
                 '<k>이란 무엇이고 대표적인 장점과 단점은 무엇이 있을까요?', '<k>에 관해서 구체적으로 이야기 해 보시기 바랍니다',
                 '<k>에 대해 알고 계시다면 자유롭게 설명해 주시길 바랍니다.', '<k>이란 무엇인지 아시는 대로 설명해주시길 바랍니다.',
                 '<k>이 무엇인지 설명해주실 수 있을까요?', '해당 분야에서 <k>이 왜 필요하다고 생각하시나요?',
                 '지원자님께서 생각하는 <k>이란 무엇인지, 그리고 <k>의 장점은 무엇인지 말씀 부탁드립니다.',
                 '<k>에 대해서 지원자님께서 아시는 대로 한번 편하게 설명해 주시겠습니까', '<k>이란 무엇인지에 대해서 설명 부탁드립니다.',
                 '지원자님은 <k>이 해당 분야에서 왜 필요하다고 생각하십니까?', '<k>의 장점과 단점에 대해 아시는 대로 편하게 설명 부탁드립니다.']

    INITIAL_CONSONANTS = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ',
                          'ㅌ', 'ㅍ', 'ㅎ']
    MEDIAL_VOWELS = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ',
                     'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    FINAL_CONSONANTS = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
                        'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    ENGLISH_FINAL = ['l', 'm', 'n', 'g', 'L', 'M', 'N', 'G']

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def decomposeHangul(self, keyword):
        first_hangul = 0xAC00
        last_hangul = 0xD7A3

        result = []
        for char in keyword:
            if char in self.ENGLISH_FINAL:
                result.append(char)
            elif first_hangul <= ord(char) <= last_hangul:
                base_code = ord(char) - first_hangul
                initial_consonant = base_code // (21 * 28)
                medial_vowel = (base_code % (21 * 28)) // 28
                final_consonant = base_code % 28

                result.append(self.INITIAL_CONSONANTS[initial_consonant])
                result.append(self.MEDIAL_VOWELS[medial_vowel])
                result.append(self.FINAL_CONSONANTS[final_consonant])
            else:
                result.append(char)
        return result

    def generateQuestion(self, keyword):
        questionList = []
        for question in self.QUESTIONS:
            if ((self.decomposeHangul(keyword[-1])[-1] != '' and len(self.decomposeHangul(keyword[-1])) == 3)
                    or (self.decomposeHangul(keyword[-1])[-1] in self.ENGLISH_FINAL)):
                question = question.replace('<k>', keyword)
                questionList.append(question)
            else:
                question = (question.replace('<k>을', '<k>를')
                            .replace('<k>이란', '<k>란').replace('<k>이', '<k>가')
                            .replace('<k>과', '<k>와').replace('<k>', keyword))
                questionList.append(question)

        return questionList
