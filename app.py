from flask import Flask, render_template, redirect, request
from flask_cors import CORS, cross_origin
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
# import waitress

scans = []

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/ispi', methods = ['POST'])
def ispi():
    return "True"

@app.route('/')

def index():

    global scans
    
    # if len(scans) < 1:
    #     return render_template("home.html", scanresults="<div class='lds-ring'><div></div><div></div><div></div><div></div></div>")
    # else:
    return render_template("home.html", scanresults=" ".join(scans))

@app.route('/reboot')
def reboot():
    command = 'shutdown -r now'.split()
    p = Popen(['sudo', '--stdin'] + command, stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    p.communicate(f'{config.password}\n')[1]

@app.route('/name',methods = ['GET'])
def name():
    try:
        return socket.gethostname()
    except:
        return "unknown"
    
@app.route('/sysinfo',methods = ['POST'])
def sysinfo():
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
    try:
        return f"{socket.gethostname()},{psutil.cpu_percent()},{psutil.virtual_memory().percent},{net_usage('eth0')}"
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

@app.route('/scan')
def scan():
    global scans
    scans = []
    
    ### making card for host that is being viewed.
    thisInfo = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding())
    if " " in thisInfo:
        hostIP = thisInfo.split(' ')
        thisInfo = thisInfo.split(' ')[0].strip()
    else:
        thisInfo.strip()
    vlc = vlcUp(thisInfo)    
    if vlc == 0:
        iframe = 'iframeVLC.html'
    else:
        iframe = 'startVLC.html'
    sysinfo = requests.request('POST','http://'+thisInfo+':5000/sysinfo').text.split(",")
    scans.append(render_template('card.html', 
        host = sysinfo[0],
        ip=thisInfo,
        reboot_function=f"reboot_{sysinfo[0].replace('-','')}",
        update_function=f"update_{sysinfo[0].replace('-','')}",
        reboot_path="http://"+thisInfo+":5000/reboot",
        update_path="http://"+thisInfo+":5000/fetch",
        cpu=sysinfo[1],
        vm=sysinfo[2],
        network=sysinfo[3],
        cardBody = render_template(iframe, ip=thisInfo, host=sysinfo[0].replace('-',''))
        ))
    
    
    ### find other machines on the network
    # mac = subprocess.run(['arp', '-a'], capture_output=True).stdout.decode(sys.getdefaultencoding()).split('\n')
    mac = subprocess.run(['nmap', '-sn', thisInfo.strip()+'/24'], capture_output=True).stdout.decode(sys.getdefaultencoding()).split('\n')
    
    for pi in mac:

        info = pi.split(' ')

        if len(info) > 1:
            if 'Nmap' in pi and 'Starting' not in pi and 'done' not in pi:
                info = pi.split(' ')
                print(info)
                # if re.findall(r"\((.*?)\)", info[4])[0] != re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4])[0]+'.1':
                if info[4] != re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4])[0]+'.1':
                    if info[4] != re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", info[4])[0]+'.94':
                        if info[4] not in hostIP:
                            print(info[4][0] + " is not the gateway.")
                            print('http://'+info[4])
                            try:
                                try:
                                    ispi = requests.request('POST','http://'+info[4]+':5000/ispi', timeout=5).text
                                except:
                                    ispi = "False"
                                if ispi == "True":
                                    sysinfo = requests.request('POST','http://'+info[4]+':5000/sysinfo').text.split(",")
                                    if sysinfo[0] not in " ".join(scans):
                                        try:                        
                                            ### See if VLC is running on the servers
                                            vlc = vlcUp(info[4])

                                            if vlc == 0:
                                                iframe = 'iframeVLC.html'
                                            else:
                                                iframe = 'startVLC.html'

                                            scans.append(render_template('card.html', 
                                                host = sysinfo[0],
                                                ip=info[4],
                                                reboot_function=f"reboot_{sysinfo[0].replace('-','')}",
                                                update_function=f"update_{sysinfo[0].replace('-','')}",
                                                reboot_path="http://"+info[4]+":5000/reboot",
                                                update_path="http://"+info[4]+":5000/fetch",
                                                  accordian_id=info[3].replace(":",""),
                                                cpu=sysinfo[1],
                                                vm=sysinfo[2],
                                                network=sysinfo[3],
                                                cardBody = render_template(iframe, ip=info[4], host=sysinfo[0].replace('-',''))
                                                ))
                                            print(scans)
                                        except:
                                            print('error in updating scans')
                            except requests.Timeout:
                                print("timeout")


                        else:
                            print(info[4] + " is the gateway, will not process.")

    return redirect('/')

def vlcUp(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, 8080))
    return result

if __name__ == '__main__':
    # from waitress import serve
    app.run('0.0.0.0', debug=True, port=5000)