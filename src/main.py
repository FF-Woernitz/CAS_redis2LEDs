# !/usr/bin/python3
import time, signal, threading, queue, os
from logbook import INFO, NOTICE
from CASlib import Config, Logger, RedisMB, Helper
from pprint import pprint
from .LEDPatterns import *
import RPi.GPIO as GPIO


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
                self.logger.debug("Pin: {} Set: {}".format(self.led, 1))
            time.sleep(0.1)

    def _setup_gpio(self):
        self.logger.info("Setting up GPIO pins")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.led, GPIO.OUT, initial=False)

    def run(self):
        self._setup_gpio()
        while self._running:
            item = None
            try:
                item = self.ledqueue.get(block=False)
            except queue.Empty:
                pass
            if item is not None:
                self._executeLEDPattern(item)
                self.ledqueue.done()
            else:
                self._executeLEDPattern(self.patternDefault)

        GPIO.output(self.led, 0)

    def stop(self):
        self._running = False

    def is_stopping(self):
        return not self._running


class Redis2LEDs:
    logger = None
    LEDError = None
    LEDError_thread = None
    LEDActiv = None
    LEDActiv_thread = None
    LEDInput = None
    LEDInput_thread = None
    LEDAlert = None
    LEDAlert_thread = None
    Redis_thread = None

    def __init__(self):
        self.logger = Logger.Logger(self.__class__.__name__).getLogger()
        self.config = Config.Config().getConfig()
        self.config = self.config["leds"]
        self.redisMB = RedisMB.RedisMB()
        self.helper = Helper.Helper()
        signal.signal(signal.SIGTERM, self.signalhandler)
        signal.signal(signal.SIGHUP, self.signalhandler)

        self.LEDError_queue = queue.Queue()
        self.LEDActiv_queue = queue.Queue()
        self.LEDInput_queue = queue.Queue()
        self.LEDAlert_queue = queue.Queue()

        self.ledpatterns = LEDPatterns(self.LEDError_queue, self.LEDActiv_queue, self.LEDInput_queue, self.LEDAlert_queue)

    def log(self, level, log, uuid="No UUID"):
        self.logger.log(level, "[{}]: {}".format(uuid, log))

    def signalhandler(self, signum, frame):
        self.log(INFO, "Signal handler called with signal {}".format(signum))
        for t in [
            self.LEDError_thread,
            self.LEDActiv_thread,
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
        self.LEDActiv_thread = LEDThread(
            self.config["LEDActiv"], self.LEDActiv_queue, LEDActivTypes.default
        )
        self.LEDInput_thread = LEDThread(
            self.config["LEDInput"], self.LEDInput_queue, LEDInputTypes.default
        )
        self.LEDAlert_thread = LEDThread(
            self.config["LEDAlert"], self.LEDAlert_queue, LEDAlertTypes.default
        )

        self.LEDError_thread.start()
        self.LEDActiv_thread.start()
        self.LEDInput_thread.start()
        self.LEDAlert_thread.start()

    def redisListener(self, message):
        self.ledpatterns.checkPattern(message['channel'])

    def main(self):
        self.startThreads()
        self.redisMB.psubscribeToType('*', self.redisListener)

        for t in [
            self.LEDError_thread,
            self.LEDActiv_thread,
            self.LEDInput_thread,
            self.LEDAlert_thread,
            self.Redis_thread,
        ]:
            if t is None:
                continue
            t.join()


if __name__ == "__main__":
    print("V1")
    c = Redis2LEDs()
    c.main()
