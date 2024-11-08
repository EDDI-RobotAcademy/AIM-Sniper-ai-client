from enum import Enum


class UserDefinedProtocolNumber(Enum):
    # 예약된 정보 (1, 2, 11, 12, 13, 21) 을 제외하고 사용하도록 함
    POLYGLOT_QUESTION = 7
    POLYGLOT_SCORE = 8
    REPORT_MAKING = 50

    @classmethod
    def hasValue(cls, value):
        return any(value == item.value for item in cls)
