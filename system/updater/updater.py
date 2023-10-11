import os
import shutil
import sys
import time
import logging
import urllib.request
from urllib.error import URLError, HTTPError


class Updater:
    version = '2.1.0-beta'
    sleep_time = 30
    installed_pip = False
    installed_new_version = False

    def __del__(self):
        self.running = False

        try:
            self.queue.put([self.installed_version_tmp, self.installed_pip, self.installed_new_version])
        except AttributeError:
            pass

        logging.info('updater.py finished')

    def __init__(self, queue):
        self.queue = queue

        try:
            self.main_program_version = self.queue.get(block=False, timeout=10)
        except AttributeError:
            self.main_program_version = self.queue

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

        logging.info('updater.py started')

        self.running = True

        i = 0
        while self.running and i < 5:
            i += 1
            try:
                urllib.request.urlretrieve('https://ffischh.de/version.txt', './system/tmp/version.txt.tmp')
            except HTTPError as e:
                logging.error('Error code: ', e.code)
                time.sleep(self.sleep_time)
                self.installed_version_tmp = False
            except URLError as e:
                logging.error('Reason: ', e.reason)
                time.sleep(self.sleep_time)
                self.installed_version_tmp = False
            else:
                logging.info('HTTP request good!')
                with open('./system/tmp/version.txt.tmp', 'r') as f:
                    data = []
                    for i in f.readlines():
                        data.append(i.replace('\n', ''))
                self.installed_version_tmp = True
                break

        if self.installed_version_tmp:
            self.install_pip_requirements(data)

        if self.installed_version_tmp and self.installed_pip:
            self.install_program_update(data)

    def install_pip_requirements(self, data):
        os.system('pip install --upgrade pip')

        i = 0
        while self.running and i < 5:
            i += 1
            try:
                urllib.request.urlretrieve(data[4], './system/tmp/requirements.txt.tmp')
            except HTTPError as e:
                logging.error('Error code: ', e.code)
                time.sleep(self.sleep_time)
                self.installed_pip = False
            except URLError as e:
                logging.error('Reason: ', e.reason)
                time.sleep(self.sleep_time)
                self.installed_pip = False
            else:
                logging.info('HTTP request good!')
                os.system('pip install -r ./system/tmp/requirements.txt.tmp')
                self.installed_pip = True
                break

        if os.path.exists('./system/tmp/requirements.txt.tmp'):
            os.remove('./system/tmp/requirements.txt.tmp')

    def install_program_update(self, data):
        if os.path.exists('./system/tmp/main.py.tmp'):
            os.remove('./system/tmp/main.py.tmp')

        i = 0
        while self.running and i < 5:
            i += 1
            if data[1] != self.main_program_version:
                try:
                    urllib.request.urlretrieve(data[1], './system/tmp/main.py.tmp')
                except HTTPError as e:
                    logging.error('Error code: ', e.code)
                    time.sleep(self.sleep_time)
                    self.installed_new_version = False
                except URLError as e:
                    logging.error('Reason: ', e.reason)
                    time.sleep(self.sleep_time)
                    self.installed_new_version = False
                else:
                    logging.info('HTTP request good!')
                    shutil.move('./system/tmp/main.py.tmp', 'main.pyw')
                    self.installed_new_version = True
                    break


if __name__ == '__main__':
    Updater(1)
