from typing import Union

import pyqrcode
import random


def return_qr_code(uid: str, scale=5) -> Union[str, bytes]:
    code = pyqrcode.create(uid)
    return code.png_as_base64_str(scale=scale)


def gen_unique_id(lower: int, upper: int) -> str:
    _len = random.randint(lower, upper)
    digits = "0123456789"
    # Do the Check logic here if the code already exists
    return "".join([random.choice(digits) for _ in range(_len)])


if __name__ == "__main__":
    print(gen_unique_id(5, 10))
