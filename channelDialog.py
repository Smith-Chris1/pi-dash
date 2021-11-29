# Import required libraries
from tkinter import *
from tkinter import ttk
import tkinter.font as font
import time
from math import trunc
import os
import sys
# try:
#     from ttkthemes import ThemedTk
# except ImportError:
#     from pip._internal import main as pip
#     pip(['install', '--user', 'ttkthemes'])
#     from ttkthemes import ThemedTk
from subprocess import PIPE
import subprocess
import ipaddress
import re

# Get the IP of the machine
thisInfo = subprocess.check_output(['hostname', '--all-ip-addresses']).decode(sys.getdefaultencoding())
if " " in thisInfo:
    thisInfo = thisInfo.split(' ')[0].strip()
else:
    thisInfo.strip()
    
#Change it to the network CIDR

net_addr = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3})\.", thisInfo)[0] +'.0'

# Create the network
ip_net = ipaddress.ip_network(net_addr)

# Get all hosts on that network
all_hosts = list(ip_net.hosts())

# Configure subprocess to hide the console window
# info = subprocess.STARTUPINFO()
# info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# info.wShowWindow = subprocess.SW_HIDE

# For each IP address in the subnet, 
# run the ping command with subprocess.popen interface
for i in range(len(all_hosts)):
    output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])], stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
    
    if "Destination host unreachable" in output.decode('utf-8'):
        print(str(all_hosts[i]), "is Offline")
    elif "Request timed out" in output.decode('utf-8'):
        print(str(all_hosts[i]), "is Offline")
    else:
        print(str(all_hosts[i]), "is Online")

keyspressed = 0
play = ''
def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

# win = ThemedTk(theme=\"adapta\")
win = Tk()

win.title("Channel Selector")
win.resizable(False, False)

window_height = 350
window_width = 700

screen_width = win.winfo_screenwidth()
screen_height = win.winfo_screenheight()

x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

win.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

def killPlayback():
    timerLabel['text'] = "Quitting Playback"

    global play
    play.stdin.write(bytes('q','ascii'))
    play.stdin.flush()
    play.kill()
    win.destroy()

def channela():
    global play
    timerLabel['text'] = "Trying to Start Channel A"
    win.after_cancel(win.after_id)
    # os.system('sudo bash /home/pi/Channels/channelaservice.sh')
    play=subprocess.Popen(['cvlc', '-I', 'http', '--http-port', '8080', '--http-password', 'play', '--no-video-title-show', '--one-instance', '--fullscreen', 'udp://@239.27.0.27:1234'])


def channelb():
    global play
    timerLabel['text'] = "Trying to Start Channel B"
    win.after_cancel(win.after_id)
    # os.system('sudo bash /home/pi/Channels/channelbservice.sh')
    play=subprocess.Popen(['cvlc', '-I', 'http', '--http-port', '8080', '--http-password', 'play', '--no-video-title-show', '--one-instance', '--fullscreen', 'udp://@239.27.0.27:1235'])



myFont = font.Font(family='Aerial', size=24)
pixelVirtual = PhotoImage(width=1, height=1)


mainLabel = ttk.Label(win, text="Your IP is: {thisInfo}\nPlease Select your Channel:", font=('Aerial', 24))
mainLabel.pack()

timerLabel = ttk.Label(win)
timerLabel.pack()

def countdown(count):
    timerLabel['text'] = "Channel A will auto start in: "+ str(count)

    if count > 0:
        win.after_id = win.after(1000, countdown, count-1)
    if count == 0:
        channela()
try:
    countdown(15)
except:
    print('window destroyed already')


channelaButton = ttk.Button(win, text='Channel A', command=channela, width=trunc(window_width*.9),compound="c",image=pixelVirtual)

channelaButton.place(relx=0.5, rely=0.4, anchor=CENTER, width = trunc(window_width*.9), height = 30)

channelbButton = ttk.Button(win, text='Channel B', command=channelb, width=trunc(window_width*.9),compound="c",image=pixelVirtual)

channelbButton.place(relx=0.5, rely=0.5, anchor=CENTER, width = trunc(window_width*.9), height = 30)

win.bind("<a>", lambda x: channela())
win.bind("<b>", lambda x: channelb())
win.bind("<q>", lambda x: killPlayback())

win.mainloop()