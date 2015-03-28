import requests
import shutil
import os
from multiprocessing import Lock

IP = '100.89.50.123'
PORT = '8080'
PROTO = 'http'
ADDR = '{}://{}:{}'.format(PROTO, IP, PORT)
STORAGE_DIR = 'images'
img_dir = None

ENDPOINTS = {
    'video':'/video',
    'audio':'/audio.wav',
    'focus':'/focus',
    'nofocus':'/nofocus',
    'image':'/shot.jpg'
}

scanning = False

camera_lock = Lock()

def switch_to_next_dir():
    global img_dir
    img_dir = STORAGE_DIR + '/{}/'.format(get_next_dir_number())
    make_dir_if_not_exists(img_dir)

def get_next_dir_number():
    first_number = 1
    subdirs = []
    for i in os.walk(STORAGE_DIR):
        name = i[0]
        if name.startswith(STORAGE_DIR):
            name = name.replace(STORAGE_DIR,'')[1:]

            if name.isdigit():
                subdirs.append(int(name))
    if subdirs:
        return max(subdirs) + 1
    return first_number

def make_dir_if_not_exists(rel_dirname):
    try:
        os.mkdir(rel_dirname)
    except OSError:
        pass

def new_scan():
    switch_to_next_dir()

def exec_cmd(cmd,rsp):
    if cmd in CALLBACKS:
        with camera_lock:
            return CALLBACKS[cmd](rsp)

def take_img():
    rsp = requests.get(ADDR + ENDPOINTS['image'], stream=True)
    return exec_cmd('image',rsp)

def focus():
    rsp = requests.get(ADDR + ENDPOINTS['focus'], stream=True)
    return exec_cmd('focus',rsp)


class IncrementalImageSaver(object):

    def __init__(self):
        self._count = 1

    def __call__(self,rsp):

        if rsp.status_code != 200:
            raise ValueError('Something went wrong with the request')

        fname = '{}{}.jpg'.format(img_dir, self._count)
        with open(fname, 'wb') as f:
            rsp.raw.decode_content = True
            shutil.copyfileobj(rsp.raw, f)
        self._count += 1
        return fname


CALLBACKS = {
    'image': IncrementalImageSaver(),
}


if __name__ == '__main__':
    start_scan()




