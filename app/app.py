from bottle import app, run

ftp_server = app()

@ftp_server.route("/")
def return_main_page():
    return render_template("main.html")

@ftp_server.route("/update")
def return_update():
    jsonify(get_server_list())

def get_server_list():
    return "{}"

if __name__ == "__main__":
    run(ftp_server)
