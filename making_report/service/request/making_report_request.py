from template.request_generator.base_request import BaseRequest
from user_defined_protocol.protocol import UserDefinedProtocolNumber


class MakingReportRequest(BaseRequest):
    def __init__(self, **kwargs):
        self.__protocolNumber = UserDefinedProtocolNumber.REPORT_MAKING.value


    def getProtocolNumber(self):
        return self.__protocolNumber

    def toDictionary(self):
        return {
            "protocolNumber": self.__protocolNumber
        }

    def __str__(self):
        return f"MakingReportRequest(protocolNumber={self.__protocolNumber})"