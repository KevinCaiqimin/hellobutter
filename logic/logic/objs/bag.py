from logic.core import BaseObj

from bag_item import BagItem

class Bag (BaseObj):
    def __construct__(self):
        self.items = {}

    def save(self, dic):
        dic["items"] = {}

        saveItems = dic["items"]
        for k in self.items:
            saveItems[k] = {}
            item = self.items[k]
            item.save(saveItems[k])

    def load(self, dic):
        if dic is None:
            return
        self.items = {}
        if dic.get("items") is None:
            return
        saveItems = dic.get("items")
        for k in saveItems:
            itemData = saveItems[k]
            item = BagItem()
            item.load(itemData)
            self.items[k] = item
