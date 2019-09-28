# -*- coding: utf-8 -*-
"""
@author: 'xiazeng'
@created: 2017/1/17 
"""
import base64
import time
import json
import logging

from . import uixml, javadriver
import at.utils.commonhelper as commonhelper


logger = logging.getLogger()


class PyUiDevice(object):
    def __init__(self, jd):
        self.jd = jd    # type: javadriver.JavaDriver
        self.adb = jd.adb

    def enter(self, text):
        self.jd.push_op(u"直接输入: %s", text)
        self.request_method("setText", [text])

    def enter_zh(self, zh_text):
        self.jd.push_op(u"直接输入中文: %s", zh_text)
        self.request_method("setChineseText", [zh_text])

    def get_ui_view(self, selector, instance=0, views=None):
        if views is None:
            views = self.jd.dump_ui()
        return uixml.get_view(views, selector, instance)

    def click_on_ui_view(self, ui_view):
        """
        :type ui_view: uixml.UiView
        :return: 
        """
        self.click_on_point(ui_view.center_x, ui_view.center_y)

    def gesture(self, points):
        self.jd.push_op(u"手势: %s", json.dumps(points))
        params = []
        for point in points:
            params.append(point[0])
            params.append(point[1])
        self.jd.request_at_device("gesture", params)

    def click_on_point(self, x, y):
        self.jd.push_op(u"点击坐标: %s, %s", int(x), int(y))
        self.request_method("click", [int(x), int(y)])

    def screen_point_data(self, x, y, width, height, quality):
        self.jd.push_op(u"局部截图: %s, %s, %s, %s", int(x), int(y), int(width), int(height))
        base64_str = self.request_method("screenPoint", [int(x), int(y), int(width), int(height), int(quality)])
        base64_data = base64.b64decode(base64_str)
        return base64_data

    def screen_point(self, filename, x, y, width, height, quality=30):
        d = self.screen_point_data(x, y, width, height, quality)
        open(filename, "wb").write(d)

    def click_on_center(self):
        self.click_on_point(self.width()/2, self.height()/2)

    def swipe(self, x1, y1, x2, y2, steps):
        self.jd.push_op(u"滑动: %s,%s -> %s, %s", x1, y1, x2, y2)
        self.request_method("swipe", [x1, y1, x2, y2, steps])

    def swipe_left(self, rect, steps=20):
        y = rect.top + rect.height / 2
        x2, x1 = rect.left + rect.width / 4, rect.left + rect.width * 3 / 4
        self.jd.push_op(u"左滑: %s,%s -> %s, %s", x1, y, x2, y)
        self.request_method("swipe", [x1, y, x2, y, steps])

    def swipe_right(self, rect, steps=20):
        y = rect.top + rect.height / 2
        x1, x2 = rect.left + rect.width / 4, rect.left + rect.width * 3 / 4
        self.jd.push_op(u"左滑: %s,%s -> %s, %s", x1, y, x2, y)
        self.request_method("swipe", [x1, y, x2, y, steps])

    def long_click_on_point(self, x, y, duration=3*1000):
        self.jd.push_op(u"长按: %s, %s, 时间:%sms", int(x), int(y), duration)
        self.request_method("longClick", [int(x), int(y), duration])

    def long_click_on_center(self, duration=3*1000):
        self.long_click_on_point(self.width()/2, self.height()/2, duration)

    def get_rotation(self):
        """
        https://developer.android.com/reference/android/view/Surface.html#ROTATION_0
        :return: 0-3
        """
        return self.request_method("getRotation")

    def status_bar_height(self):
        return self.request_method("getStatusBarHeight")

    def height(self):
        """
        获取全屏幕大小（包括status_bar的高度）
        """
        return self.request_method("getDisplayHeight")

    def width(self):
        return self.request_method("getDisplayWidth")

    def device_size(self):
        return self.width(), self.height()

    def wait_window_update(self, pkg, timeout=10*1000):
        ret = self.request_method("waitForWindowUpdate", [pkg, timeout])
        if ret:
            time.sleep(2)
        return ret

    def wait_for_idle(self, timeout=10*1000):
        """
        等待一段时间内ui没有变化
        """
        return self.request_method("waitForIdle", [timeout])

    def current_package(self):
        return self.request_method("getCurrentPackageName")

    def drag(self, x1, y1, x2, y2, steps=10, first_sleep=200, last_sleep=200):
        """
        拖动
        """
        self.jd.push_op(u"拖动: %s,%s -> %s, %s", x1, y1, x2, y2)
        self.custom_drag(x1, y1, x2, y2, [first_sleep]+steps*[50]+[last_sleep])

    def scroll(self, x1, y1, x2, y2, steps=50):
        """
        滑动
        """
        self.jd.push_op(u"滑动: %s,%s -> %s, %s", x1, y1, x2, y2)
        self.jd.request_action(self.jd.ACTION_AT_DEVICE, "fastDrag", [x1, y1, x2, y2, 500, steps])

    def fast_scroll_one_forth_page(self, direction, num=1, milliseconds=100, steps=10):
        """
        滑动1/4个屏幕
        """
        width = self.width()
        height = self.height() - self.status_bar_height()
        for i in range(num):
            if direction == "up":
                self.fast_scroll(width/2, height*5/8, width/2, height*3/8, milliseconds, steps)
            elif direction == "down":
                self.fast_scroll(width / 2, height*3/8, width / 2, height*5/8, milliseconds, steps)
            elif direction == "left":
                self.fast_scroll(width*5/8, height/2, width*3/8, height/2, milliseconds, steps)
            elif direction == "right":
                self.fast_scroll(width*3/8, height/2, width*5/8, height/2, milliseconds, steps)
            else:
                raise TypeError("%s direction" % direction)
            time.sleep(0.1)

    def scroll_one_forth_page(self, direction, num=1):
        """
        滑动1/4个屏幕
        """
        width = self.width()
        height = self.height() - self.status_bar_height()
        for i in range(num):
            if direction == "up":
                self.scroll(width/2, height*5/8, width/2, height*3/8)
            elif direction == "down":
                self.scroll(width / 2, height*3/8, width / 2, height*5/8)
            elif direction == "left":
                self.scroll(width*5/8, height/2, width*3/8, height/2)
            elif direction == "right":
                self.scroll(width*3/8, height/2, width*5/8, height/2)
            else:
                raise TypeError("%s direction" % direction)
            time.sleep(0.2)

    def fast_scroll(self, x1, y1, x2, y2, milliseconds=500, steps=10):
        self.jd.push_op(u"快速滑动: %s,%s -> %s, %s 时间:%s", x1, y1, x2, y2, milliseconds)
        self.jd.request_action(self.jd.ACTION_AT_DEVICE, "fastDrag", [x1, y1, x2, y2, milliseconds, steps])

    def custom_drag(self, x1, y1, x2, y2, sleep_times):
        self.jd.request_action(self.jd.ACTION_AT_DEVICE, "customDrag", [x1, y1, x2, y2, json.dumps(sleep_times)])

    def request_method(self, method, params=None):
        return self.jd.request_at_device(method, params)

    def wake_up(self):
        """
        等待一段时间内ui没有变化
        """
        return self.request_method("wakeUp")

    # 处理rect相关的操作
    def screen_rect(self, filename, rect, quality=30):
        d = self.screen_point_data(rect.left, rect.top, rect.width, rect.height, quality)
        open(filename, "wb").write(d)

    def click(self, rect):
        self.click_on_point(rect.center_x, rect.center_y)

    def long_click(self, rect, microseconds=3*1000):
        self.long_click_on_point(rect.center_x, rect.center_y, microseconds)

    def screen_shot(self, filename, scale=1.0, quality=-1, max_idle=200):
        try:
            scale = scale if 0 < scale < 1.0 else 1
            quality = quality if 0 < quality < 100 else 30
            res = self.jd.request_at_device("screen", [float(scale), quality, max_idle])
            commonhelper.base64_to_file(res, filename)
        except Exception:
            logger.exception("uiautomator screen failed")
            self.adb.screen(filename)
        return filename
