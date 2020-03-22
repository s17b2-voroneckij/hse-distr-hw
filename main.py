from flask import Flask, request, abort
import sqlite3
import json
import time
import hashlib
import psycopg2
from random import randint
app = Flask(__name__)


def random_token():
    res = ''
    for i in range(20):
        res += chr(randint(ord('a'), ord('z')))
    return res


@app.route("/registerUser", methods=["POST"])
def register_user():
    data = request.args
    login = data['login']
    password = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    conn = db.cursor()
    conn.execute("SELECT count(*) FROM users_table WHERE login='%s'" % login)
    if conn.fetchall()[0][0] >= 1:
        return "User with such name already exists"
    conn.execute("INSERT INTO users_table VALUES ('%s', '%s', '', 0)" % (login, password))
    db.commit()
    conn.close()
    return "Success"


@app.route("/authorization", methods=["PUT"])
def authorize():
    data = request.args
    login = data['login']
    password = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    conn = db.cursor()
    conn.execute("SELECT count(*) FROM users_table WHERE login='%s' and password='%s'" % (login, password))
    if conn.fetchall()[0][0]:
        refresh_token = random_token()
        access_token = random_token()
        tokens.add(access_token)
        conn.execute("UPDATE users_table SET refresh_token='%s', expire_time=%d WHERE login='%s'" % (refresh_token, time.time()
                                                                    + SECONDS_IN_DAY, login))
        db.commit()
        conn.close()
        return {'refresh_token': refresh_token, 'access_token': access_token}
    else:
        abort(403)


@app.route("/getNewToken", methods=["PUT"])
def get_new_token():
    data = request.args
    old_token = data['refresh_token']
    conn = db.cursor()
    conn.execute(
        "SELECT count(*) FROM users_table WHERE refresh_token='%s' and expire_time > %d" % (old_token, time.time()))
    if conn.fetchall()[0][0] >= 1:
        refresh_token = random_token()
        access_token = random_token()
        tokens.add(access_token)
        conn.execute("UPDATE users_table SET refresh_token='%s', expire_time=%d WHERE refresh_token='%s'" % (refresh_token, time.time() + SECONDS_IN_DAY, old_token))
        db.commit()
        conn.close()
        return {'refresh_token': refresh_token, 'access_token': access_token}
    else:
        abort(403)


def validate_token(data):
    if data['token'] not in tokens:
        abort(403)


@app.route("/validateToken", methods=["GET"])
def validate_token_third_party():
    data = request.args
    validate_token(data)
    return "This token is OK"


@app.route("/getAll", methods=["GET"])
def get_all():
    data = request.args
    validate_token(data)
    conn = db.cursor()
    conn.execute("SELECT * from items ORDER BY id")
    return json.dumps(conn.fetchall())


@app.route("/getByID", methods=["GET"])
def get_by_id():
    data = request.args
    validate_token(data)
    id = int(data['id'])
    conn = db.cursor()
    conn.execute("SELECT * FROM items WHERE id = %d" % id)
    result = conn.fetchall()
    if len(result) == 1:
        return json.dumps(result[0])
    else:
        abort(404)


@app.route("/addItem", methods=["POST"])
def add_item():
    data = request.args
    validate_token(data)
    conn = db.cursor()
    id = int(data['id'])
    name = data['name']
    cat = data['category']
    conn.execute("SELECT count(*) from items WHERE id = %d" % id)
    if conn.fetchall()[0][0] >= 1:
        abort(404)
    conn.execute("INSERT INTO items VALUES (%d, '%s', '%s')" % (id, name, cat))
    db.commit()
    conn.close()
    return "Added successfully"


@app.route("/removeItem", methods=["DELETE"])
def delete_item():
    conn = db.cursor()
    data = request.args
    validate_token(data)
    id = int(data['id'])
    conn.execute("SELECT count(*) from items WHERE id = %d" % id)
    if conn.fetchall()[0][0] == 0:
        abort(404)
    else:
        conn.execute("DELETE FROM items WHERE id = %d" % id)
        db.commit()
        conn.close()
        return "Deleted"


@app.route("/editItem", methods=["PUT"])
def edit_item():
    data = request.args
    validate_token(data)
    id = int(data['id'])
    conn = db.cursor()
    conn.execute("SELECT count(*) from items WHERE id = %d" % id)
    if conn.fetchall()[0][0] == 0:
        abort(404)
    name = data['name']
    cat = data['category']
    conn.execute("DELETE FROM items WHERE id = %d" % id)
    conn.execute("INSERT INTO items VALUES (%d, '%s', '%s')" % (id, name, cat))
    db.commit()
    conn.close()
    return "Edited successfully"


tokens = set()
db = psycopg2.connect(dbname='market', user='server',
                        password='123456', host='db')
SECONDS_IN_DAY = 24 * 60 * 60
conn = db.cursor()
db.commit()
try:
    conn.execute("""CREATE TABLE items
                    (id INTEGER, name TEXT, category TEXT)""")
except psycopg2.errors.DuplicateTable:
    db.commit()

try:
    conn.execute("""CREATE TABLE users_table
              (login TEXT, password TEXT, refresh_token TEXT, expire_time INTEGER)""")

except psycopg2.errors.DuplicateTable:
    db.commit()

conn.close()
print("READY TO RUN")
app.run(host='0.0.0.0')
