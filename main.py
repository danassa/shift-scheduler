from src.backend.data import Data
from src.utils.hard_drive import restore_old_values
from src.frontend.events import start
import logging
import sys


logFormatter = logging.Formatter("%(asctime)s %(levelname)s:%(funcName)s %(message)s")
fileHandler = logging.FileHandler(filename="sahar.log", encoding='utf-8')
fileHandler.setFormatter(logFormatter)
streamHandler = logging.StreamHandler()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

sys.setrecursionlimit(10000)

if __name__ == "__main__":

    try:
        data = restore_old_values()
    except FileNotFoundError:
        data = Data()

    try:
        start(data)
    except Exception as e:
        logging.error(e, exc_info=True)
