# Echo led cycle is 0.1 second. 1 = On 0 = Off
from queue import Queue

from logbook import DEBUG, INFO

from CASlibrary.constants import AlertType



class LEDErrorTypes:
    default = "0"
    errorZVEI = "1111100000"
    errorFax = "1000010000"


class LEDActiveTypes:
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
    def __init__(self, logger, LEDError_queue: Queue, LEDActive_queue: Queue, LEDInput_queue: Queue,
                 LEDAlert_queue: Queue):
        self.logger = logger
        self.LEDInput_queue = LEDInput_queue
        self.LEDActive_queue = LEDActive_queue
        self.LEDError_queue = LEDError_queue
        self.LEDAlert_queue = LEDAlert_queue

    def _log(self, level, log, uuid="No UUID"):
        self.logger.log(level, "[{}]: {}".format(uuid, log))

    def _check(self, message: dict, channel: str, type: str, queue: Queue, LEDType: str):
        if type:
            self._log(DEBUG, "Check if message is from channel: {} and has type {}:".format(channel, type),
                      message["uuid"])
            if message["channel"] == channel and "type" in message["message"] and message["message"]["type"] == type:
                self._log(INFO,
                          "Message has channel: {} and type: {}".format(message["channel"], message["message"]["type"]),
                          message["uuid"])
                queue.put_nowait(LEDType)
        else:
            self._log(DEBUG, "Check if message is from channel: {} and has any type".format(channel), message["uuid"])
            if message["channel"] == channel:
                self._log(INFO, "Message has channel: {}".format(message["channel"]), message["uuid"])
                queue.put_nowait(LEDType)

    def checkPattern(self, message):
        self._check(message, "input", AlertType.ZVEI, self.LEDInput_queue, LEDInputTypes.inputZVEI)
        self._check(message, "alert", AlertType.ZVEI, self.LEDAlert_queue, LEDAlertTypes.alertZVEI)
        self._check(message, "error", AlertType.ZVEI, self.LEDError_queue, LEDErrorTypes.errorZVEI)
        self._check(message, "test", AlertType.ZVEI, self.LEDAlert_queue, LEDAlertTypes.testalertZVEI)
