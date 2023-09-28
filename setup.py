import os
import time
import logging
import urllib.request
from urllib.error import URLError, HTTPError


class Setup:
    version = '2.0.0-beta'
    sleep_time = 5
    data = []

    def __del__(self):
        tmp_files = os.listdir('./system/tmp/')
        for i in tmp_files:
            os.remove(f'./system/tmp/{i}')

    def __init__(self):
        if not os.path.exists('./system/tmp/'):
            os.makedirs('./system/tmp/')

        if not os.path.isfile('main.py'):
            self.read_version_file()
            self.install_pip_requirements()
            self.download_main_program()

    def read_version_file(self):
        try:
            urllib.request.urlretrieve('https://ffischh.de/version.txt', './system/tmp/version.txt.tmp')
        except HTTPError as e:
            logging.error('Error code: ', e.code)
            time.sleep(self.sleep_time)
        except URLError as e:
            logging.error('Reason: ', e.reason)
            time.sleep(self.sleep_time)
        else:
            logging.info('HTTP request good!')
            with open('./system/tmp/version.txt.tmp', 'r') as f:
                for i in f.readlines():
                    self.data.append(i.replace('\n', ''))

    def install_pip_requirements(self):
        try:
            urllib.request.urlretrieve(self.data[4], './system/tmp/requirements.txt.tmp')
        except HTTPError as e:
            logging.error('Error code: ', e.code)
            time.sleep(self.sleep_time)
        except URLError as e:
            logging.error('Reason: ', e.reason)
            time.sleep(self.sleep_time)
        else:
            logging.info('HTTP request good!')

            os.system('pip install -r ./system/tmp/requirements.txt.tmp')

    def download_main_program(self):
        try:
            urllib.request.urlretrieve(self.data[1], 'main.pyw')
        except HTTPError as e:
            logging.error('Error code: ', e.code)
            time.sleep(self.sleep_time)
        except URLError as e:
            logging.error('Reason: ', e.reason)
            time.sleep(self.sleep_time)
        else:
            logging.info('HTTP request good!')


if __name__ == '__main__':
    setup = Setup()
