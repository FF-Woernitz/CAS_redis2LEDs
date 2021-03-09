# !/usr/bin/python3
import queue
import signal
import threading
import time

import RPi.GPIO as GPIO
from CASlibrary import Config, Logger, RedisMB
from CASlibrary.constants import AlertType
from logbook import INFO, NOTICE, DEBUG

from LEDPatterns import *


class LEDThread(threading.Thread):
    def __init__(self, led, ledqueue, patternDefault):
        super().__init__()
        self.logger = Logger.Logger(self.__class__.__name__).getLogger()
        self.led = led
        self.ledqueue = ledqueue
        self.patternDefault = patternDefault
        self._running = True

    def _executeLEDPattern(self, pattern):
        for stateChar in pattern:
            state = GPIO.input(self.led)
            self.logger.trace(
                "Pin: {} State: {} Nextstate: {}".format(self.led, state, stateChar)
            )
            if int(stateChar) != state:
                GPIO.output(self.led, int(stateChar))
                self.logger.debug("Pin: {} Set: {}".format(self.led, stateChar))
            time.sleep(0.1)

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.led, GPIO.OUT, initial=False)

    def run(self):
        self.logger.info("Setting up GPIO pins")
        self._setup_gpio()
        while self._running:
            item = None
            try:
                item = self.ledqueue.get(block=False)
            except queue.Empty:
                pass
            if item is not None:
                self._executeLEDPattern(item)
            else:
                self._executeLEDPattern(self.patternDefault)

        try:
            self._setup_gpio()
            GPIO.output(self.led, 0)
        except RuntimeError:
            pass

    def stop(self):
        self._running = False

    def is_stopping(self):
        return not self._running


class Redis2LEDs:
    logger = None
    LEDError = None
    LEDError_thread = None
    LEDActive = None
    LEDActive_thread = None
    LEDInput = None
    LEDInput_thread = None
    LEDAlert = None
    LEDAlert_thread = None
    Redis_thread = None

    def __init__(self):
        self.logger = Logger.Logger(self.__class__.__name__).getLogger()

        self.config = Config.Config().getConfig()
        if "gpio" not in self.config:
            raise LookupError('Could not found gpio in config')
        if "led" not in self.config["gpio"]:
            raise LookupError('Could not found led in gpio config')
        self.config = self.config["gpio"]["led"]

        self.redisMB = RedisMB.RedisMB()
        signal.signal(signal.SIGTERM, self.signalhandler)
        signal.signal(signal.SIGHUP, self.signalhandler)

        self.LEDError_queue = queue.Queue(maxsize=64)
        self.LEDActive_queue = queue.Queue(maxsize=64)
        self.LEDInput_queue = queue.Queue(maxsize=64)
        self.LEDAlert_queue = queue.Queue(maxsize=64)

        self.ledpatterns = LEDPatterns(self.logger, self.LEDError_queue, self.LEDActive_queue, self.LEDInput_queue,
                                       self.LEDAlert_queue)

    def log(self, level, log, uuid="No UUID"):
        self.logger.log(level, "[{}]: {}".format(uuid, log))

    def signalhandler(self, signum):
        self.log(INFO, "Signal handler called with signal {}".format(signum))
        for t in [
            self.LEDError_thread,
            self.LEDActive_thread,
            self.LEDInput_thread,
            self.LEDAlert_thread,
        ]:
            try:
                if t is not None:
                    t.stop()
            except:
                pass
        try:
            self.redisMB.exit()
        except:
            pass
        GPIO.cleanup()
        self.log(NOTICE, "exiting...")
        exit()

    def startThreads(self):
        self.log(INFO, "Starting LED threads")
        self.LEDError_thread = LEDThread(
            self.config["LEDError"], self.LEDError_queue, LEDErrorTypes.default
        )
        self.LEDActive_thread = LEDThread(
            self.config["LEDActive"], self.LEDActive_queue, LEDActiveTypes.default
        )
        self.LEDInput_thread = LEDThread(
            self.config["LEDInput"], self.LEDInput_queue, LEDInputTypes.default
        )
        self.LEDAlert_thread = LEDThread(
            self.config["LEDAlert"], self.LEDAlert_queue, LEDAlertTypes.default
        )

        self.LEDError_thread.start()
        self.LEDActive_thread.start()
        self.LEDInput_thread.start()
        self.LEDAlert_thread.start()

    def redisListener(self, data):
        self.log(INFO, "Received new redis message")
        self.log(DEBUG, data)
        message = self.redisMB.decodeMessage(data)
        self.ledpatterns.checkPattern(message)

    def main(self):
        self.startThreads()
        self.Redis_thread = self.redisMB.psubscribeToType('*', self.redisListener)

        for t in [
            self.LEDError_thread,
            self.LEDActive_thread,
            self.LEDInput_thread,
            self.LEDAlert_thread,
            self.Redis_thread,
        ]:
            if t is None:
                continue
            try:
                t.join()
            except KeyboardInterrupt:
                self.signalhandler("KeyboardInterrupt")


if __name__ == "__main__":
    c = Redis2LEDs()
    c.main()
