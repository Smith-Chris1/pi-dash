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
# import waitress

scans = []

macAddresses = ['e4:5f:01:35:25:9b','dc:a6:32:8b:42:e1']

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
    def net_usage(inf):   #change the inf variable according to the interface
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        net_in_1 = net_stat.bytes_recv
        net_out_1 = net_stat.bytes_sent
        time.sleep(1)
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        net_in_2 = net_stat.bytes_recv
        net_out_2 = net_stat.bytes_sent

        net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
        net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)
        return net_out
        # print(f"Current net-usage:\nIN: {net_in} MB/s, OUT: {net_out} MB/s")
    try:
        return f"{socket.gethostname()},{psutil.cpu_percent()},{psutil.virtual_memory().available * 100 / psutil.virtual_memory().total},{net_usage('eth0')}"
    except:
        return "unknown,unknown,unknown,unknown"

@app.route('/fetch',methods = ['GET'])
def fetch():
    print('updating from the repo')

    process = subprocess.Popen(['sudo', '--stdin', "python3", "/home/pi/pi-dash/setup.py"], stdin=PIPE, stderr=PIPE,
            universal_newlines=True)
    output = process.communicate(f'{config.password}\n')[1]
    # process = subprocess.Popen(["git", "-C","/home/pi/pi-dash","pull", "https://github.com/Smith-Chris1/pi-dash.git"], stdout=subprocess.PIPE)
    # output = process.communicate()[0]

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
                                                 host = sysinfo[0],
                                                 ip=info[1].replace("(", "").replace(")",""),
                                                 reboot_function=f"reboot_{sysinfo[0].replace('-','')}",
                                                 update_function=f"update_{sysinfo[0].replace('-','')}",
                                                 reboot_path="http://"+info[1].replace("(", "").replace(")","")+":5000/reboot",
                                                 update_path="http://"+info[1].replace("(", "").replace(")","")+":5000/fetch",
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
    app.run('0.0.0.0', debug=True, port=5000)