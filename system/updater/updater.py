import time


class Updater:
    version = '1.0.0'

    def __init__(self):
        print(1)
        for i in range(100):
            print(i)
            time.sleep(5)


if __name__ == '__main__':
    updater = Updater()
