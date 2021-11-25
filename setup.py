#!/usr/bin/python3
import subprocess
import shutil
import os

print("Setting up Temple Pi")

print('updating from the repo')
process = subprocess.Popen(["git", "-C","/home/pi/pi-dash","pull", "https://github.com/Smith-Chris1/pi-dash.git"], stdout=subprocess.PIPE)
output = process.communicate()[0]


print("installing dependancies")
pythoninstall = subprocess.Popen([ 'pip', 'install', '-r', 'requirements.txt' ], cwd="/home/pi/pi-dash", stdout=subprocess.PIPE)

print('moving files')
shutil.copyfile('/home/pi/pi-dash/vlc/temple.html', '/usr/share/vlc/lua/http/')


