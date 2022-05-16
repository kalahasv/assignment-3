from flask import Flask, render_template, jsonify
import mysql.connector


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

if __name__ == '__main__':
    app.run()