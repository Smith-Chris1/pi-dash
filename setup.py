#!/usr/bin/python3
import subprocess
import shutil
import os

print("Setting up Temple Pi")

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
print(CURR_DIR)

path = '/home/pi/pi-dash'

# Check whether the specified path exists or not
isExist = os.path.exists(path)

if not isExist:
    # Create a new directory because it does not exist 
    os.makedirs(path)
    print("The new directory is created!")

print('updating from the repo')
process = subprocess.Popen(["git", "-C","/home/pi/pi-dash","pull", "https://github.com/Smith-Chris1/pi-dash.git"], stdout=subprocess.PIPE)
output = process.communicate()[0]


print("installing dependancies")
pythoninstall = subprocess.Popen([ 'pip', 'install', '-r', 'requirements.txt' ], cwd="/home/pi/pi-dash", stdout=subprocess.PIPE)

print('moving files')
shutil.copyfile('/home/pi/pi-dash/vlc/temple.html', '/usr/share/vlc/lua/http/temple.html')

print('cleaning up')
if CURR_DIR is not '/hom/pi/pi-dash':
    os.remove(__file__)


