from flask import Flask, render_template, redirect, request
from subprocess import Popen, PIPE
import config
import os
import sys
import subprocess
import socket
import platform
import psutil
import requests
# import waitress

scans = []

macAddresses = ['e4:5f:01:35:25:9b','dc:a6:32:8b:42:e1']

app = Flask(__name__)

@app.route('/')

def index():
    h_name = socket.gethostname()
    IP_addres = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding()).strip()
    return render_template("home.html", this_ip=IP_addres, this_host=h_name, scanresults=" ".join(scans))

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
    try:
        return f"{socket.gethostname()},{psutil.cpu_percent()},{psutil.virtual_memory().available * 100 / psutil.virtual_memory().total},{psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv}"
    except:
        return "unknown,unknown,unknown,unknown"

@app.route('/fetch',methods = ['GET'])
def fetch():
    print('updating from the repo')
    command = 'git fetch https://github.com/Smith-Chris1/pi-dash.git'.split()
    subprocess.check_output(command, cwd='/home/pi/pi-dash', shell=True)
    return 'success'

@app.route('/scan')
def scan():
    global scans
    scans = []
    mac = subprocess.run(['arp', '-a'], capture_output=True).stdout.decode(sys.getdefaultencoding()).split('\n')
    for pi in mac:
        print(pi)
        info = pi.split(' ')
        try:
            if info[3] in macAddresses:
                sysinfo = requests.request('POST','http://'+info[1].replace("(", "").replace(")","")+':5000/sysinfo').text.split(",")
                try:
                    scans.append(render_template('card.html', 
                                                 ip=sysinfo[0]+" " + info[1].replace("(", "").replace(")",""),
                                                 reboot_function=f"reboot_{sysinfo[0].replace('-','')}",
                                                 reboot_path="http://"+info[1].replace("(", "").replace(")","")+":5000/reboot",
                                                 accordian_id=info[3].replace(":",""),
                                                 cpu=sysinfo[1],
                                                 vm=sysinfo[2],
                                                 network=sysinfo[3]
                                                 ))
                except:
                    print('error')
        except:
            print('error')
    return redirect('/')

if __name__ == '__main__':
    from waitress import serve
    app.run(debug=True, port=5000)