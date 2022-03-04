import random
import uuid
from typing import Union

import pyqrcode

from .models import User


def return_qr_code(uid: str, scale=5) -> Union[str, bytes]:
    code = pyqrcode.create(uid)
    return code.png_as_base64_str(scale=scale)


def gen_unique_id(email: str, password: str) -> User:
    _len = 16
    digits = "0123456789"
    code = "".join([random.choice(digits) for _ in range(_len)])
    while User.objects.filter(username=code):  # what does this return?
        code = "".join([random.choice(digits) for _ in range(_len)])

    user = User.objects.create_user(username=code,
                                    password=password,
                                    email=email)
    user.save()
    return user


def get_hcw_vid(email:str, password: str, division: str):
    hcw_vid = uuid.uuid4()
    hcw_vid = str(hcw_vid)[:12]
    while User.objects.filter(username=hcw_vid):
        hcw_vid = uuid.uuid4()
        hcw_vid = str(hcw_vid)[:12]
    user = User.objects.create_user(username=hcw_vid,
                                    password=password,
                                    email=email,
                                    division=division)
    user.save()
    return user


# TODO kushurox: Do file ext checks here before saving
def is_valid_file(file: str) -> bool:
    print(file, str(file))
    return False


if __name__ == "__main__":
    print(str(uuid.uuid4())[:12])
