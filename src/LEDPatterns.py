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
    alertZVEI = "1111100000"
    alertFax = "1000010000"
    alertGPIO = "1001001000"


class LEDPatterns:
    def __init__(self, LEDError_queue: Queue, LEDActiv_queue: Queue, LEDInput_queue: Queue, LEDAlert_queue: Queue):
        self.LEDInput_queue = LEDInput_queue
        self.LEDActiv_queue = LEDActiv_queue
        self.LEDError_queue = LEDError_queue
        self.LEDAlert_queue = LEDAlert_queue

    def _check(self, channel: str, channelPattern: str, queue: Queue, type: str):
        if channel.lower().strip() is channelPattern.lower().strip():
            queue.put(type)

    def checkPattern(self, channel):
        self._check(channel, "inputZVEI", self.LEDInput_queue, LEDInputTypes.inputZVEI)
        self._check(channel, "alertZVEI", self.LEDAlert_queue, LEDAlertTypes.alertZVEI)
