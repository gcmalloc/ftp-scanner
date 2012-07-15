#!/bin/env python
"""
This simple webapp is a frontend to the scanner.py.
It return an interface for a GET method in the root folder, and the list
of servers in the /servers.
"""
from bottle import Bottle, run, template, static_file
#from bottle-mysql import bottle_mysql
import oursql
import json
import datetime
import time

ftp_server = Bottle()

#debug route
@ftp_server.route("/:filename")
def return_static(filename):
    return static_file(filename, root="./static")

#debug route
@ftp_server.route("/")
def main_page():
    return static_file("index.html", root="./static")


@ftp_server.route("/servers")
def return_update():
    """
    Return the list of the tested server as a dictionnary
    """
    plugin = oursql.connect(host='127.0.0.1', user='server_app', passwd='metametame', db='server')
    db = plugin.cursor()
    db.execute("""SHOW FIELDS FROM servers;""")
    fields_name = db.fetchall()
    db.execute("""SELECT * FROM servers;""")
    rows = db.fetchall()
    ret_dict = dict()
    ret_dict['servers'] = [dict(zip(map(lambda a: a[0], fields_name), row)) for row in rows]
    #TODO: change this, looking for a better json parser that can handle
    db.close()
    handler = lambda obj: int(time.mktime(obj.timetuple())) if isinstance(obj, datetime.datetime) else None
    return json.dumps(ret_dict, default=handler)

if __name__ == "__main__":
    run(ftp_server, reloader=True)
