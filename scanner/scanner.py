from scapy import sr1, IP, TCP
from ftplib import FTP

def filter_by_log(server):
    try:
        ftp = FTP(server, timeout=10)
        ftp.login()
        ftp.retrlines('LIST')
        ftp.quit()
    except:
        return False

def filter_by_ack(server):
    try
        rcv = sr1(IP(dst=server)/TCP(dport=21,flags="S"), timeout=10)
    if rcv:
        return True
    else:
        return False

if __name__ == "__main__":
    scan(range)
