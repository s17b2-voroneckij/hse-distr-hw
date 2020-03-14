from flask import Flask, request, abort
import sqlite3
import json
app = Flask(__name__)


@app.route("/getAll", methods=["GET"])
def get_all():
    data = request.args
    conn = sqlite3.connect("shop.db")
    return json.dumps(conn.execute("SELECT * from items ORDER BY id").fetchall())


@app.route("/getByID", methods=["GET"])
def get_by_id():
    data = request.args
    id = int(data['id'])
    conn = sqlite3.connect("shop.db")
    result = conn.execute("SELECT * FROM items WHERE id = %d" % id).fetchall()
    if len(result) == 1:
        return json.dumps(result[0])
    else:
        abort(404)


@app.route("/addItem", methods=["POST"])
def add_item():
    data = request.args
    conn = sqlite3.connect("shop.db")
    id = int(data['id'])
    name = data['name']
    cat = data['category']
    if conn.execute("SELECT count(*) from items WHERE id = %d" % id).fetchall()[0][0] >= 1:
        abort(404)
    conn.execute("INSERT INTO items VALUES (%d, '%s', '%s')" % (id, name, cat))
    conn.commit()
    conn.close()
    return "Added successfully"


@app.route("/removeItem", methods=["DELETE"])
def delete_item():
    conn = sqlite3.connect("shop.db")
    data = request.args
    id = int(data['id'])
    if conn.execute("SELECT count(*) from items WHERE id = %d" % id).fetchall()[0][0] == 0:
        abort(404)
    else:
        conn.execute("DELETE FROM items WHERE id = %d" % id)
        conn.commit()
        conn.close()
        return "Deleted"


@app.route("/editItem", methods=["PUT"])
def edit_item():
    data = request.args
    id = int(data['id'])
    conn = sqlite3.connect("shop.db")
    if conn.execute("SELECT count(*) from items WHERE id = %d" % id).fetchall()[0][0] == 0:
        abort(404)
    name = data['name']
    cat = data['category']
    conn.execute("DELETE FROM items WHERE id = %d" % id)
    conn.execute("INSERT INTO items VALUES (%d, '%s', '%s')" % (id, name, cat))
    conn.commit()
    conn.close()
    return "Edited successfully"


conn = sqlite3.connect("shop.db")
try:
    conn.execute("""CREATE TABLE items
              (id INTEGER, name TEXT, category TEXT)""")
except sqlite3.OperationalError as err:
    if err.args[0] == 'table items already exists':
        pass
    else:
        raise err

conn.close()
app.run()
