to install: 

##Installation 
```wget "https://raw.githubusercontent.com/Smith-Chris1/pi-dash/main/setup.py" -P /home/pi/ && sudo python3 /home/pi/setup.py```

##Build Docker

```docker build --platform=linux/arm/v7 -t pi-dash .```

```docker save -o pi-dash.tar pi-dash```

```sudo docker run --rm -it -p 5000:5000 --name pi-dash-container pi-dash ```

##FFmpeg UDP test stream
If you're testing on a VM with virtualbox, you need a bridged network configuration
```ffmpeg -f lavfi -i color=color=red -f mpegts "udp://239.27.0.27:1234?pkt_size=188&buffer_size=65535"```