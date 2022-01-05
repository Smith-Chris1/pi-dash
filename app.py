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

app = Flask(__name__)

scans = []

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app)


@app.route('/')
def index():
    global scans
    return render_template("home.html", scanresults=" ".join(scans))

@socketio.on('scans')
def load_all(message):
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
    print(thisInfo.strip()+'/24')
    ### find other machines on the network

    if 'localhost' in thisInfo.strip():
        thisInfo = '127.0.0.1'
        
    subnet = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", thisInfo.strip())[0]
    print(subnet)
    for host in range(255):
        
        try:
            ispi = requests.request('POST','http://'+subnet+str(host)+':5000/ispi', timeout=.1).text
        except:
            ispi = False
        # print(ispi)
        if host == 254:
            socketio.emit('host', "Scan Complete")
            time.sleep(3)
            socketio.emit('host', "")
        else:
            socketio.emit('host', "Scanning Subnet/24 for PI: " + subnet+str(host) + ' ' +str(ispi))
        if ispi == "True":
            print(ispi)
            sysinfo = requests.request('POST','http://'+subnet+str(host)+':5000/sysinfo').text.split(",")
            print(sysinfo)
            if sysinfo[0] not in " ".join(scans):
                try:                        
                    ### See if VLC is running on the servers
                    vlc = vlcUp(subnet+str(host))
                    if vlc == 0:
                        iframe = '<iframe src="http://' + subnet+str(host) + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
                    else:
                        print(84)
                        iframe = '<iframe src="http://' + subnet+str(host) + ':5000/static/startVLC.html?ip='+subnet+str(host)+ '" style="max-width:240px !important; max-height: 50px;"></iframe>'
                    # card = render_template('card.html', 
                    #     host = sysinfo[0],
                    #     ip=subnet+str(host),
                    #     reboot_function=subnet+str(host),
                    #     update_function=f"update_{sysinfo[0].replace('-','')}",
                    #     reboot_path="http://"+subnet+str(host)+":5000/reboot",
                    #     update_path="http://"+subnet+str(host)+":5000/fetch",
                    #     # accordian_id=info[3].replace(":",""),
                    #     cpu=sysinfo[1],
                    #     vm=sysinfo[2],
                    #     network=sysinfo[3],
                    #     cardBody = render_template(iframe, ip=subnet+str(host), host=sysinfo[0].replace('-',''))
                    #     )
                    # scans.append(card)
                    location = requests.request('GET','http://'+thisInfo+':5000/getLocation')
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

@socketio.on('load_one')                        # Decorator to catch an event called "my event":
def load_one(message):                        # test_message() is the event callback function.
    print(message)
    ### making card for host that is being viewed.
    print(len(scans))
    if len(scans) == 0:
        try:
            thisInfo = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding())
        except:
            thisInfo = 'localhost'

        if " " in thisInfo:
            hostIP = thisInfo.split(' ')
            thisInfo = thisInfo.split(' ')[0].strip()
        else:
            thisInfo.strip()
        vlc = vlcUp(thisInfo)
        if vlc == 0:
            iframe = '<iframe src="http://' + thisInfo + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
        else:
            iframe = '<iframe src="http://' + thisInfo + ':5000/static/startVLC.html?ip='+thisInfo + '" style="max-width:240px !important; max-height: 50px;"></iframe>'
        sysinfo = requests.request('POST','http://'+thisInfo+':5000/sysinfo').text.split(",")
        # print('http://'+thisInfo+':5000/sysinfo')
        location = requests.request('GET','http://'+thisInfo+':5000/getLocation')
        print(location.text)
        # card = render_template('card.html', 
        #     host = sysinfo[0],
        #     ip=thisInfo,
        #     reboot_function=thisInfo,
        #     update_function=f"update_{sysinfo[0].replace('-','')}",
        #     reboot_path="http://"+thisInfo+":5000/reboot",
        #     update_path="http://"+thisInfo+":5000/fetch",
        #     cpu=sysinfo[1],
        #     vm=sysinfo[2],
        #     network=sysinfo[3],
        #     cardBody = render_template(iframe, ip=thisInfo, host=sysinfo[0].replace('-',''))
        #     )
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
        socketio.emit("new_pi", " ".join(scans))


@app.route('/reboot')
def reboot():
    command = 'shutdown -r now'.split()
    p = Popen(['sudo', '--stdin'] + command, stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    p.communicate(f'{config.password}\n')[1]

@app.route('/shutdown')
def reboot():
    command = 'shutdown now'.split()
    p = Popen(['sudo', '--stdin'] + command, stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    p.communicate(f'{config.password}\n')[1]
    
@app.route('/setLocation',methods = ['POST'])
def setLocation():
    with open(os.path.dirname(os.path.realpath(__file__))+"/location", 'w') as f:
        f.write(request.values.get('location'))
    return "success"
        

@app.route('/getLocation')
def getLocation():
    file = open(os.path.dirname(os.path.realpath(__file__))+"/location", 'r')
    location = file.readlines()
    return location[0]

@app.route('/name',methods = ['GET'])
def name():
    try:
        return socket.gethostname()
    except:
        return "unknown"
    
@app.route('/sysinfo',methods = ['POST'])
def sysinfo():
    if 'Darwin' in os.uname():
        inf = 'lo0'
    else:
        inf = 'eth0'
    try:
        return f"{socket.gethostname().split('.')[0]},{psutil.cpu_percent()},{psutil.virtual_memory().percent},{net_usage(inf)}"
    except:
        return "unknown,unknown,unknown,unknown"
    
@app.route('/startVLCA', methods = ['POST'])
def startVLCA():
    vlca = subprocess.Popen(['cvlc', '-I', 'http', '--http-port', '8080', '--http-password', 'software', '--no-video-title-show', '--one-instance', '--fullscreen', '--volume-save','--volume-step=256', 'udp://@239.27.0.27:1234'])
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

@app.route('/scan')
def scan():
    global scans
    scans = []
    
    ### making card for host that is being viewed.
    try:
        thisInfo = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding())
    except:
        thisInfo = 'localhost'

    if " " in thisInfo:
        hostIP = thisInfo.split(' ')
        thisInfo = thisInfo.split(' ')[0].strip()
    else:
        thisInfo.strip()
    vlc = vlcUp(thisInfo)

    # if vlc == 0:
    #     iframe = '<iframe src="http://' + subnet+str(host) + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
    # else:
    #     iframe = '<iframe src="http://' + subnet+str(host) + ':5000/startVLC.html" style="min-width:320px; max-height: 50px;"></iframe>'
    sysinfo = requests.request('POST','http://'+thisInfo+':5000/sysinfo').text.split(",")
    # print('http://'+thisInfo+':5000/sysinfo')
    # scans.append(render_template('card.html', 
    #     host = sysinfo[0],
    #     ip=thisInfo,
    #     reboot_function=subnet+str(host),
    #     update_function=f"update_{sysinfo[0].replace('-','')}",
    #     reboot_path="http://"+thisInfo+":5000/reboot",
    #     update_path="http://"+thisInfo+":5000/fetch",
    #     cpu=sysinfo[1],
    #     vm=sysinfo[2],
    #     network=sysinfo[3],
    #     cardBody = render_template(iframe, ip=thisInfo, host=sysinfo[0].replace('-',''))
    #     ))
    
    print(thisInfo.strip()+'/24')
    ### find other machines on the network
    # mac = subprocess.run(['arp', '-a'], capture_output=True).stdout.decode(sys.getdefaultencoding()).split('\n')
    mac = subprocess.run(['nmap', '-p', '5000', thisInfo.strip()+'/24'], capture_output=True).stdout.decode(sys.getdefaultencoding()).split('\n')
    
    if 'localhost' in thisInfo.strip():
        thisInfo = '127.0.0.1'
    subnet = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", thisInfo.strip())[0]
    print(subnet)
    for host in range(256):
        try:
            ispi = requests.request('POST','http://'+subnet+str(host)+':5000/ispi', timeout=.1).text
        except:
            ispi = False
        # print(ispi)
        if ispi == "True":
            print(ispi)
            sysinfo = requests.request('POST','http://'+subnet+str(host)+':5000/sysinfo').text.split(",")
            print(sysinfo)
            if sysinfo[0] not in " ".join(scans):
                try:                        
                    ### See if VLC is running on the servers
                    vlc = vlcUp(subnet+str(host))
                    if vlc == 0:
                        iframe = '<iframe src="http://' + subnet+str(host) + ':8080/table.html" style="min-width:320px; max-height: 50px;"></iframe>'
                    else:
                        iframe = '<iframe src="http://' + subnet+str(host) + ':5000/static/startVLC.html?ip='+subnet+str(host)+ '" style="max-width:240px !important; max-height: 50px;"></iframe>'
                    scans.append(render_template('card.html', 
                        host = sysinfo[0],
                        ip=subnet+str(host),
                        reboot_function=subnet+str(host),
                        update_function=f"update_{sysinfo[0].replace('-','')}",
                        reboot_path="http://"+subnet+str(host)+":5000/reboot",
                        update_path="http://"+subnet+str(host)+":5000/fetch",
                        # accordian_id=info[3].replace(":",""),
                        cpu=sysinfo[1],
                        vm=sysinfo[2],
                        network=sysinfo[3],
                        cardBody = render_template(iframe, ip=subnet+str(host), host=sysinfo[0].replace('-',''))
                        ))
                    print(scans)
                except:
                    print('error in updating scans')
    
    
    # for pi in mac:

    #     info = pi.split(' ')

    #     if len(info) > 1:
    #         if 'Nmap' in pi and 'Starting' not in pi and 'done' not in pi:
    #             info = pi.split(' ')
    #             print(info)
    #             # if re.findall(r"\((.*?)\)", info[4])[0] != re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4])[0]+'.1':
    #             if re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4]):    
    #                 if info[4] != re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4])[0]+'.1':
    #                     print(info[4])
    #                     if info[4] != re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4])[0]+'.94':
    #                         if info[4] not in hostIP:
    #                             print(info[4][0] + " is not the gateway.")
    #                             print('http://'+info[4])
    #                             try:
    #                                 try:
    #                                     ispi = requests.request('POST','http://'+info[4]+':5000/ispi', timeout=5).text
    #                                 except:
    #                                     ispi = "False"
    #                                 if ispi == "True":
    #                                     print(ispi)
    #                                     sysinfo = requests.request('POST','http://'+info[4]+':5000/sysinfo').text.split(",")
    #                                     print(sysinfo)
    #                                     if sysinfo[0] not in " ".join(scans):
    #                                         try:                        
    #                                             ### See if VLC is running on the servers
    #                                             vlc = vlcUp(info[4])

    #                                             if vlc == 0:
    #                                                 iframe = 'iframeVLC.html'
    #                                             else:
    #                                                 iframe = 'startVLC.html'

    #                                             scans.append(render_template('card.html', 
    #                                                 host = sysinfo[0],
    #                                                 ip=info[4],
    #                                                 reboot_function=f"reboot_{sysinfo[0].replace('-','')}",
    #                                                 update_function=f"update_{sysinfo[0].replace('-','')}",
    #                                                 reboot_path="http://"+info[4]+":5000/reboot",
    #                                                 update_path="http://"+info[4]+":5000/fetch",
    #                                                   accordian_id=info[3].replace(":",""),
    #                                                 cpu=sysinfo[1],
    #                                                 vm=sysinfo[2],
    #                                                 network=sysinfo[3],
    #                                                 cardBody = render_template(iframe, ip=info[4], host=sysinfo[0].replace('-',''))
    #                                                 ))
    #                                             print(scans)
    #                                         except:
    #                                             print('error in updating scans')
    #                             except requests.Timeout:
    #                                 print("timeout")


    #                         else:
    #                             print(info[4] + " is the gateway, will not process.")

    return redirect('/')

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