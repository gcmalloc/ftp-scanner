from bottle import app

a = app(__file__)

@app.route("/")
def return_main_page():
    return render_template("main.html")

@app.route("/update")
def return_update():
    jsonify(get_server_list())

def get_server_list():

