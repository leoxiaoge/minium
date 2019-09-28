# -*- coding: utf-8 -*-
"""
@author: 'xiazeng'
@created: 2016/10/21 
"""
import base64
import copy
import inspect
import json
import logging
import os.path
import time
import sys

from . import uixml, javadriver, resguard, uidevice

if sys.version_info[0] < 3:
    basestring = (str, unicode)
else:
    basestring = str

logger = logging.getLogger()


class AtSelector:
    SELECTOR_NIL = 0
    SELECTOR_TEXT = 1
    SELECTOR_START_TEXT = 2
    SELECTOR_CONTAINS_TEXT = 3
    SELECTOR_CLASS = 4
    SELECTOR_DESCRIPTION = 5
    SELECTOR_START_DESCRIPTION = 6
    SELECTOR_CONTAINS_DESCRIPTION = 7
    SELECTOR_INDEX = 8
    SELECTOR_INSTANCE = 9
    SELECTOR_ENABLED = 10
    SELECTOR_FOCUSED = 11
    SELECTOR_FOCUSABLE = 12
    SELECTOR_SCROLLABLE = 13
    SELECTOR_CLICKABLE = 14
    SELECTOR_CHECKED = 15
    SELECTOR_SELECTED = 16
    SELECTOR_ID = 17
    SELECTOR_PACKAGE_NAME = 18
    SELECTOR_CHILD = 19
    SELECTOR_CONTAINER = 20
    SELECTOR_PATTERN = 21
    SELECTOR_PARENT = 22
    SELECTOR_COUNT = 23
    SELECTOR_LONG_CLICKABLE = 24
    SELECTOR_TEXT_REGEX = 25
    SELECTOR_CLASS_REGEX = 26
    SELECTOR_DESCRIPTION_REGEX = 27
    SELECTOR_PACKAGE_NAME_REGEX = 28
    SELECTOR_RESOURCE_ID = 29
    SELECTOR_CHECKABLE = 30
    SELECTOR_RESOURCE_ID_REGEX = 31

    @classmethod
    def msg(cls, sid):
        msg = {
            cls.SELECTOR_TEXT: "text",
            cls.SELECTOR_RESOURCE_ID: "rid",
            cls.SELECTOR_DESCRIPTION: "description",
            cls.SELECTOR_CLASS: "class",
            cls.SELECTOR_CONTAINS_TEXT: "contains",
            cls.SELECTOR_ENABLED: "enabled",
            cls.SELECTOR_CHECKED: "checked",
            cls.SELECTOR_PACKAGE_NAME: "package",
            cls.SELECTOR_INSTANCE: "instance",
            cls.SELECTOR_INDEX: "index",
            cls.SELECTOR_CONTAINS_DESCRIPTION: "desc contains",
        }
        return msg.get(sid, sid)


class Element(object):
    default_jd = None
    default_resguard_filename = None

    def __init__(self, **selector):
        """
        :param selector:手动填入选择器， 如果需要试用多设备，请传入jd_instance实例
        """
        self._resguard = None
        self._private_jd = None
        self._resguard_filename = None
        if "jd_instance" in selector:
            self._private_jd = selector["jd_instance"]
            del selector["jd_instance"]
        if "resguard_filename" in selector:
            self._resguard_filename = selector["resguard_filename"]
            del selector["resguard_filename"]
        self._selector = selector
        self._selectors = [{"name": "current", "values": self._selector}]

    def match_ui_view(self, ui_view):
        for select_id, value in self.get_selector().items():
            if select_id == AtSelector.SELECTOR_PACKAGE_NAME:
                if value not in ui_view.package:
                    return False
            elif select_id == AtSelector.SELECTOR_CONTAINS_TEXT:
                if value not in ui_view.text:
                    return False
            elif select_id == AtSelector.SELECTOR_CONTAINS_DESCRIPTION:
                if value not in ui_view.content_desc:
                    return False
            elif select_id == AtSelector.SELECTOR_TEXT:
                if ui_view.text != value:
                    return False
            elif select_id == AtSelector.SELECTOR_CLASS:
                if ui_view.cls_name != value:
                    return False
            elif select_id == AtSelector.SELECTOR_RESOURCE_ID:
                if ui_view.raw_id != value:
                    return False
            elif select_id == AtSelector.SELECTOR_DESCRIPTION:
                if ui_view.content_desc != value:
                    return False
            else:
                raise RuntimeError("unknown select_id:%s" % select_id)
        return True

    def get_selector(self):
        return self._selector

    def __repr__(self):
        values = []
        for sid, value in self._selector.items():
            if sid == AtSelector.SELECTOR_RESOURCE_ID:
                value = self.resguard.retrace_id(value)
            values.append(u"%s=%s" % (AtSelector.msg(sid), value))
        return u', '.join(values)

    def __hash__(self):
        return hash(repr(self))

    @property
    def jd(self):
        """
        
        :return: 
        """
        if self._private_jd:
            return self._private_jd  # type: javadriver.JavaDriver
        elif Element.default_jd:
            return Element.default_jd   # type: javadriver.JavaDriver
        else:
            raise RuntimeError("elem should be passed a JavaDriver")

    @property
    def resguard(self):
        return resguard.Resguard.get_resguard(self.jd.serial)

    @classmethod
    def bind_java_driver(cls, jd):
        cls.default_jd = jd

    @classmethod
    def bind_resguard_filename(cls, filename):
        if filename:
            cls.default_resguard_filename = filename

    def child(self, **selector):
        """
        使用这个函数之后，选择器切换到孩子的选择器，后续的链式操作只对孩子生效
        """
        self._selector = copy.deepcopy(selector)
        self._selectors.append({"name": "child", "values": self._selector})
        return self

    def parent(self, **selector):
        """
        使用这个函数之后，选择器切换到孩子的选择器，后续的链式操作只对孩子生效
        """
        self._selector = copy.deepcopy(selector)
        self._selectors.append({"name": "parent", "values": self._selector})
        return self

    def not_found_exception(self, msg=u"控件没有找到"):
        return RuntimeError(msg + ", selector: " + self.__repr__())

    def text(self, text=None):
        """
        :param text: 完全匹配
        :return:
        """
        if text is None:
            return self.action("getText")  # self.get_attr("text")
        self._selector[AtSelector.SELECTOR_TEXT] = text
        return self

    def text_contains(self, text):
        """
        :param text: 匹配包含的文本
        :return:
        """
        self._selector[AtSelector.SELECTOR_CONTAINS_TEXT] = text
        return self

    def text_start(self, text):
        """
        :param text: 匹配开始的文本
        :return:
        """
        self._selector[AtSelector.SELECTOR_START_TEXT] = text
        return self

    def instance(self, index):
        """
        :param index: 匹配所以，安装XML的树形结构前序遍历的顺序
        :return:
        """
        self._selector[AtSelector.SELECTOR_INSTANCE] = index
        return self

    def text_matches(self, java_regx_str):
        """
        :param text: 匹配文本，请传入java的正则表达式
        :return:
        """
        self._selector[AtSelector.SELECTOR_TEXT_REGEX] = java_regx_str
        return self

    def rid(self, rid=None):
        """
        :param rid: 匹配resource-id
        :return:
        """
        if rid is None:
            return self.get_attr("resource_id")
        rid = self.resguard.resgurad_id(rid)
        self._selector[AtSelector.SELECTOR_RESOURCE_ID] = rid
        return self

    def index(self, index=None):    # 不建议使用，
        """
        :param index: 匹配index，uiAutomatorviewer中的index
        :return:
        """
        if index is None:
            return self.get_attr("index")
        self._selector[AtSelector.SELECTOR_INDEX] = index
        return self

    def clickable(self, true_or_false):
        """

        :param true_or_false:
        :return:
        """
        self._selector[AtSelector.SELECTOR_CLICKABLE] = true_or_false
        return self

    def checkable(self, true_or_false):
        """

        :param true_or_false:
        :return:
        """
        self._selector[AtSelector.SELECTOR_CHECKABLE] = true_or_false
        return self

    def checked(self, true_or_false):
        self._selector[AtSelector.SELECTOR_CHECKED] = true_or_false
        return self

    def enabled(self, true_or_false):
        """

        :param true_or_false:
        :return:
        """
        self._selector[AtSelector.SELECTOR_ENABLED] = true_or_false
        return self

    def focusable(self, true_or_false):
        """

        :param true_or_false:
        :return:
        """
        self._selector[AtSelector.SELECTOR_FOCUSABLE] = true_or_false
        return self

    def longClickable(self, true_or_false):
        """

        :param true_or_false:
        :return:
        """
        self._selector[AtSelector.SELECTOR_LONG_CLICKABLE] = true_or_false
        return self

    def selected(self, true_or_false):
        """

        :param true_or_false:
        :return:
        """
        self._selector[AtSelector.SELECTOR_SELECTED] = true_or_false
        return self

    def cls_name(self, cls_name=None):
        """

        :param cls_name: 匹配classs_name
        :return:
        """
        if cls_name is None:
            return self.get_attr("cls_name")
        self._selector[AtSelector.SELECTOR_CLASS] = cls_name
        return self

    def desc(self, desc, true_or_false=False):
        self.check_scroll(true_or_false)
        if desc is None:
            return self.action("getContentDescription")
        self._selector[AtSelector.SELECTOR_DESCRIPTION] = desc
        return self

    def pkg(self, pkg_name):
        """
        :param pkg_name: 控件所属的包名
        :return: Element
        """
        self._selector[AtSelector.SELECTOR_PACKAGE_NAME] = pkg_name
        return self

    def desc_contains(self, desc, true_or_false=False):
        self.check_scroll(true_or_false)
        self._selector[AtSelector.SELECTOR_CONTAINS_DESCRIPTION] = desc
        return self

    def desc_reg(self, desc, true_or_false=False):
        self.check_scroll(true_or_false)
        self._selector[AtSelector.SELECTOR_DESCRIPTION_REGEX] = desc
        return self

    def list_view(self):
        """
        选择ListView
        :return:
        """
        self.cls_name("android.widget.ListView")
        return self

    def edit_text(self):
        """
        选择EditText
        :return:
        """
        self.cls_name("android.widget.EditText")
        return self

    def get_attr(self, attr):
        views = uixml.get_views(self.jd.dump_ui(), self._selector)
        if not views:
            return None
        if len(views) == 1:
            if hasattr(views[0], attr):
                return getattr(self.views[0], attr)
            else:
                raise RuntimeError("no this attribute %s in %s" % (str(attr), type(views[0])))
        else:
            rets = []
            for v in views:
                if hasattr(v, attr):
                    rets.append(getattr(v, attr))
                else:
                    raise RuntimeError("no this attribute %s in %s" % (str(attr), type(v)))
            return rets

    def get_ui_views(self):
        ui_views = []
        for ui_view in self.jd.dump_ui():
            if self.match_ui_view(ui_view):
                ui_views.append(ui_view)
        return ui_views

    def wait_exists(self, timeout=10, should_throw_exception=False):
        """
        :param timeout:
        :return:
        """
        s = time.time()
        while time.time()-s < timeout:
            if self.exists(0.5):
                return True
            time.sleep(1)
        if should_throw_exception:
            raise RuntimeError("not exists")
        return False

    def wait_disappear(self, timeout=20, should_throw_exception=False):
        s = time.time()
        while time.time() - s < timeout:
            if not self.exists(0):
                return True
            time.sleep(1)
        else:
            if should_throw_exception:
                raise RuntimeError("still exists")
            return False

    def wait_disappear_by_idle(self, timeout, idle_time=1):
        """

        :param timeout:
        :param idle_time:
        :return:
        """
        s = time.time()
        while time.time() - s < timeout:
            if not self.exists(0):
                time.sleep(idle_time)
                if not self.exists(0):
                    return True
            time.sleep(0.1)
        else:
            return False

    def get_rect(self):
        bounds = self.action("pyGetBounds")
        return uixml.Rect(*bounds)

    def get_bounds(self):
        return self.action("pyGetBounds")

    def screen_data(self, quality=100):
        base64_str = self.action("screen", [quality])
        base64_data = base64.b64decode(base64_str)
        return base64_data

    def screen(self, filename, quality=100):
        d = self.screen_data(quality)
        open(filename, "wb").write(d)

    def get_text(self):
        return self.action("getText")

    def get_counts(self):
        if self.exists():
            return self.action("getCounts")
        return 0

    def get_desc(self):
        return self.action("getDesc")

    def sleep(self, seconds):
        """
        不推荐试用sleep，如果不能满足需求，请联系xiazeng
        """
        time.sleep(seconds)
        return self

    def action(self, method, params=None, is_async=False):
        if params is None:
            params = list()
        frames = inspect.stack()
        call = ""
        if len(frames) > 2:
            current_filename = frames[0][1]
            for frame in frames[1:]:
                if frame[1] != current_filename and os.path.basename(frame[1]) != "monitor.py":
                    call = ", called by %s in line %d" % (frame[3], frame[2])
                    break
        logger.info("action %s, params %s, selector %s, %s " % (method, json.dumps(params, ensure_ascii=False),
                                                                self.__repr__(), call))
        if is_async:
            import threading
            t = threading.Thread(target=self.jd.request_ui_selector, name="", args=(self._selectors, method, params))
            t.setDaemon(True)
            t.start()
        else:
            return self.jd.request_ui_selector(self._selectors, method, params)

    def record(self, name):
        self.jd.push_op(u"%s: %s", name, self)

    def check_scroll(self, is_scroll):
        if is_scroll:
            if not self.action("scrollExists"):
                logger.error("scrollExists failed")
            else:
                return True
        return False

    def scroll_exists(self):
        return self.check_scroll(True)

    def fast_click(self, is_scroll=False):
        self.record(u"快速点击")
        return self.long_click(100, is_scroll=is_scroll)

    def drag_to(self, x, y, steps=120, is_scroll=False, is_async=False):
        self.record(u"拖动")
        self.check_scroll(is_scroll)
        self.action("dragTo", [x, y, steps], is_async=is_async)

    def click_position(self,is_scroll=False, is_retry=False, is_url=False):
        """
        动作
        :param is_scroll:
        :return:
        """
        self.check_scroll(is_scroll)
        # ret = self.action("click")
        ret = False
        if ret is False:
            logger.warning("click failed, %s, is_retry %s", ret, is_retry)
            if is_retry:
                try:
                    bounds = self.get_bounds()
                    x = (bounds[0] + bounds[2]) / 8
                    y = (bounds[1] + bounds[3]) / 5
                    self.jd.adb.click_point(x, y)
                except:
                    logger.exception("retry click failed")
            if is_url:
                bounds = self.get_bounds()
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                x = bounds[0] + width / 2
                y = bounds[1] + height / 8
                device = uidevice.PyUiDevice(self.jd)
                time.sleep(2)
                if not device.click_on_point(x, y):
                    y += height / 8
                    time.sleep(2)
                    return device.click_on_point(x, y)
                else:
                    return True
        return ret

    def click(self, is_scroll=False, is_retry=False, is_url=False):
        """
        动作
        :param is_scroll:
        :return:
        """
        self.record(u"点击")
        self.check_scroll(is_scroll)

        if is_url:
            bounds = self.get_bounds()
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            x = bounds[0] + width / 2
            device = uidevice.PyUiDevice(self.jd)
            retrys = 3
            while retrys > 0:
                y = bounds[1] + height*9.0/10 / (retrys+1)   # 尝试3次分别点不同地方
                device.click_on_point(x, y)
                if self.wait_disappear(5):
                    return True
                retrys = retrys-1
            return False

        ret = self.action("click")
        if ret is False:
            logger.warning("click failed, %s, is_retry %s", ret, is_retry)
            if is_retry:
                try:
                    bounds = self.get_bounds()
                    x = (bounds[0] + bounds[2])/2
                    y = (bounds[1] + bounds[3])/2
                    self.jd.adb.click_point(x, y)
                except:
                    logger.exception("retry click failed")
        return ret

    def swipe_left(self, steps=50):
        self.record(u"向左滑动")
        return self.action("swipeLeft", [steps])

    def swipe_up(self, steps=50):
        self.record(u"向上滑动")
        return self.action("swipeUp", [steps])

    def swipe_right(self, steps=50):
        self.record(u"向右滑动")
        return self.action("swipeRight", [steps])

    def swipe_down(self, steps=50):
        self.record(u"向下滑动")
        return self.action("swipeDown", [steps])

    def delay_click(self, delay):
        """
        延后delay秒点击
        :param delay:
        :return:
        """
        self.record(u"延迟点击(%ss):" % delay)
        return self.action("delayClick", [delay*1000])

    def double_click(self, is_scroll=False):
        self.record(u"双击")
        self.check_scroll(is_scroll)
        return self.action("doubleClick", [100])

    def long_click(self,  duration=4000, is_scroll=False):
        self.record(u"长按")
        self.check_scroll(is_scroll)
        return self.action("longPress", [duration, ])

    def click_if_exists(self, timeout=2):
        if timeout == 0:
            if self.exists(0):
                return self.click()
            else:
                logger.warn("not exists by selector:" + self.__repr__())
                return False
        else:
            t = time.time()
            while time.time() - t < timeout:
                if self.exists(0.5):
                    return self.click()
            else:
                logger.warn("not exists by selector:" + self.__repr__())
                return False

    def click_button_right(self, is_scroll=False):
        self.record(u"点击右下角")
        self.check_scroll(is_scroll)
        return self.action("clickBottomRight")

    def enter(self, text, is_clear_text=False, is_scroll=False, is_click=True):
        self.record(u"输入:%s" % text)
        self.check_scroll(is_scroll)
        if not isinstance(text, basestring):
            raise RuntimeError(u"需要传入字符串，而实际类型是：%s" % str(type(text)))
        logger.info("enter %s %s, %s" % (text, str(self._selector), is_clear_text))
        return self.action("setText", [text, is_clear_text, is_click])

    def enter_chinese(self, text, is_clear_text=False, is_scroll=False, is_click=True):
        self.record(u"输(%s)" % text)
        self.check_scroll(is_scroll)
        if not isinstance(text, basestring):
            raise RuntimeError(u"需要传入字符串，而实际类型是：%s" % str(type(text)))
        logger.info("enter %s %s" % (text, str(self._selector)))
        return self.action("setChineseText", [text, is_clear_text, is_click])

    def exists(self, seconds=3.000):    # seconds指一个最小时间，而不是最大时间，最大时间无法控制
        self.record(u"检查")
        return self.action("exists", [int(seconds*1000)])

    def tap_scroll(self, direction="up"):
        """

        :param direction: up, down, left, right
        :return:
        """
        rect = self.get_bounds()
        device = uidevice.PyUiDevice(self.jd)
        center_x = (rect[0]+rect[2])/2
        center_y = (rect[1]+rect[3])/2
        min_width = rect[0] + int((rect[2] - rect[0])*1.0/4)
        max_width = rect[0] + int((rect[2] - rect[0])*3.0/4)
        min_height = rect[1] + int((rect[3] - rect[1])*1.0/4)
        max_height = rect[1] + int((rect[3] - rect[1])*3.0/4)
        duration = 100
        steps = 2
        if direction == "up":
            device.fast_scroll(center_x, max_height, center_x, min_height, duration, steps)
        elif direction == "down":
            device.fast_scroll(center_x, min_height, center_x, max_height, duration, steps)
        elif direction == "left":
            device.fast_scroll(max_width, center_y, min_width, center_y, duration, steps)
        elif direction == "right":
            device.fast_scroll(min_width, center_y, max_width, center_y, duration, steps)
        else:
            raise RuntimeError("direction should be one of up, down, left, right")
