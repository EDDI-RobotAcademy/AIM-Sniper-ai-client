import os
import sys

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
    def registerUserDefinedProtocol():
        UserDefinedProtocolRegister.registerTestProtocol()
