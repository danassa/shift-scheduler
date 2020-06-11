from backend.data import Data
from utils.hard_drive import restore_old_values
from frontend.events import start
import rook


if __name__ == "__main__":
    rook.start(token='0bad5d6c1ed1db259f87d43f84791bdc868db40376fe7cd8840a8b6a0380703a')
    # i = 0
    # while True:
    #     i = i + 1
    #     x = input()
    #     print(x)
    #     print(i)

    try:
        data = restore_old_values()
    except FileNotFoundError:
        data = Data()

    start(data)
