from bottle import Bottle, run, template
import oursql
ftp_server = Bottle()

@ftp_server.route("/")
def return_main_page():
    return template("templates/main.html")

@ftp_server.route("/servers")
def return_update():
    jsonify(get_server_list())

def get_server_list():
    cursor.excecute("""
    SELECT *
    FROM servers
    """)

if __name__ == "__main__":
    run(ftp_server, reloader=True)
