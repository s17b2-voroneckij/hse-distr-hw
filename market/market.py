from flask import Flask, request
import json
import time
import hashlib
import psycopg2
from random import randint
from commons import *
app = Flask(__name__)


def random_token():
    res = ''
    for i in range(20):
        res += chr(randint(ord('a'), ord('z')))
    return res


def make_item(item):
    return {'id': item[0], 'name': item[1], 'category': item[2]}

@app.route("/registerUser", methods=["POST"])
def register_user():
    data = request.args
    login = data['login']
    password = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    conn = db.cursor()
    conn.execute("SELECT count(*) FROM users_table WHERE login='%s'" % login)
    if conn.fetchall()[0][0] >= 1:
        return return_string("User with such name already exists")
    conn.execute("INSERT INTO users_table VALUES ('%s', '%s', '', 0)" % (login, password))
    db.commit()
    conn.close()
    return return_string("Success")


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
        return return_data({'refresh_token': refresh_token, 'access_token': access_token})
    else:
        return return_error(403, "login or password incorrect")


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
        return return_data({'refresh_token': refresh_token, 'access_token': access_token})
    else:
        return return_error(403, "refresh_time invalid or expired")


def check_token(data):
    return data['token'] in tokens


@app.route("/validateToken", methods=["GET"])
def validate_token_third_party():
    data = request.args
    if not check_token(data):
        return return_error(404, "token invalid")
    return return_string("This token is OK")


@app.route("/getAll", methods=["GET"])
def get_all():
    data = request.args
    if not check_token(data):
        return return_error(404, "token invalid")
    conn = db.cursor()
    if 'per_page' in data:
        per_page = int(data['per_page'])
    else:
        per_page = 200
    if 'page' in data:
        page = int(data['page'])
    else:
        page = 0
    conn.execute("SELECT * from items ORDER BY id")
    items = conn.fetchall()
    items = list(map(make_item, items))
    return return_data(items[page * per_page: (page + 1) * per_page])


@app.route("/getByID", methods=["GET"])
def get_by_id():
    data = request.args
    if not check_token(data):
        return return_error(404, "token invalid")
    id = int(data['id'])
    conn = db.cursor()
    conn.execute("SELECT * FROM items WHERE id = %d" % id)
    items = conn.fetchall()
    items = list(map(make_item, items))
    if len(items) == 1:
        return return_data(items[0])
    else:
        return return_error(404, "item not found")


@app.route("/addItem", methods=["POST"])
def add_item():
    data = request.args
    if not check_token(data):
        return return_error(404, "token invalid")
    conn = db.cursor()
    id = int(data['id'])
    name = data['name']
    cat = data['category']
    conn.execute("SELECT count(*) from items WHERE id = %d" % id)
    if conn.fetchall()[0][0] >= 1:
        return return_error(404, "item already exists")
    conn.execute("INSERT INTO items VALUES (%d, '%s', '%s')" % (id, name, cat))
    db.commit()
    conn.close()
    return return_string("Added successfully")


@app.route("/removeItem", methods=["DELETE"])
def delete_item():
    conn = db.cursor()
    data = request.args
    if not check_token(data):
        return return_error(404, "token invalid")
    id = int(data['id'])
    conn.execute("SELECT count(*) from items WHERE id = %d" % id)
    if conn.fetchall()[0][0] == 0:
        return return_error(404, "element doesn`t exist")
    else:
        conn.execute("DELETE FROM items WHERE id = %d" % id)
        db.commit()
        conn.close()
        return return_string("Deleted")


@app.route("/editItem", methods=["PUT"])
def edit_item():
    data = request.args
    if not check_token(data):
        return return_error(404, "token invalid")
    id = int(data['id'])
    conn = db.cursor()
    conn.execute("SELECT count(*) from items WHERE id = %d" % id)
    if conn.fetchall()[0][0] == 0:
        return return_error(404, "item not found")
    name = data['name']
    cat = data['category']
    conn.execute("DELETE FROM items WHERE id = %d" % id)
    conn.execute("INSERT INTO items VALUES (%d, '%s', '%s')" % (id, name, cat))
    db.commit()
    conn.close()
    return return_string("Edited successfully")


tokens = set()
db = psycopg2.connect(dbname='market', user='server',
                      password='123456', host='db')
SECONDS_IN_DAY = 24 * 60 * 60
conn = db.cursor()
db.commit()
conn.execute("""CREATE TABLE IF NOT EXISTS items
                    (id INTEGER, name TEXT, category TEXT)""")

conn.execute("""CREATE TABLE IF NOT EXISTS users_table
              (login TEXT, password TEXT, refresh_token TEXT, expire_time INTEGER)""")


conn.close()
print("READY TO RUN MARKET")
app.run(host='0.0.0.0')
