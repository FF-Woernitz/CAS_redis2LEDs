# Echo led cycle is 0.1 second. 1 = On 0 = Off
from queue import Queue


class LEDErrorTypes:
    default = "0"
    errorZVEI = "1111100000"
    errorFax = "1000010000"


class LEDActivTypes:
    default = "1010000000"


class LEDInputTypes:
    default = "0"
    inputZVEI = "1111100000"
    inputFax = "1000010000"
    inputGPIO = "1001001000"


class LEDAlertTypes:
    default = "0"
    testalertZVEI = "100000000010000000001000000000"
    alertZVEI = "111110000011111000001111100000"
    alertFax = "100001000010000100001000010000"
    alertGPIO = "100100100010010010001001001000"


class LEDPatterns:
    def __init__(self, logger, LEDError_queue: Queue, LEDActiv_queue: Queue, LEDInput_queue: Queue, LEDAlert_queue: Queue):
        self.logger = logger
        self.LEDInput_queue = LEDInput_queue
        self.LEDActiv_queue = LEDActiv_queue
        self.LEDError_queue = LEDError_queue
        self.LEDAlert_queue = LEDAlert_queue

    def _check(self, message: dict, messagePattern: str, queue: Queue, LEDType: str):
        self.logger.debug("Check if message has pattern: {}".format(messagePattern))
        if message["type"] == messagePattern:
            self.logger.info("Message has pattern: {}".format(message["type"]))
            queue.put_nowait(LEDType)

    def checkPattern(self, channel):
        self._check(channel, "inputZVEI", self.LEDInput_queue, LEDInputTypes.inputZVEI)
        self._check(channel, "alertZVEI", self.LEDAlert_queue, LEDAlertTypes.alertZVEI)
        self._check(channel, "errorZVEI", self.LEDError_queue, LEDErrorTypes.errorZVEI)
        self._check(channel, "testalertZVEI", self.LEDAlert_queue, LEDAlertTypes.testalertZVEI)
