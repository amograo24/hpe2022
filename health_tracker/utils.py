from typing import Union

import pyqrcode
import random
from .models import User


def return_qr_code(uid: str, scale=5) -> Union[str, bytes]:
    code = pyqrcode.create(uid)
    return code.png_as_base64_str(scale=scale)


def gen_unique_id(lower: int = 12, upper: int = 16) -> str:
    _len = random.randint(lower, upper)
    digits = "0123456789"
    code = "".join([random.choice(digits) for _ in range(_len)])
    while User.objects.filter(wbid=code):
        code = "".join([random.choice(digits) for _ in range(_len)])

    user = User.objects.create_user("kushurox", "password@gmail.com", "password", wbid=code,
                                    aadharid="12313", division="D/HCW/MS", )
    user.save()
    return code


if __name__ == "__main__":
    print(gen_unique_id(5, 10))
