from flask import Flask, render_template, redirect, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from subprocess import Popen, PIPE
import config
import os
import sys
import subprocess
import socket
import platform
import psutil
import requests
import time
import re
import json
import vlc

app = Flask(__name__)

scans = []

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app,async_mode='threading')

@socketio.on('scans')
def load_all(message):
    # scans = []
    print(message)
    try:
        thisInfo = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding())
    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            thisInfo = s.getsockname()[0]
        except Exception:
            thisInfo = '127.0.0.1'


    if " " in thisInfo:
        hostIP = thisInfo.split(' ')
        thisInfo = thisInfo.split(' ')[0].strip()
    else:
        thisInfo.strip()
    print(thisInfo.strip()+'/25')
    ### find other machines on the network

    if 'localhost' in thisInfo.strip():
        thisInfo = '127.0.0.1'
        
    subnet = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", thisInfo.strip())[0]
    print(subnet)
    for host in range(127):
        ispi = False
        try:
            ispi = requests.request('POST','http://'+subnet+str(host)+':5000/ispi', timeout=.1).text
        except:
            ispi = False
        # print(ispi)
        if host == 126:
            socketio.emit('host', "Scan Complete")
            time.sleep(3)
            socketio.emit('host', "")
        else:
            if ispi == "True":
                print(ispi)
                sysinfo = requests.request('POST','http://'+subnet+str(host)+':5000/sysinfo').text.split(",")
                print(sysinfo)
                print(scans)
                if subnet+str(host) not in scans:
                    scans.append(subnet+str(host))
                    try:                        
                        ### See if VLC is running on the servers
                        vlc = vlcUp(subnet+str(host))
                        if vlc == 0:
                            iframe = '<iframe src="http://' + subnet+str(host) + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
                        else:
                            iframe = '<iframe src="http://' + subnet+str(host) + ':5000/static/startVLC.html?ip='+subnet+str(host)+ '" style="max-width:240px !important; max-height: 50px;"></iframe>'

                        location = requests.request('GET','http://'+subnet+str(host)+':5000/getLocation')
                        row = {"host": sysinfo[0],
                            "ip":subnet+str(host),
                            "reboot_function":subnet+str(host),
                            "update_function":f"update_{sysinfo[0].replace('-','')}",
                            "reboot_path":subnet+str(host),
                            "update_path":f"http://{subnet+str(host)}:5000/fetch",
                            "cpu":sysinfo[1],
                            "vm":sysinfo[2],
                            "network":sysinfo[3],
                            "location":location.text,
                            "iframe":iframe}
                        socketio.emit('new_row', row)

                        # socketio.emit("new_pi", card) 
                        # print(scans)
                    except:
                        print('error in updating scans')
        
            socketio.emit('host', "Scanning Subnet/25 for PI: " + subnet+str(host) + ' ' +str(ispi))
            

@socketio.on('load_one')                        # Decorator to catch an event called "my event":
def load_one(message):                        # test_message() is the event callback function.
    print(message)
    ### making card for host that is being viewed.
    print(scans)
    print(len(scans))
    if len(scans) == 0:
        try:
            thisInfo = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding())
        except:
            thisInfo = 'localhost'
        print(thisInfo)
        if "\r" or "\n" in thisInfo:
            print('line break')
        if " " in thisInfo:
            hostIP = thisInfo.split(' ')
            thisInfo = thisInfo.split(' ')[0].strip()
        else:
            thisInfo.strip()
        print(thisInfo)
        vlc = vlcUp(thisInfo)
        print(vlc)
        if vlc == 0:
            iframe = '<iframe src="http://' + thisInfo + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
        else:
            iframe = '<iframe src="http://' + thisInfo + ':5000/static/startVLC.html?ip='+thisInfo + '" style="max-width:240px !important; max-height: 50px;"></iframe>'
        print(iframe)
        print(('http://'+thisInfo+':5000/sysinfo'))
        try:
            sysinfo = requests.request('POST','http://'+thisInfo+':5000/sysinfo', timeout=3).text.split(",")
        except:
            print('exception')
            sysinfo = ("uknown,unknown,unknown,unknown").split(',')
        # print('http://'+thisInfo+':5000/sysinfo')
        print(sysinfo)
        
        location = requests.request('GET','http://'+thisInfo+':5000/getLocation')
        print(location.text)
        scans.append(thisInfo)
        row = {"host": sysinfo[0],
                        "ip":thisInfo,
                        "reboot_function":thisInfo,
                        "update_function":f"update_{sysinfo[0].replace('-','')}",
                        "reboot_path":f"http://{thisInfo}:5000/reboot",
                        "update_path":f"http://{thisInfo}:5000/fetch",
                        "cpu":sysinfo[1],
                        "vm":sysinfo[2],
                        "network":sysinfo[3],
                        "location":location.text,
                        "iframe":iframe}
        socketio.emit('new_row', row)
        # scans.append(card)
        # socketio.emit("new_pi", card) 
    else:
        for host in scans:
            # subnet = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", host.strip())[0]
            piInfo(host)


@app.route('/')
def index():
    global scans
    return render_template("home.html", scanresults=" ".join(scans))



@app.route('/reboot')
def reboot():
    command = 'shutdown -r now'.split()
    p = Popen(['sudo', '--stdin'] + command, stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    p.communicate(f'{config.password}\n')[1]

@app.route('/shutdown')
def shutdown():
    command = 'shutdown now'.split()
    p = Popen(['sudo', '--stdin'] + command, stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    p.communicate(f'{config.password}\n')[1]
    
@app.route('/setLocation',methods = ['POST'])
def setLocation():
    try:
        with open(os.path.dirname(os.path.realpath(__file__))+"/location", 'w') as f:
            f.write(request.values.get('location'))
        return "success"
    except:
        return "error setting location"
        

@app.route('/getLocation')
def getLocation():
    file = open(os.path.dirname(os.path.realpath(__file__))+"/location", 'r')
    location = file.readlines()
    if len(location) > 0:
        return location[0]
    else:
        return "set"

@app.route('/name',methods = ['GET'])
def name():
    try:
        return socket.gethostname()
    except:
        return "unknown"
    
@app.route('/sysinfo',methods = ['POST'])
def sysinfo():
    inf = 'eth0'
    # print('work ')
    try:
        return f"{socket.gethostname().split('.')[0]},{psutil.cpu_percent()},{psutil.virtual_memory().percent},{net_usage(inf)}"
    except:
        return "unknown,unknown,unknown,unknown"
    
@app.route('/startVLCA', methods = ['POST'])
def startVLCA():
    i = vlc.Instance()
    media_player = i.media_player_new()
    media_player.fullscreen()
    media_player.set_mrl('udp://@239.27.0.27:1234')
    media_player.play()
    # vlca = subprocess.Popen(['cvlc', '-I', 'http', '--http-port', '8080', '--http-password', 'software', '--no-video-title-show', '--one-instance', '--fullscreen', '--volume-save','--volume-step=256', 'udp://@239.27.0.27:1234'])
    return "started"

@app.route('/startVLCB', methods = ['POST'])
def startVLCB():
    vlcb = subprocess.Popen(['cvlc', '-I', 'http', '--http-port', '8080', '--http-password', 'software', '--no-video-title-show', '--one-instance', '--fullscreen', '--volume-save','--volume-step=256', 'udp://@239.27.0.27:1235'])
    return "started"

@app.route('/fetch',methods = ['GET'])
def fetch():
    print('updating from the repo')

    processDL = subprocess.Popen(['sudo', '--stdin', 'wget', 'https://raw.githubusercontent.com/Smith-Chris1/pi-dash/main/setup.py', '-P', '/home/pi/'], stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    processoutput = processDL.communicate(f'{config.password}\n')[1]
    processInstall = subprocess.Popen(['sudo', '--stdin', "python3", "/home/pi/setup.py"], stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    installoutput = processInstall.communicate(f'{config.password}\n')[1]

    return 'success'

@app.route('/ispi', methods = ['POST'])
def ispi():
    return "True"

def piInfo(host):
    sysinfo = requests.request('POST','http://'+str(host)+':5000/sysinfo').text.split(",")
    ### See if VLC is running on the servers
    vlc = vlcUp(str(host))
    if vlc == 0:
        iframe = '<iframe src="http://' +str(host) + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
    else:
        iframe = '<iframe src="http://' + str(host) + ':5000/static/startVLC.html?ip='+str(host)+ '" style="max-width:240px !important; max-height: 50px;"></iframe>'
    
    location = requests.request('GET','http://'+str(host)+':5000/getLocation')
    row = {"host": sysinfo[0],
        "ip":str(host),
        "reboot_function":str(host),
        "update_function":f"update_{sysinfo[0].replace('-','')}",
        "reboot_path":str(host),
        "update_path":f"http://{str(host)}:5000/fetch",
        "cpu":sysinfo[1],
        "vm":sysinfo[2],
        "network":sysinfo[3],
        "location":location.text,
        "iframe":iframe}
    socketio.emit('new_row', row)


def net_usage(inf):   #change the inf variable according to the interface
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
    net_in_1 = net_stat.bytes_recv
    net_out_1 = net_stat.bytes_sent
    time.sleep(1)
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
    net_in_2 = net_stat.bytes_recv
    net_out_2 = net_stat.bytes_sent
    net_in = round(((net_in_2 - net_in_1) * 8) / 1024 / 1024, 3)
    # net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
    net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)
    return net_in

def vlcUp(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, 8080))
    return result

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', debug=True, port=5000)