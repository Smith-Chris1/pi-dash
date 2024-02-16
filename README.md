This is used to control multiple Raspberry Pi's UDP video playback from any Rasperry Pi. 

All the Pi's talk to each other via an endpoint. Once the Pi's are identified they are displayed on the dashboard accessible at: http://localhost:5000 or from the IP of the Pi. This is designed to be flexible in an environment with dynamic IP's.

##Installation 
```wget "https://raw.githubusercontent.com/Smith-Chris1/pi-dash/main/setup.py" -P /home/pi/ && sudo python3 /home/pi/setup.py```

##Build App

To ensure proper installation the flask server app is compiled to a binary with pyinstaller.
The binary must be built on the same OS that its deployed on, in this case a Raspberry Pi.

Clone this repo onto the Pi or OS you need to compile for.

 ```pip3 install pyinstaller```

CD to the directory its cloned into.

```pyinstaller --add-data "static:static" --add-data "templates:templates" --add-data "scripts:scripts" --add-data "services:services" --add-data "vlc:vlc" --add-data "host:host" app.py```

use the app binary and _internals in the dist folder to distribue.

This may work using onefile in pyinstaller but I haven't tested it.

##FFmpeg UDP test stream

Use this ffmpeg command to generate a simple red video feed over the UDP address and port. This is only for testing if you're lacking a UDP playout stream.

If you're testing on a VM with virtualbox, you need a bridged network configuration.

```ffmpeg -f lavfi -i color=color=red -f mpegts "udp://239.27.0.27:1234?pkt_size=188&buffer_size=65535"```