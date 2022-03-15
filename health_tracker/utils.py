import os
import random
import uuid
from typing import Union
import qrcode
from PIL import Image

from .models import User


def return_qr_code(uid: str):
    icon = Image.open("health_tracker/static/health_tracker/temo.jpg")
    icon.thumbnail((128, 128), Image.ANTIALIAS)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=25)
    qr.add_data(uid)
    qr.make()
    img = qr.make_image(fill_color="blue").convert('RGB')
    pos = ((img.size[0] - icon.size[0])//2, (img.size[1] - icon.size[1])//2)
    img.paste(icon, pos)



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
    hcw_vid = str(hcw_vid)[:11]
    while User.objects.filter(username=hcw_vid):
        hcw_vid = uuid.uuid4()
        hcw_vid = str(hcw_vid)[:11]
    user = User.objects.create_user(username=hcw_vid,
                                    password=password,
                                    email=email,
                                    division=division)
    user.save()
    return user

def is_valid_file(file: str) -> bool:
    approved = ["docx", "pdf", "jpg", "jpeg", "png", "pptx", "ppt", "xlsx", "xls", "txt", "mp4", "avi", "mov", "mp3", "key"]
    file = str(file)

    if "." not in file:
        print(file)
        return False

    f_ext = file[file.rfind(".")+1:]
    if f_ext not in approved:
        return False

    return True


def filter_files(files: list, mode: str) -> list:
    if mode == "def":
        return files
    return [f for f in files if f.file_type == mode]


def sort_files(files: list, mode: str) -> list:
    if mode == "def":
        return files

    elif mode == "ft":

        exts = {f.file_type: [] for f in files}
        for file in files:
            exts[file.file_type].append(file)
        nfs = []
        for v in exts.values():
            nfs.extend(v)
        return nfs

    elif mode == "az":
        fs = [f for f in files]
        return sorted(fs, key=lambda x: str(x))

if __name__ == "__main__":
    print(str(uuid.uuid4())[:12])
