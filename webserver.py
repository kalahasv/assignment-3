from flask import Flask, render_template, jsonify, session, redirect
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
    sql.commit()
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


if __name__ == '__main__':
    app.run()