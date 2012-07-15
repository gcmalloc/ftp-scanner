from bottle import Bottle, run, template, static_file
#from bottle-mysql import bottle_mysql
import oursql

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
    plugin = oursql.connect(host='127.0.0.1', user='server_app', passwd='metametame', db='server')
    db = plugin.cursor()
    db.execute("""SHOW FIELDS FROM servers;""")
    fields_name = db.fetchall()
    db.execute("""SELECT * FROM servers;""")
    rows = db.fetchall()
    ret_dict = dict()
    ret_dict['servers'] = [dict(zip(map(lambda a: a[0], fields_name), row)) for row in rows]
    db.close()
    return ret_dict

if __name__ == "__main__":
    run(ftp_server, reloader=True)
