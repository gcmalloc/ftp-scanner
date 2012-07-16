#/usr/bin/env python2
from ftplib import FTP
import netaddr
import socket
import time
from subprocess import Popen
from subprocess import PIPE
from multiprocessing import Process
import re
import logging
import os
import configparser

import oursql


def dbwrap(func):
    """Wrap a function in an idomatic SQL transaction.  The wrapped function
    should take a cursor as its first argument; other arguments will be
    preserved.
    """

    def new_func(self, *args, **kwargs):
        cursor = self.connection.cursor()
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
    """A forked process that test the server at regular interval,
    the default is 5 minute. The ip range should be in CIDR notation
    """
    def __init__(self, ip_range, conn, poll_interval=300):
        """
        Create the new poller process.
        Parameters
        ----------
        ip_range -- The CIDR range notation to poll.
        conn -- The connection to a SQL database with enough right to
                add table or at least insert into a table named servers.
        poll_interval -- The waiting time of the process.
        """
        self.ip_range = ip_range
        self.connection = conn
        self.interval = poll_interval
        Process.__init__(self)

    @dbwrap
    def init_db(self, cursor):
        """
        Insert the server entry into the table, flush the old data if any.
        Parameters
        ----------
        cursor -- the cursor to the database.
        """
        self.create_table()
        self.clean_table()

        for serv_ip in self._get_range():
            try:
                hostname = socket.gethostbyaddr(serv_ip)[1][0]
            except socket.error:
                hostname = ""
            logging.debug("insert address:{} host:{}".format(serv_ip, hostname))
            cursor.execute("""INSERT INTO servers VALUES (
                                ?,
                                ?,
                                FALSE,
                                0,
                                0,
                                0,
                                0)""", (serv_ip, hostname,))

    @dbwrap
    def clean_table(self, cursor):
        """
        Delete all the data in the server table
        Parameters
        ----------
        cursor -- the cursor to the database.
        """
        cursor.execute("TRUNCATE TABLE servers;")

    @dbwrap
    def create_table(self, cursor):
        """
        Create the servers table in self.conn. init the database table "servers".
         Parameters
        ----------
        cursor -- the cursor to the database.
        """
        cursor.execute("""DROP TABLE servers;
        """)
        cursor.execute("""CREATE TABLE IF NOT EXISTS servers(
                            address VARCHAR(15) NOT NULL,
                            host CHAR(50),
                            status TINYINT(1),
                            ping FLOAT UNSIGNED,
                            up_number INT UNSIGNED,
                            down_number INT UNSIGNED,
                            check_last TIMESTAMP,
                            PRIMARY KEY(address))""")

    def _get_range(self):
        """
        Return the ip range as a generator for this poller.
        """
        for i in netaddr.IPNetwork(self.ip_range):
            yield str(i)

    def run(self):
        """
        Run the process, start the poller.
        """
        self.init_db()
        while True:
            ip_range = self._get_range()
            for server_ip in ip_range:
                self.update_db_entry(server_ip)
            time.sleep(self.interval)

    @dbwrap
    def update_db_entry(self, cursor, server):
        """
        Update the server information with a ping and a new status
        Parameters
        ----------
        cursor -- The cursor to the database.
        server -- The server ip as a string.
        """
        #update the ping delay
        try:
            ping_time = ping(server)
        except Exception as e:
            logging.info("error : " + str(e))
            ping_time = 0

        status = test_by_login(server)
        if status:
            logging.debug("updating entry {} with status:True ping:{} ".format(server, ping_time))
            cursor.execute("""UPDATE servers SET
                                status=TRUE,
                                ping=?,
                                up_number = up_number + 1
                                where address = ?""", (ping_time, server))
        else:
            logging.debug("updating entry {} with status:False ping:{} ".format(server, ping_time))
            cursor.execute("""UPDATE servers SET
                                status=FALSE,
                                ping=?,
                                down_number = down_number + 1
                                where address = ?""", (ping_time, server))


def test_by_login(server, timeout=10):
    """
    Test a ftp server by login as anonymous and listing the root directory.
    Parameters
    ----------
    server -- An ipv4 address to connect to.
    timeout -- The login timeout, default as 10 seconds.
    """
    try:
        ftp = FTP(server, timeout=timeout)
        logging.info("ftp is {}".format(str(ftp)))
        ftp.login()
        ftp.dir(logging.info)
        ftp.quit()
        return True
    except socket.error:
        return False


def ping(ip_addr):
    """
    A simple ping wrapper, return 0 if an error occured or the host is unavailable.
    Parameters
    ----------
    ip_addr -- an ipv4 address to which a ping should be sent.
    """
    null_output = open(os.devnull, 'w')
    p = Popen(['ping', '-c', '1', ip_addr], stderr=null_output, stdout=PIPE, close_fds=True)
    null_output.close()
    output = str(p.communicate()[0])
    logging.debug(output)
    match = re.search('time=(.*?) ms', output)
    if match:
        time = float(match.groups(0)[0])
        return time
    else:
        return 0


if __name__ == "__main__":
    #just a launcher

    config = configparser.ConfigParser()
    config.readfp(open('config'))
    db_config = config['Database']
    test_conn = oursql.connect(host=db_config['host'], user=db_config['user'],
                               passwd=db_config['password'], db=db_config['database'])
    s = ServerTester(config['Scan']['range'], test_conn)
    s.create_table()
    s.start()
