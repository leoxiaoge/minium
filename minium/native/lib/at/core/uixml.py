#!/usr/bin/env python
# encoding:utf-8
# created:16/8/15

__author__ = 'xiazeng'

import traceback
import xml.dom.minidom
import xml.dom
import re
import logging

logger = logging.getLogger()


def parse_int(i):
    return int(i)


def parse_boolean(b):
    if b == "true":
        return True
    else:
        return False


def parse_bounds(bounds):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if m is None:
        return 0, 0, 0, 0
    return m.groups()


class ActivityProxy(object):
    def __init__(self, root_node, resgurad=None):
        self._document_node = root_node
        self._ui_views = [UiView(node, resgurad) for node in root_node.getElementsByTagName("node")]

    def find(self, **kwargs):
        for ui_view in self._ui_views:
            if ui_view.match(kwargs):
                return ui_view
        return None

    def find_all(self, **kwargs):
        ui_views = []
        for ui_view in self._ui_views:
            if ui_view.match(kwargs):
                ui_views.append(ui_view)
        return ui_views     # type: List[UiView]


class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2
        self.center_x = (self.left + self.right) / 2
        self.center_y = (self.top + self.bottom) / 2
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def to_list(self):
        return [self.left, self.top, self.right, self.bottom]

    def contains(self, others):
        pass

    def __repr__(self):
        return "%d, %d, %d, %d" % (self.left, self.top, self.right, self.bottom)


class MOTION_EVENT:
    CLICK = 1
    LONG_CLICK = 2
    DOUBLE_CLICK = 3
    SCROLL_CLICK = 4
    SCROLL_DOWN = 5
    SCROLL_UP = 6
    SCROLL_LEFT = 7
    SCROLL_RIGHT = 8
    INPUT = 9


class BaseView(object):
    """
    控件的抽象
    """
    def get_rect(self):
        raise RuntimeError(u"Not Implementation")

    def surrport_action_ids(self):
        raise RuntimeError(u"Not Implementation")

    def perform(self):
        pass


class UiView(BaseView):
    def __init__(self, node, resgurad=None):
        self._node = node
        self._node.uiview = self  # 使得 node 可以得到 uiview 对象
        self.index = parse_int(self.g("index"))
        self.rg = resgurad
        self.raw_id = self.g("resource-id")
        if resgurad is not None:
            self.rid = resgurad.retrace_id(self.g("resource-id"))
        else:
            self.rid = self.g("resource-id")
        self.text = self.g("text")
        self.cls_name = self.g("class")
        self.package = self.g("package")
        self.content_desc = self.g("content-desc")
        self.checkable = parse_boolean(self.g("checkable"))
        self.checked = parse_boolean(self.g("checked"))
        self.clickable = parse_boolean(self.g("clickable"))
        self.enabled = parse_boolean(self.g("enabled"))
        self.focusable = parse_boolean(self.g("focusable"))
        self.focused = parse_boolean(self.g("focused"))
        self.scrollable = parse_boolean(self.g("scrollable"))
        self.long_clickable = parse_boolean(self.g("long_clickable"))
        self.password = self.g("password")
        self.selected = self.g("selected")
        self.bound_raw = self.g("bounds")
        self.bounds = parse_bounds(self.bound_raw)
        self.x1 = max(parse_int(self.bounds[0]), 0)
        self.y1 = max(parse_int(self.bounds[1]), 0)
        self.x2 = max(parse_int(self.bounds[2]), self.x1)
        self.y2 = max(parse_int(self.bounds[3]), self.y1)
        self.center_x = (self.x1+self.x2) / 2
        self.center_y = (self.y1 + self.y2) / 2
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        self.size = self.width * self.height

    def surrport_action_ids(self):
        action_ids = []
        if self.clickable:  action_ids.append(MOTION_EVENT.CLICK)
        if self.long_clickable: action_ids.append(MOTION_EVENT.LONG_CLICK)
        return action_ids

    def get_rect(self):
        return Rect(self.x1, self.y1, self.x2, self.y2)

    def group_name(self):
        """
        用于分组的标识
        """
        return u", ".join([u"package="+self.package, u"class="+self.cls_name, u"resource-id="+self.rid, u"text="+self.text, u"content-desc="+self.content_desc, u"size=%d" % self.size])

    @property
    def parent(self):
        parent_node = self._node.parentNode

        # 这个方法有bug 第一个UiView 的parentNode不是UiView对象
        # if parent_node.nodeType == xml.dom.Node.DOCUMENT_NODE:
        #    return None
        # return UiView(parent_node, self.rg)

        # 每一个UiView对像在初始化，都给 _node 加了 uiview 引用自己。如果没有 uiview 属性，那就是到顶了
        try:
            return parent_node.uiview
        except:
            return None

    def get_ancestors(self):
        views = []
        parent = self.parent
        while parent:
            views.append(parent)
            parent = parent.parent
        return views

    def get_children(self):
        return [UiView(child_node) for child_node in self._node.childNodes if child_node.nodeType == xml.dom.Node.ELEMENT_NODE]

    def get_descendants(self):
        views = [self, ]
        for view in self.get_children():
            views += view.get_children()
        return views

    def first_text(self):
        if self.all_texts():
            return self.all_texts()[0]
        return ""

    def all_texts(self):
        return [v.text for v in self.get_descendants() if v.text]

    def find(self, **kwargs):
        if self.match(kwargs):
            return self
        for view in self.get_children():
            ret = view.find(**kwargs)
            if ret:
                return ret
        return None

    def sibling(self, **kwargs):
        if self.parent:
            for ui_view in self.parent.get_children():
                if ui_view != self and ui_view.match(kwargs):
                    return ui_view
        return None

    def __eq__(self, obj):
        if obj is None or not isinstance(obj, UiView):
            return False
        ret = self.index == obj.index and \
            self.cls_name == obj.cls_name and \
            self.x1 == obj.x1 and\
            self.y1 == obj.y1 and \
            self.x2 == obj.x2 and \
            self.y2 == obj.y2 and \
            self.rid == obj.rid and \
            self.content_desc == obj.content_desc and \
            (self.text == obj.text if self.cls_name.endswith(".EditText") else True)
        return ret

    def __ne__(self, other):
        if self == other:
            return False
        return True

    def __hash__(self):
        return hash(self.__repr__())

    def unique_key(self):
        return self._node.toxml()

    def contains(self, view):
        if self == view:
            return False
        if view is None:
            return False
        if view.x1 == self.x1 and view.y1 == self.y1:
            if self.x2 == view.x2 and self.y2 == view.y2:
                return False

        if self.x2 >= view.x1 >= self.x1 and self.y2 >= view.y1 >= self.y1:
            if self.x2 >= view.x2 >= self.x1 and self.y2 >= view.y2 >= self.y1:
                return True
        return False

    def match(self, selector):
        if selector is None:
            return True
        if not isinstance(selector, dict):
            logger.error("selector not dict, is %s" % type(selector))
            return False
        for key, value in selector.items():
            if not value:
                if getattr(self, key):
                    break
            elif isinstance(value, int):
                if value != getattr(self, key, -1):
                    break
            elif value not in getattr(self, key, ""):
                break
        else:
            return True
        return False

    def g(self, attr):
        value = self._node.getAttribute(attr)
        if isinstance(value, str):
            value = value.strip()
        return value

    def to_dict(self):
        return {
            "rid": self.rid,
            "index": self.index,
            "cls_name": self.cls_name,
            "text": self.first_text(),
            "package": self.package,
            "content_desc": self.content_desc,
            "clickable": self.clickable,
            "long_clickable": self.long_clickable,
            "scrollable": self.scrollable,
            "rect": self.get_rect().to_list(),
            "id": hash(self)
        }

    def __repr__(self):
        return ",".join([self.cls_name, self.content_desc, self.rid, self.package, self.first_text()])

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __str__(self):
        return u", ".join([u"package="+self.package, u"class="+self.cls_name, u"enabled=%s"%self.enabled,
                           u"resource-id="+self.rid, u"text="+self.text, u"content-desc="+self.content_desc,
                           u"bounds="+self.bound_raw])


def ui_views_contains_texts(ui_views, *texts):
    text_dict = dict((text, 0) for text in texts)
    for ui_view in ui_views:
        for text in text_dict:
            if text in ui_view.text:
                text_dict[text] = 1
    for k, v in text_dict.items():
        if v == 0:
            return False
    return True


def ui_views_match(ui_views, *sub_views):
    """
    todo: 重构
    :param ui_views: 
    :param sub_views: 
    :return: 
    """
    sub_set_views = set(sub_views)
    for ui_view in ui_views:
        for sub_view in sub_views:
            if sub_view in sub_set_views:
                sub_set_views.remove(sub_view)
    if sub_set_views:
        return False
    return True


def view_filter(views, selector):
    result_views = []
    for view in views:
        if view.match(selector):
            result_views.append(view)
    return result_views


def get_view(views, selector, instance=0):
    hit_views = get_views(views, selector)
    if len(hit_views) <= abs(instance):
        return None
    return hit_views[instance]  # type: UiView


def get_views(views, selector):
    rets = []
    try:
        iter(views)
    except TypeError:
        logger.info("not iterable")
    else:
        for view in views:
            if view.match(selector):
                rets.append(view)
    return rets


def get_view_parents(views, target):
    result_views = []
    for view in views:
        if view.contains(target):
            result_views.append(view)
    return result_views


def get_child(views, target, selector, instance=0):
    rets = get_children(views, target, selector)
    if len(rets) > abs(instance):
        return rets[instance]
    return None


def get_children(views, target, selector):
    rets = []
    for view in views:
        if target.contains(view):
            if view.match(selector):
                rets.append(view)
    return rets


def window_dump_parse(filename):
    dom = xml.dom.minidom.parse(filename)
    root = dom.documentElement
    nodes = root.getElementsByTagName("node")
    return [UiView(child) for child in nodes]


def window_dump_parse_str(s, resgurad=None):
    "根据XML实例化成View对象，平铺返回"
    nodes = []
    try:
        s = s.encode("utf-8")
        dom = xml.dom.minidom.parseString(s)    # 这里有可能出错, 因为传入的s有问题
        root = dom.documentElement
        nodes = root.getElementsByTagName("node")
    except Exception:
        logger.warn(s)
        logger.warn(traceback.format_exc())
    return [UiView(child, resgurad) for child in nodes]


def window_dump_2_activity_proxy(s, resgurad=None):
    try:
        s = s.encode("utf-8")
        dom = xml.dom.minidom.parseString(s)    # 这里有可能出错, 因为传入的s有问题
        root_node = dom.documentElement
        return ActivityProxy(root_node, resgurad)
    except Exception:
        logger.exception("parse xml failed")
    return None


def ui_views_same_rate(ui_views, other_views):
    if not other_views or not ui_views:
        return 0
    eq_num = 0
    for v in ui_views:
        for other_view in other_views:
            if other_view == v:
                eq_num += 1
                break
    return eq_num * 1.0 / len(other_views) if other_views else 0


def find_ui_view_by_element(ui_views, elem):
    for ui_view in ui_views:
        if elem.match_ui_view(ui_view):
            return ui_view
    return None


if __name__ == '__main__':
    vs = window_dump_parse("window_dump.xml")
    import pickle

    pickle.dump(vs, open('test.pickle', 'w'), 2)
    ss = pickle.load(open('test.pickle', 'rb'))
    print(1)
    # pickle.dump(vs, open('test.pickle', 'w'), 2)
