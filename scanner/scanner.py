#!/usr/bin/env python2
from ftplib import FTP, Error
import netaddr
import socket
import time
import ping
from subprocess import Popen
from subprocess import PIPE
from multiprocessing import Pool, Process
import re
import logging

import oursql

def dbwrap(func):
   """Wrap a function in an idomatic SQL transaction.  The wrapped function
   should take a cursor as its first argument; other arguments will be
   preserved.
   """
   
   def new_func(self, *args, **kwargs):
       cursor = self.conn.cursor()
       try:
           cursor.execute("BEGIN")
           retval = func(self, cursor, *args, **kwargs)
           cursor.execute("COMMIT")
       except:
           cursor.execute("ROLLBACK")
           raise
       finally:
           cursor.close()

       return retval

   # Tidy up the help()-visible docstrings to be nice
   new_func.__name__ = func.__name__
   new_func.__doc__ = func.__doc__

   return new_func

class ServerTester(Process):

    def __init__(self, ip_range, conn, poll_interval=300):
        logging.debug("ip_range is {}".format(ip_range))
        self.ip_range = ip_range
        self.conn = conn
        self.poll_interval = poll_interval
        Process.__init__(self)
        self.init_db()

    @dbwrap
    def init_db(self, cursor):
        """
        insert the server entry into the table, flush the old data if any.
        """
        self.create_table()
        self.clean_table()
        for ip in self._get_range():
            try:
                hostname = socket.gethostbyaddr(ip)[1][0]
            except socket.error:
                hostname = ""
            logging.debug("insert ip:{} hostname:{}".format(ip, hostname))
            cursor.execute("INSERT INTO servers VALUES (?, ?, FALSE, 0, 0, 0, 0)", (ip, hostname,))

    @dbwrap
    def clean_table(self, cursor):
        cursor.execute("TRUNCATE TABLE servers;")

    @dbwrap
    def create_table(self, cursor):
        cursor.execute("""CREATE TABLE IF NOT EXISTS servers (
                            adress VARCHAR(15) NOT NULL,
                            hostname CHAR(50),
                            status TINYINT(1),
                            ping FLOAT UNSIGNED, 
                            up_number INT UNSIGNED, 
                            down_number INT UNSIGNED, 
                            last_check TIMESTAMP,
                            PRIMARY KEY(adress))""")

    def _get_range(self):
        for i in netaddr.IPNetwork(self.ip_range):
            yield str(i)

    def run(self):
        self.init_db()
        while True:
            ip_range = self._get_range()
            for server_ip in self._get_range():
                self.update_db_entry(server_ip)
            time.sleep(self.poll_interval)

    @dbwrap
    def update_db_entry(self, cursor, server):
        #update the ping delay
        try:
            ping_time = ping(server)
        except Exception as e:
            logging.info("error : " + str(e))
            ping_time = 0

        timestamp = int(time.time())

        status = test_by_login(server)
        print(status)
        if status:
            logging.debug("updating entry {} with status:True ping:{} ".format(server, ping_time))
            cursor.execute("""UPDATE servers SET status=TRUE, ping=?, up_number = up_number + 1 where adress = ?""", (ping_time, server))
        else:
            logging.debug("updating entry {} with status:False ping:{} ".format(server, ping_time))
            cursor.execute("""UPDATE servers SET status=FALSE, ping=?, down_number = down_number + 1 where adress = ?""", (ping_time, server))


def test_by_login(server):
    """
    Test a simple login and a list
    """
    try:
        ftp = FTP(server, timeout=10)
        print("ftp is {}".format(str(ftp)))
        ftp.login()
        ftp.retrlines('LIST')
        ftp.quit()
        return True
    except:
        return False

def ping(ip):
    """
    A simple ping wrapper, return 0 if an error occured or the host is unavailable.
    """
    p = Popen(['ping', '-c', '1', ip], stdout=PIPE, close_fds=True)
    output = str(p.communicate()[0])
    print(output)
    m = re.search('time=(.*?) ms', output)
    time = float(m.groups(0)[0])
    if m:
        return time
    else:
        return 0

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG) 
    logging.debug("debbug is on")
    conn = oursql.connect(host='127.0.0.1', user='server_app', passwd='metametame', db='server')
    ServerTester("127.0.0.1", conn).start()
