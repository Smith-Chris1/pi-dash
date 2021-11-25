#!/usr/bin/python3
import subprocess
import shutil
import os

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
print(CURR_DIR)

try:
    print("Setting up Temple Pi")

    path = '/home/pi/pi-dash'

    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print("The new directory is created!")

    print('updating from the repo')
    process = subprocess.Popen(["git", "-C",path,"pull", "https://github.com/Smith-Chris1/pi-dash.git"], stdout=subprocess.PIPE)
    output = process.communicate()[0]


    print("installing dependancies")
    process = subprocess.Popen([ 'pip', 'install', '-r', path+'/requirements.txt' ], cwd=path, stdout=subprocess.PIPE)
    output = process.communicate()[0]

    print('moving files')
    shutil.copyfile(path+'/vlc/temple.html', '/usr/share/vlc/lua/http/temple.html')

    print('cleaning up')
    if CURR_DIR != path:
        os.remove(__file__)
except:
    if CURR_DIR != path:
        os.remove(__file__)
