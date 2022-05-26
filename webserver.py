from flask import Flask, render_template, jsonify, session, redirect, request
from flask_session import Session
import mysql.connector
import search
import json
from rake_nltk import Rake

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
r = Rake()

@app.errorhandler(404)
def invalid_path(error):
    return ""

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/query/")
def no_query():
    return jsonify(list())

@app.route("/ads", methods=["GET"])
def get_ads():
    if not session.get("loggedin"):
        return redirect("/")
    else:
        return render_template("createads.html")

@app.route("/ads", methods=["POST"])
def create_ads():
    if not session.get("loggedin"):
        return "Log in first!", 400
    else:
        try:
            query.execute("INSERT INTO ads (title, content, url, user_id) VALUES (%s, %s, %s, %s)", (request.values.get("title"), request.values.get("body"), request.values.get("site"), session["uid"]))
            l = query.lastrowid
            print(request.values.get("keywords[0][tag]"))
            counter = 0
            while True:
                if request.values.get("keywords[" + str(counter) + "][tag]") == None:
                    break
                query.execute("INSERT INTO ads_keywords (ad_id, word, cpc) VALUES (%s, %s, %s)", (l,request.values.get("keywords[" + str(counter) + "][tag]"), request.values.get("cpc")))
                counter += 1
            sql.commit()
            return "Thanks for submitting the ad!"
        except:
            return "bad input!", 400

@app.route("/query/<input>")
def query_db(input):
    input = input.split(" ")
    query.execute("SELECT * FROM terms WHERE content LIKE %s LIMIT 5", ("%".join(input) + "%",))
    result = query.fetchall()
    sql.commit()
    return jsonify(result)

@app.route("/search/<input>")
def search_page(input):
    d = list()
    a = list()
    r.extract_keywords_from_text(input)
    w = r.get_ranked_phrases()
    for word in w:
        query.execute("SELECT * FROM ads_keywords, ads WHERE word = %s AND ads_keywords.ad_id = ads.id ORDER BY cpc DESC", (word,))
        results = query.fetchall()
        sql.commit()
        if results:
            for result in results:
                print(result)
                query.execute("SELECT balance FROM users, ads, ads_keywords WHERE users.id = ads.user_id AND ads.id = ads_keywords.ad_id AND ads_keywords.word = %s LIMIT 1", (result[1],))
                res = query.fetchone()
                sql.commit()
                if res[0] > result[2]:
                    a.append("<span class=\"badge bg-warning text-dark\">Ad</span>" + result[4])
                    a.append(result[5])
                    a.append(result[6])
                    a.append("ad:" + str(result[0]) + ":" + result[1])
                    break
            break
    q = search.buildDocList(input.split(" "))
    if len(q) > 0:
        sort = search.getSortedList(q)
        urls = search.find_urls(sort)
        d = search.searchEngineData(urls)
        if len(a) > 0:
            d.insert(0, a)
    return render_template("searchresults.html", data=d)

@app.route("/render/<path:input>")
def render_page(input):
    if input[:3] == "ad:":
        frags = input.split(":")
        if len(frags) < 3:
            return 'Badly formatted URL', 400
        try:
            query.execute("SELECT users.id, ads.url, ads_keywords.cpc FROM users,ads,ads_keywords WHERE ads.id = %s AND ads.user_id = users.id AND ads.id = ads_keywords.ad_id AND ads_keywords.word = %s LIMIT 1", (frags[1],frags[2]))
            res = query.fetchone()
            print(res)
            query.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (res[2], res[0]))
            sql.commit()
            return redirect(res[1])
        except:
            return 'Ad Owner ran out of money', 400
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
            session["uid"] = result[0]
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
    search.searchInit()
    app.run()