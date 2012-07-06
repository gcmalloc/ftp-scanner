from ftplib import FTP, Error
import netaddr
import socket
import time
import ping
from subprocess import Popen
from subprocess import PIPE
from multiprocessing import Pool
import re

RANGE = "127.0.0.1"


def filter_by_login(server):
    try:
        ftp = FTP(server, timeout=10)
        ftp.login()
        ftp.retrlines('LIST')
        ftp.quit()
        return True
    except:
        return False

def filter_by_ack(server):
    try:
        rcv = sr1(IP(dst=server)/TCP(dport=21,flags="S"), timeout=10)
    except:
        return True

    if rcv:
        return True
    else:
        return False

class PingAgent():
    def __init__(self, host):
        self.host = host

    def run(self):
        p = Popen(['ping', '-c', '1', self.host], stdout=PIPE, close_fds=True)
        output = str(p.communicate()[0])
        m = re.search('time=(.*?) ms', output)
        time = float(m.groups(0)[0])
        if m:
            return time
        else:
            return 0

def generate_metadata(server, server_data=None):
    if not server_data:
        server_data = dict()
        server_data["address"] = server
        server_data["hostname"] = socket.gethostbyaddr(server)[1][0]
        server_data["status"] = False
        server_data["check_last"] = 0
        server_data["up_number"] = 0
        server_data["down_number"] = 0
        server_data["ping"] = 0

    #update the status
    status = filter_by_login(server)
    if status:
        server_data["up_number"] += 1
    else:
        server_data["down_number"] +=1
    server_data["status"] = status

    #update the ping delay
    try:
        server_data["ping"] = PingAgent(server).run()
    except socket.error as e:
        print("error : " + e)

    #update time
    server_data["check_last"] = int(time.time())
    return server_data

def generate_range(ip_range):
    for i in netaddr.IPNetwork(ip_range):
        yield str(i)

def repoll():
    ip_range = generate_range(RANGE)
    pool = Pool(5)
    out = pool.map(generate_metadata, ip_range)

if __name__ == "__main__":
    ip_range = generate_range("127.0.0.1")
    pool = Pool(5)
    out = pool.map(generate_metadata, ip_range)
    print(out)
