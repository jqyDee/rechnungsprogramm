import os
import shutil
import sys
import time
import logging
import urllib.request
from urllib.error import URLError, HTTPError


class Updater:
    version = '2.2.0-beta'
    sleep_time = 10
    downloaded_version_file = False
    downloaded_pip_requirements_file = False
    downloaded_new_version_file = False

    def __del__(self):
        """garbage collection and making sure all threads are closed.
        Passing response into queue"""

        # terminate all while loops
        self.running = False

        try:
            self.queue.put([self.downloaded_version_file, self.downloaded_pip_requirements_file, self.downloaded_new_version_file])
            logging.debug('item put in queue')
        except AttributeError:
            logging.debug("item couldn't be put in queue, passing")
            logging.info(f'"queue" item = {[self.downloaded_version_file, self.downloaded_pip_requirements_file, self.downloaded_new_version_file]}')
            pass

        logging.info('updater.py finished')

    def __init__(self, queue):
        self.queue = queue
        self.running = True

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logging.info('updater.py started')

        try:
            self.main_program_version = self.queue.get(block=False, timeout=10)
            logging.debug('queue item received')
        except AttributeError:
            # DEBUGGING
            logging.debug("queue item couldn't be received, using given parameter")
            self.main_program_version = self.queue

        if self.download_version_file():
            data = self.extract_version_file_data()
            if self.download_pip_requirements_file(data):
                self.install_pip_requirements()
                if self.download_new_program_file(data):
                    self.install_new_program_version()

    def download_version_file(self) -> bool:
        """Downloads the version file from remote and puts it in the
        tmp folder"""

        logging.debug('Updater.download_version_file() called')

        i = 0
        while self.running and i < 5:
            i += 1
            try:
                logging.info('HTTP: trying to fetch version.txt')
                urllib.request.urlretrieve('http://rechnungsprogramm.ffischh.de/version.txt', './system/tmp/version.txt.tmp')
            except HTTPError as e:
                logging.error('Error code: ', e.code)
                time.sleep(self.sleep_time)
                self.downloaded_version_file = False
            except URLError as e:
                logging.error('Reason: ', e.reason)
                time.sleep(self.sleep_time)
                self.downloaded_version_file = False
            else:
                logging.info('HTTP request good!')
                self.downloaded_version_file = True
                break

        return self.downloaded_version_file

    def extract_version_file_data(self) -> list:
        """extracts the data out of the downloaded local version file
        in the tmp directory"""

        logging.debug('Updater.extract_version_file_data() called')

        data = []
        with open('./system/tmp/version.txt.tmp', 'r') as f:
            for i in f.readlines():
                data.append(i.replace('\n', ''))

        if os.path.exists('./system/tmp/version.txt.tmp'):
            os.remove('./system/tmp/version.txt.tmp')

        return data

    def download_pip_requirements_file(self, data: list) -> bool:
        """Downloads the pip requirements file from remote and puts it in the
        tmp folder"""

        logging.debug('Updater.download_pip_requirements_file() called')

        i = 0
        while self.running and i < 5:
            i += 1
            try:
                logging.info('HTTP: trying to fetch requirements.txt')
                urllib.request.urlretrieve(data[4], './system/tmp/requirements.txt.tmp')
            except HTTPError as e:
                logging.error('Error code: ', e.code)
                time.sleep(self.sleep_time)
                self.downloaded_pip_requirements_file = False
            except URLError as e:
                logging.error('Reason: ', e.reason)
                time.sleep(self.sleep_time)
                self.downloaded_pip_requirements_file = False
            else:
                logging.info('HTTP request good!')
                self.downloaded_pip_requirements_file = True
                break

        return self.downloaded_pip_requirements_file

    def install_pip_requirements(self):
        """Installs the pip requirements from the requirements.txt
        in the tmp folder"""

        logging.debug('Updater.install_pip_requirements() called')

        os.system('pip install --upgrade pip')
        os.system('pip install -r ./system/tmp/requirements.txt.tmp')

        if os.path.exists('./system/tmp/requirements.txt.tmp'):
            os.remove('./system/tmp/requirements.txt.tmp')

    def download_new_program_file(self, data: list) -> bool:
        """Downloads the newest main program file from remote and puts it
        in the tmp folder"""

        logging.debug('Updater.download_new_program_file() called')

        i = 0
        while self.running and i < 5:
            i += 1
            if data[1] != self.main_program_version:
                try:
                    logging.info('HTTP: trying to fetch main.py')
                    urllib.request.urlretrieve(data[1], './system/tmp/main.py.tmp')
                except HTTPError as e:
                    logging.error('Error code: ', e.code)
                    time.sleep(self.sleep_time)
                    self.downloaded_new_version_file = False
                except URLError as e:
                    logging.error('Reason: ', e.reason)
                    time.sleep(self.sleep_time)
                    self.downloaded_new_version_file = False
                else:
                    logging.info('HTTP request good!')
                    self.downloaded_new_version_file = True
                    break

        return self.downloaded_new_version_file

    def install_new_program_version(self):
        """Installs the newest program file in the root directory"""

        shutil.move('./system/tmp/main.py.tmp', 'main.pyw')


if __name__ == '__main__':
    Updater(1)
