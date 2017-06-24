"""
Decorators

Xiuming Zhang, MIT CSAIL
April 2017
"""

from time import time, sleep
from os import makedirs
from os.path import abspath, join, dirname
import logging

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


def timeit(somefunc):
    """
    Outputs the time a function takes to execute
    """
    thisfunc = thisfile + '->@timeit'

    def wrapper(*arg, **kwargs):
        funcname = somefunc.__name__
        logging.info("%s: Function %s started", thisfunc, funcname)
        t0 = time()
        results = somefunc(*arg, **kwargs)
        t = time() - t0
        logging.info("%s: Function %s done in %.2f seconds", thisfunc, funcname, t)
        return results

    return wrapper


def existok(makedirs_func):
    """
    Implements the exist_ok flag in >= 3.2, which avoids race conditions,
    where one parallel worker checks the folder doesn't exist and wants to
    create it with another worker doing so faster
    """
    thisfunc = thisfile + '->@existok'

    def wrapper(*args, **kwargs):
        try:
            makedirs_func(*args, **kwargs)
        except OSError as e:
            if e.errno != 17:
                raise
            logging.debug("%s: %s already exists, but that is OK", thisfunc, args[0])
    return wrapper


# Tests
if __name__ == '__main__':
    # timeit
    @timeit
    def findsums(x, y, z):
        sleep(1)
        return x + y, x + z, y + z, x + y + z
    print(findsums(1, 2, 3))
    # existok
    newdir = join(dirname(__file__), 'test')
    makedirs = existok(makedirs)
    makedirs(newdir)
    makedirs(newdir)
