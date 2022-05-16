from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/query")
def query():
    return jsonify({"hello": "world"})

if __name__ == '__main__':
    app.run()