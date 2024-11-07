import os
import sys
import threading
from functools import partial

import colorama

from user_defined_protocol.register import UserDefinedProtocolRegister

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'template'))

from template.client_socket.service.client_socket_service_impl import ClientSocketServiceImpl
from template.command_analyzer.service.command_analyzer_service_impl import CommandAnalyzerServiceImpl
from template.command_executor.service.command_executor_service_impl import CommandExecutorServiceImpl
from template.conditional_custom_executor.service.conditional_custom_executor_service_impl import ConditionalCustomExecutorServiceImpl
from template.initializer.init_domain import DomainInitializer
from template.os_detector.detect import OperatingSystemDetector
from template.os_detector.operating_system import OperatingSystem
from template.receiver.service.receiver_service_impl import ReceiverServiceImpl
from template.thread_worker.service.thread_worker_service_impl import ThreadWorkerServiceImpl
from template.thread_worker_pool.service.thread_worker_pool_service_impl import ThreadWorkerPoolServiceImpl
from template.transmitter.service.transmitter_service_impl import TransmitterServiceImpl
from template.utility.color_print import ColorPrinter
from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap

DomainInitializer.initEachDomain()
UserDefinedProtocolRegister.registerUserDefinedProtocol()

stop_event = threading.Event()

if __name__ == "__main__":
    colorama.init(autoreset=True)

    responseClassMapInstance = ResponseClassMap.getInstance()
    requestClassMapInstance = RequestClassMap.getInstance()
    requestClassMapInstance.printRequestClassMap()

    detectedOperatingSystem = OperatingSystemDetector.checkCurrentOperatingSystem()
    ColorPrinter.print_important_data("detectedOperatingSystem", detectedOperatingSystem)

    if detectedOperatingSystem is OperatingSystem.UNKNOWN:
        ColorPrinter.print_important_message("범용 운영체제 외에는 실행 할 수 없습니다!")
        exit(1)


    threadWorkerPoolService = ThreadWorkerPoolServiceImpl.getInstance()

    try:
        clientSocketService = ClientSocketServiceImpl.getInstance()
        clientSocket = clientSocketService.createClientSocket()
        clientSocketService.connectToTargetHostUnitSuccess()

        transmitterService = TransmitterServiceImpl.getInstance()
        transmitterService.requestToInjectUserDefinedResponseClassMapInstance(responseClassMapInstance)

        receiverService = ReceiverServiceImpl.getInstance()
        receiverService.requestToInjectUserDefinedRequestClassMapInstance(requestClassMapInstance)

        commandAnalyzerService = CommandAnalyzerServiceImpl.getInstance()
        commandExecutorService = CommandExecutorServiceImpl.getInstance()

        conditionalCustomExecutorService = ConditionalCustomExecutorServiceImpl.getInstance()

        # threadWorkerPoolService = ThreadWorkerPoolServiceImpl.getInstance()
        # TODO: 맥북 m2 스레드 최대 지원 개수가 12개임
        for receiverId in range(3):
            threadWorkerPoolService.executeThreadPoolWorker(
                f"Receiver-{receiverId}",
                partial(receiverService.requestToReceiveCommand, receiverId)
            )

        for analyzerId in range(2):
            threadWorkerPoolService.executeThreadPoolWorker(
                f"CommandAnalyzer-{analyzerId}",
                partial(commandAnalyzerService.analysisCommand, analyzerId)
            )

        for executorId in range(4):
            threadWorkerPoolService.executeThreadPoolWorker(
                f"CommandExecutor-{executorId}",
                partial(commandExecutorService.executeCommand, executorId)
            )

        for conditionalCustomExecutorId in range(2):
            threadWorkerPoolService.executeThreadPoolWorker(
                f"ConditionalCustomExecutor-{conditionalCustomExecutorId}",
                partial(conditionalCustomExecutorService.executeConditionalCustomCommand,
                        conditionalCustomExecutorId)
            )

        threadWorkerPoolService.executeThreadPoolWorker(
            "Transmitter-0",
            partial(transmitterService.requestToTransmitResult, 0)  # 단일 ID 사용
        )

        # 프로그램 종료를 위한 이벤트 대기
        while not stop_event.is_set():
            threading.Event().wait(1)  # 1초 대기

    except Exception as e:
        ColorPrinter.print_important_message(f"An error occurred: {e}")

    finally:
        # 스레드 풀 종료
        threadWorkerPoolService.shutdownAll()