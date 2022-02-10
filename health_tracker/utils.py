from typing import Union
import random
import uuid

import pyqrcode
from .models import Patients, User, MedWorkerRep


def return_qr_code(uid: str, scale=5) -> Union[str, bytes]:
    code = pyqrcode.create(uid)
    return code.png_as_base64_str(scale=scale)


def gen_unique_id(email: str, password: str, lower: int = 12, upper: int = 16) -> User:
    _len = random.randint(lower, upper)
    digits = "0123456789"
    code = "".join([random.choice(digits) for _ in range(_len)])
    while User.objects.filter(username=code):  # what does this return?
        code = "".join([random.choice(digits) for _ in range(_len)])

    user = User.objects.create_user(username=code,
                                    password=password,
                                    email=email)
    user.save()
    return user


def get_hcw_vid(reg_no: str, dept: str, account: User):
    hcw_vid = uuid.uuid4()
    hcw_vid = str(hcw_vid)[:10]
    while MedWorkerRep.objects.filter(hcwvid=hcw_vid):
        hcw_vid = uuid.uuid4()
        hcw_vid = str(hcw_vid)[:10]
    mwr = MedWorkerRep(department=dept, reg_no=reg_no, account=account, hcwvid=hcw_vid)
    mwr.save()
    return hcw_vid


if __name__ == "__main__":
    print(str(uuid.uuid4())[:11])
