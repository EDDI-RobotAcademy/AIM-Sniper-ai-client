import os
import sys

from polyglot_temp.service.polyglot_service_impl import PolyglotServiceImpl
from polyglot_temp.service.request.polyglot_request import PolyglotRequest
from polyglot_temp.service.response.polyglot_response import PolyglotResponse
from polyglot_temp.service.request.polyglot_score_request import PolyglotScoreRequest
from polyglot_temp.service.response.polyglot_score_response import PolyglotScoreResponse
from test.service.request.test_request import TestRequest
from test.service.response.test_response import TestResponse
from test.service.test_service_impl import TestServiceImpl

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'template'))

from template.custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl
from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap

from user_defined_protocol.protocol import UserDefinedProtocolNumber


class UserDefinedProtocolRegister:
    @staticmethod
    def registerTestProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        testService = TestServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.TEST,
            TestRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.TEST,
            TestResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.TEST,
            testService.printTestWord
        )

    @staticmethod
    def registerPolyglotProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        polyglotService = PolyglotServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.POLYGLOT,
            PolyglotRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.POLYGLOT,
            PolyglotResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.POLYGLOT,
            polyglotService.generateNextQuestion
        )

    @staticmethod
    def registerPolyglotScoreProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        polyglotService = PolyglotServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.POLYGLOT_SCORE,
            PolyglotScoreRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.POLYGLOT_SCORE,
            PolyglotScoreResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.POLYGLOT_SCORE,
            polyglotService.scoreUserAnswer
        )

    @staticmethod
    def registerUserDefinedProtocol():
        UserDefinedProtocolRegister.registerTestProtocol()
        UserDefinedProtocolRegister.registerPolyglotProtocol()
        UserDefinedProtocolRegister.registerPolyglotScoreProtocol()
