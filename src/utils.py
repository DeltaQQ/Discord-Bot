import time


def timer(function):
    def wrapper(*arg, **kwargs):
        t1 = time.time()
        function(*arg, **kwargs)
        t2 = time.time()
        print(function.__name__, 'took', t2 - t1, 's')
    return wrapper
