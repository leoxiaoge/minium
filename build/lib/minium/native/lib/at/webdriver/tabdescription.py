# encoding=utf-8
import json


class TabDescription(object):
    def __init__(self, desc_text):
        self.desc_text = desc_text
        desc = {}
        try:
            desc = json.loads(desc_text)
        except ValueError:
            pass
        self.attached = desc.get("attached", None)
        self.empty = desc.get("empty", None)
        self.height = desc.get("height", None)
        self.screenX = desc.get("screenX", None)
        self.screenY = desc.get("screenY", None)
        self.visible = desc.get("visible", None)
        self.width = desc.get("width", None)
        self.title = desc.get("title", None)

    def __repr__(self):
        return self.desc_text
