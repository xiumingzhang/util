import time
import os
import logging
logging.basicConfig(level=logging.INFO)
thisfile = os.path.abspath(__file__)


def timeit(somefunc):
    """
    Outputs the time a function takes to execute
    """
    def wrapper(*arg, **kwargs):
        t0 = time.time()
        results = somefunc(*arg, **kwargs)
        t = time.time() - t0
        funcname = somefunc.__name__
        logging.info("%s: Function %s takes %.2f seconds", thisfile, funcname, t)
        return results
    return wrapper


def existok(makedirs_func):
    """
    Implements the exist_ok flag in >= 3.2, which avoids race conditions,
    where one parallel worker checks the folder doesn't exist and wants to
    create it with another worker doing so faster
    """
    def wrapper(*args, **kwargs):
        try:
            makedirs_func(*args, **kwargs)
        except OSError as e:
            if e.errno != 17:
                raise
            logging.debug("%s: %s already exists, but that is OK", thisfile, args[0])
    return wrapper


# Tests
if __name__ == '__main__':
    # timeit
    @timeit
    def findsums(x, y, z):
        time.sleep(1)
        return x + y, x + z, y + z, x + y + z
    print(findsums(1, 2, 3))
    # existok
    newdir = os.path.join(os.path.dirname(__file__), 'test')
    makedirs = existok(os.makedirs)
    makedirs(newdir)
    makedirs(newdir)
