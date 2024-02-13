to install: wget "https://raw.githubusercontent.com/Smith-Chris1/pi-dash/main/setup.py" -P /home/pi/ && sudo python3 /home/pi/setup.py

##Build Docker

```docker build -t pi-dash .```

```docker save -o pi-dash.tar pi-dash```

```sudo docker run --rm -it -p 5000:5000 --name pi-dash-container pi-dash ```