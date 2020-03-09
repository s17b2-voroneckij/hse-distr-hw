import json

class Item:
    def __init__(self, name, id, category):
        self.name = name
        self.id = id
        self.category = category

    def __str__(self):
        return "{name: %s, id: %d, category: %s" % (self.name, self.id, self.category)


class ItemEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)