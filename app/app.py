#!/bin/env python
"""
This simple webapp is a frontend to the scanner.py.
It return an interface for a GET method in the root folder, and the list
of servers in the /servers.
"""
from bottle import Bottle, run, static_file
import oursql
import json
import datetime
import time
import configparser

scanner_app = Bottle()

config = configparser.ConfigParser()
config.readfp(open('config'))
db_config = config['Database']
plugin = oursql.connect(host=db_config['host'], user=db_config['user'],
                        passwd=db_config['password'], db=db_config['database'])


@scanner_app.route("/:filename")
def return_static(filename):
    """
    Return static file `filename`.
    """
    return static_file(filename, root="./app/static")

#debug route
@scanner_app.route("/")
def main_page():
    """
    Return the main page.
    """
    return static_file("index.html", root="./app/static")


@scanner_app.route("/servers")
def return_update():
    """
    Return the list of tested servers as a dictionnary.
    """
    db = plugin.cursor()

    db.execute("""SHOW FIELDS FROM servers;""")
    fields_name = db.fetchall()

    db.execute("""SELECT * FROM servers;""")
    rows = db.fetchall()
    ret_dict = dict()
    ret_dict['servers'] = [dict(zip(map(lambda a: a[0], fields_name), row)) for row in rows]
    db.close()
    handler = lambda obj: int(time.mktime(obj.timetuple())) if isinstance(obj, datetime.datetime) else None
    return json.dumps(ret_dict, default=handler)

if __name__ == "__main__":
    #a test server
    run(scanner_app, reloader=True)
