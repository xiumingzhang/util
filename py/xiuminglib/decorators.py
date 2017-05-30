import time
import os
import logging


logging.basicConfig(level=logging.INFO)
thisFile = os.path.abspath(__file__)


def timeIt(someFunc):
    """
    Outputs the time a function takes to execute
    """
    def wrapper(*arg, **kwargs):
        t0 = time.time()
        results = someFunc(*arg, **kwargs)
        t = time.time() - t0
        funcName = someFunc.__name__
        logging.info(
            "%s: Function %s takes %.2f seconds", thisFile, funcName, t
        )
        return results
    return wrapper


def existOK(makedirsFunc):
    """
    Implements the exist_ok flag in >= 3.2, which avoids race conditions,
    where one parallel worker checks the folder doesn't exist and wants to
    create it with another worker doing so faster
    """
    def wrapper(*args, **kwargs):
        try:
            makedirsFunc(*args, **kwargs)
        except OSError as e:
            if e.errno != 17:
                raise
            logging.debug(
                "%s: %s already exists, but that is OK", thisFile, args[0]
            )
    return wrapper


# Tests
if __name__ == '__main__':
    # timeIt
    @timeIt
    def findSums(x, y, z):
        time.sleep(1)
        return x + y, x + z, y + z, x + y + z
    print(findSums(1, 2, 3))
    # existOK
    newDir = os.path.join(os.path.dirname(__file__), 'test')
    makedirs = existOK(os.makedirs)
    makedirs(newDir)
    makedirs(newDir)
