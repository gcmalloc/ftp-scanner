from bottle import Bottle, run, template, static_file
#from bottle-mysql import bottle_mysql
import bottle-mysql.bottle_mysql
import oursql

ftp_server = Bottle()
plugin = bottle_mysql.Plugin(dbhost='127.0.0.1', dbuser='server_app', dbpass='metametame', dbname='server')

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
    db.execute("""SELECT * FROM servers""")
    rows = db.fetchall()
    jsonify(rows)

if __name__ == "__main__":
    run(ftp_server, reloader=True)
