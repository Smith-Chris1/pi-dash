import time
import psutil
import socket


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

path = "/home/pi/pi-dash/host/info.txt"

while True:
    time.sleep(10)
    with open(path, "a") as file:
        # Reading form a file
        file.write(f"{socket.gethostname().split('.')[0]},{psutil.cpu_percent()},{psutil.virtual_memory().percent},{net_usage('eth0')}")


