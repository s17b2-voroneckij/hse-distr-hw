from flask import Flask, request, abort
from item import *
app = Flask(__name__)


@app.route("/getAll", methods=["GET"])
def get_all():
    data = request.args
    return json.dumps(items, cls=ItemEncoder)


@app.route("/getByID", methods=["GET"])
def get_by_id():
    data = request.args
    id = int(data['id'])
    if id in items:
        return json.dumps(items[id], cls=ItemEncoder)
    else:
        abort(404)


@app.route("/addItem", methods=["POST"])
def add_item():
    data = request.args
    id = int(data['id'])
    if id in items:
        abort(208)
    name = data['name']
    cat = data['category']
    items[id] = Item(name, id, cat)
    return "Added successfully"


@app.route("/removeItem", methods=["DELETE"])
def delete_item():
    data = request.args
    print(data)
    id = int(data['id'])
    if id not in items:
        abort(404)
    else:
        items.pop(id)
        return "Deleted"


@app.route("/editItem", methods=["PUT"])
def edit_item():
    data = request.args
    print(data)
    id = int(data['id'])
    if id not in items:
        abort(404)
    name = data['name']
    cat = data['category']
    items[id] = Item(name, id, cat)
    return "Edited successfully"


items = dict()
app.run(host='0.0.0.0')
