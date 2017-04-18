import time


def timeIt(someFunc):
    """
    Outputs the time a function takes to execute
    """
    def wrapper(*arg, **kwargs):
        t0 = time.time()
        results = someFunc(*arg, **kwargs)
        t = time.time() - t0
        funcName = someFunc.__name__
        print("Function %s takes %.2f seconds" % (funcName, t))
        return results
    return wrapper


# Tests
if __name__ == '__main__':
    @timeIt
    def findSums(x, y, z):
        time.sleep(2)
        return x + y, x + z, y + z, x + y + z
    print(findSums(1, 2, 3))
