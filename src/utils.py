import time


def timer(function):
    def wrapper(*arg, **kwargs):
        t1 = time.time()
        function(*arg, **kwargs)
        t2 = time.time()
        print(function.__name__, 'took', t2 - t1, 's')
    return wrapper


class Data:
    def __init__(self):
        self.m_ingame_class_list = ['Mage', 'Archer', 'Priest', 'Nightwalker', 'Warrior']