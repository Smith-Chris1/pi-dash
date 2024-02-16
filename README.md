to install: 

##Installation 
```wget "https://raw.githubusercontent.com/Smith-Chris1/pi-dash/main/setup.py" -P /home/pi/ && sudo python3 /home/pi/setup.py```

##Build App

On a raspberry pi install pyinstaller ```pip3 install pyinstaller```

```cd /home/pi-dash```

```pyinstaller --add-data "static:static" --add-data "templates:templates" --add-data "scripts:scripts" --add-data "services:services" --add-data "vlc:vlc" --add-data "host:host" app.py```

use the app binary in the dist folder to distribue.

##FFmpeg UDP test stream
If you're testing on a VM with virtualbox, you need a bridged network configuration
```ffmpeg -f lavfi -i color=color=red -f mpegts "udp://239.27.0.27:1234?pkt_size=188&buffer_size=65535"```