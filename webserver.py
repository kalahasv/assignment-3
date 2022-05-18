from flask import Flask, render_template, jsonify, session, redirect, request
from flask_session import Session
import mysql.connector
import search
import json


sql = mysql.connector.connect(
        host="localhost",
        user="search",
        password="",
        database="search_engine",
        pool_name="sqlPool",
        pool_size=3
    )
query = sql.cursor()
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.errorhandler(404)
def invalid_path(error):
    return ""

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/query/")
def no_query():
    return jsonify(list())


@app.route("/query/<input>")
def query_db(input):
    input = input.split(" ")
    query.execute("SELECT * FROM terms WHERE content LIKE %s LIMIT 5", ("%".join(input) + "%",))
    result = query.fetchall()
    return jsonify(result)

@app.route("/search/<input>")
def search_page(input):
    q = search.buildDocList(input.split(" "))
    d = list()
    if len(q) > 0:
        sort = search.getSortedList(q)
        urls = search.find_urls(sort)
        d = search.searchEngineData(urls)
    return render_template("searchresults.html", data=d)

@app.route("/render/<path:input>")
def render_page(input):
    try:
        with open(input) as f:
            data = json.load(f)
        return data["content"]
    except:
        return "Invalid file path"

@app.route("/login", methods=["GET"])
def login():
    if session.get("loggedin"):
        return redirect("/")
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    if session.get("loggedin"):
        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login_auth():
    if session.get("loggedin"):
        return 'Already logged in!', 400
    if request.form.get("email") and request.form.get("password"):
        query.execute("SELECT * FROM users WHERE email = %s AND password = %s", (request.form.get("email"), request.form.get("password")))
        result = query.fetchone()
        if result:
            session["loggedin"] = True
            session["uid"] = query.lastrowid
            session["user"] = request.form.get("email")
            return 'Success!'
        else:
            return 'Invalid credentials!', 401
    else:
        return 'Invalid credentials!', 401

@app.route("/register", methods=["POST"])
def register_auth():
    if session.get("loggedin"):
        return 'Already logged in!', 401
    if request.form.get("email") and request.form.get("password"):
        query.execute("SELECT * FROM users WHERE email = %s", (request.form.get("email"),))
        result = query.fetchone()
        if result:
            return 'User exists!', 401
        else:
            query.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (request.form.get("email"), request.form.get("password")))
            sql.commit()
            session["loggedin"] = True
            session["uid"] = query.lastrowid
            session["user"] = request.form.get("email")
            return 'Success!'
    else:
        return 'Invalid request!', 401

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")


if __name__ == '__main__':
    app.run()