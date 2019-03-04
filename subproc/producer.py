import random
import time
import string


if __name__ == "__main__":
    for i in range(5):
        time.sleep(random.random() * 2)
        s = "".join(random.choice(string.ascii_letters) for _ in range(10))
        print(s)
