#!/usr/bin/python3
from re import sub
import subprocess
import shutil
import os
from subprocess import run
import sys
import time


CURR_DIR = os.path.dirname(os.path.realpath(__file__))
print(CURR_DIR)

def apt_install(pkgs):
    cmd = ['pkexec', 'apt-get', 'install', '-y'] + pkgs
    print('Running command: {}'.format(' '.join(cmd)))
    result = run(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        encoding='utf8',
        env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
    )
    result.check_returncode()

def accept_eula():
    cmd = 'echo msttcorefonts msttcorefonts/{}-mscorefonts-eula {} | pkexec debconf-set-selections'
    run(cmd.format("present", "note ''"), stdout=sys.stdout, stderr=sys.stderr, shell=True)
    run(cmd.format("accepted", "select true"), stdout=sys.stdout, stderr=sys.stderr, shell=True)


try:
    print("Setting up Temple Pi")

    path = '/home/pi/pi-dash'

    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print("The new directory is created!")
    else:
        subprocess.Popen(['rm', '-r', path])
        time.sleep(10)
        os.makedirs(path)
        # os.makedirs(path+'/dockerStuff')

    
    # if Path(path+'requirements.txt').is_file():
    
    # print(path+'/requirements.txt')
    # print(os.path.isfile(path+'/requirements.txt'))
    # if os.path.isfile(path+'/requirements.txt'):
        # print('updating from the repo')
        # process = subprocess.Popen(["git", "-C", '/home/pi/pi-dash/', "pull", "https://github.com/Smith-Chris1/pi-dash.git"], stdout=subprocess.PIPE)
        # print(process.args)
        # output = process.communicate()[0]
    # else:
    print('first install')
    process = subprocess.Popen(["git", "-C", '/home/pi/', "clone", "https://github.com/Smith-Chris1/pi-dash.git"], stdout=subprocess.PIPE)
    output = process.communicate()[0] 
    # os.makedirs(path+'/dockerStuff')
    


    
    if os.path.isfile('/usr/bin/docker'):
        print("Docker already installed")
    else:
        print("installing docker")
        process = subprocess.Popen(['sudo', 'apt', 'install', 'docker.io'], stdout=subprocess.PIPE)
        process.communicate()[0]
    process = subprocess.Popen(['sudo', 'usermod', '-aG', 'docker', '$USER'], stdout=subprocess.PIPE)
    process.communicate()[0]
    # subprocess.Popen(['sh', path+'/scripts/docker.sh'])
    # subprocess.Popen(['sudo', 'usermod', '-aG', 'docker', 'pi', '&&', 'sudo', 'usermod', '-aG', 'docker', 'Pi'])
    # subprocess.Popen(['pip3', 'install', 'docker'])

    process = subprocess.Popen(['wget', 'https://github.com/Smith-Chris1/pi-dash/releases/download/latest/pi-dash.tar', '-O', path+"/pi-dash.tar"])
    process.communicate()[0]
    # client = docker.from_env()
    # client.containers.run('pidash')
    # process = subprocess.Popen([ 'pip3', 'install', '-r', path+'/requirements.txt', '--break-system-packages' ], cwd=path, stdout=subprocess.PIPE)
    # output = process.communicate()[0]
    
    print("installing hostinfo")
    process = subprocess.Popen(['pip3', 'install', 'psutil'], stdout=subprocess.PIPE)
    process.communicate()[0]
    process = subprocess.Popen(['sudo', 'chown', 'pi:root', path+'/scripts/info.txt'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    shutil.copyfile(path+'/services/hostinfo.service', '/etc/systemd/system/hostinfo.service')
    process = subprocess.Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['sudo', 'systemctl', 'enable', 'hostinfo.service'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['sudo','systemctl', 'start', 'hostinfo.service'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    
    accept_eula()
    apt_install(['curl', 'nmap'])

    print('moving files')
    process = subprocess.Popen(['sudo', 'chown', 'root:root', path+'/services/channel.desktop'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['sudo', 'chmod', '777', path+'/location'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    shutil.copyfile(path+'/vlc/table.html', '/usr/share/vlc/lua/http/table.html')
    shutil.copyfile(path+'/services/flask_service.service', '/etc/systemd/system/pidash.service')
    shutil.copyfile(path+'/services/channel.desktop', '/etc/xdg/autostart/ChannelSwitch.desktop')
    # shutil.copyfile(path+'/scripts/boot.txt', '/boot/config.txt')
    shutil.copyfile(path+'/scripts/deskpi.conf', '/etc/deskpi.conf')
    process = subprocess.Popen(['sudo', 'systemctl', 'daemon-reload'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['sudo', 'systemctl', 'enable', 'pidash.service'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['sudo','systemctl', 'start', 'pidash.service'], stdout=subprocess.PIPE)
    output = process.communicate()[0]

    print('cleaning up')
    if CURR_DIR != path:
        print('Rebooting')
        time.sleep(5)
        os.remove(__file__)
        # subprocess.run(['shutdown', '-r', 'now'])
        print('Restart this Pi after installation - shutdown -r now')
        # os.system("shutdown -r now")
        

except Exception as e:
    print(e)
    if CURR_DIR != path:
        os.remove(__file__)
