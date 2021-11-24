from getpass import getpass
from subprocess import Popen, PIPE

command = 'shutdown -r now'.split()

p = Popen(['sudo', '--stdin'] + command, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
sudo_prompt = p.communicate('WestonDean=0219!\n')[1]