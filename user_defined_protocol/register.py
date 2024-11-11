import os
import sys

from making_report.service.making_report_service_impl import MakingReportServiceImpl
from making_report.service.request.making_report_request import MakingReportRequest
from making_report.service.response.making_report_response import MakingReportResponse
from polyglot_question.service.polyglot_question_service_impl import PolyglotQuestionServiceImpl
from polyglot_question.service.request.polyglot_question_request import PolyglotQuestionRequest
from polyglot_question.service.response.polyglot_question_response import PolyglotQuestionResponse
from polyglot_score.service.polyglot_score_service_impl import PolyglotScoreServiceImpl
from polyglot_score.service.request.polyglot_score_request import PolyglotScoreRequest
from polyglot_score.service.response.polyglot_score_response import PolyglotScoreResponse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'template'))

from template.custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl
from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap

from user_defined_protocol.protocol import UserDefinedProtocolNumber


class UserDefinedProtocolRegister:
    @staticmethod
    def registerPolyglotQuestionProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        polyglotQuestionService = PolyglotQuestionServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.POLYGLOT_QUESTION,
            PolyglotQuestionRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.POLYGLOT_QUESTION,
            PolyglotQuestionResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.POLYGLOT_QUESTION,
            polyglotQuestionService.generateNextQuestion
        )

    @staticmethod
    def registerPolyglotScoreProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        polyglotScoreService = PolyglotScoreServiceImpl.getInstance()

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
            polyglotScoreService.scoreUserAnswer
        )

    @staticmethod
    def registerReportMakingProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        reportService = MakingReportServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.REPORT_MAKING,
            MakingReportRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.REPORT_MAKING,
            MakingReportResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.REPORT_MAKING,
            reportService.makingReport
        )

    @staticmethod
    def registerReportUpdatingProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        reportService = MakingReportServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.REPORT_UPDATING,
            MakingReportRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.REPORT_UPDATING,
            MakingReportResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.REPORT_UPDATING,
            reportService.makingReport
        )



    @staticmethod
    def registerUserDefinedProtocol():
        UserDefinedProtocolRegister.registerPolyglotQuestionProtocol()
        UserDefinedProtocolRegister.registerPolyglotScoreProtocol()
        UserDefinedProtocolRegister.registerReportMakingProtocol()
