# !/usr/bin/python3
import time, requests, pprint, signal, threading, queue
from datetime import datetime
from logbook import INFO, NOTICE, WARNING
from CASlib import Config, Logger, RedisMB, Helper
from pprint import pprint
from .Constans import LED1_types

class redis2LEDs():
    logger = None
    queueLED1 = None
    queueLED1_thread = None
    queueLED2 = None
    queueLED2_thread = None
    queueLED3 = None
    queueLED3_thread = None
    queueLED4 = None
    queueLED4_thread = None

    def __init__(self):
        self.logger = Logger.Logger(self.__class__.__name__).getLogger()
        self.config = Config.Config().getConfig()
        self.redisMB = RedisMB.RedisMB()
        self.helper = Helper.Helper()
        signal.signal(signal.SIGTERM, self.signalhandler)
        signal.signal(signal.SIGHUP, self.signalhandler)

        self.queueLED1 = queue.Queue()
        self.queueLED2 = queue.Queue()
        self.queueLED3 = queue.Queue()
        self.queueLED4 = queue.Queue()

    def log(self, level, log, uuid="No UUID"):
        self.logger.log(level, "[{}]: {}".format(uuid, log))

    def signalhandler(self, signum, frame):
        self.log(INFO, 'Signal handler called with signal {}'.format(signum))
        for t in [self.queueLED1_thread, self.queueLED2_thread, self.queueLED3_thread, self.queueLED4_thread]:
            try:
                if t is not None:
                    t.kill()
                self.redisMB.exit()
            except:
                pass
        try:
            self.redisMB.exit()
        except:
            pass

        self.log(NOTICE, 'exiting...')
        exit()

    def threadLED1(self):

    def startThreads(self):
        x = threading.Thread(target=self.threadLED1)

    def main(self):
        pass


if __name__ == '__main__':
    c = redis2LEDs()
    c.main()
