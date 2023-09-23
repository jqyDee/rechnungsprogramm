import os
import shutil
import sys
import time
import logging
import urllib.request
from urllib.error import URLError, HTTPError


class Updater:
    version = '1.0.0'

    def __init__(self, program_version):
        self.program_version = program_version

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

        self.running = True

        while self.running:
            try:
                urllib.request.urlretrieve('https://ffischh.de/version.txt', './system/tmp/version.txt.tmp')
            except HTTPError as e:
                logging.error('Error code: ', e.code)
                time.sleep(60)
            except URLError as e:
                logging.error('Reason: ', e.reason)
                time.sleep(60)
            else:
                logging.info('HTTP request good!')
                with open('./system/tmp/version.txt.tmp', 'r') as f:
                    data = []
                    for i in f.readlines():
                        data.append(i.replace('\n', ''))
                break

        self.install_pip_requirements(data)
        self.install_program_update(data)

    def __del__(self):
        self.running = False
        logging.info('Updater finished')

    def install_pip_requirements(self, data):
        os.system('pip install --upgrade pip')

        while self.running:
            try:
                urllib.request.urlretrieve(data[4], './system/tmp/requirements.txt.tmp')
            except HTTPError as e:
                logging.error('Error code: ', e.code)
                time.sleep(60)
            except URLError as e:
                logging.error('Reason: ', e.reason)
                time.sleep(60)
            else:
                logging.info('HTTP request good!')

                os.system('pip install -r ./system/tmp/requirements.txt.tmp')
                break

        if os.path.exists('./system/tmp/requirements.txt.tmp'):
            os.remove('./system/tmp/requirements.txt.tmp')

    def install_program_update(self, data):
        if os.path.exists('./system/tmp/main.py.tmp'):
            os.remove('./system/tmp/main.py.tmp')

        while self.running:
            if data[1] != self.program_version:
                try:
                    urllib.request.urlretrieve(data[1], './system/tmp/main.py.tmp')
                except HTTPError as e:
                    logging.error('Error code: ', e.code)
                    time.sleep(60)
                except URLError as e:
                    logging.error('Reason: ', e.reason)
                    time.sleep(60)
                else:
                    logging.info('HTTP request good!')

                    shutil.move('./system/tmp/main.py.tmp', './main.py')
                    break


if __name__ == '__main__':
    Updater(sys.argv)
