import threading
import time


class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, refresh_interval=10):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """

        self.interval = refresh_interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        """ Method that runs forever """
        while True:

            print('Doing something important in the background')

            time.sleep(self.interval)

example = ThreadingExample(refresh_interval=10)

while True:
    time.sleep(5)
