# -*- coding: utf-8 -*-
"""
@author: 'xiazeng'
@created: 2016/12/22 
"""
import logging
import time
import at
from . import jsapi


logger = logging.getLogger()
MM_X5_CLASS_NAME = "com.tencent.smtt.webkit.WebView"
ANDROID_WEBKIT_CLASS_NAME = "android.webkit.WebView"


class WebElementNotFound(RuntimeError):
    pass


class WebElement(object):
    def __init__(self, page, web_view_bounds = None, hid=None, css=None, text=None, cls_name=None, xpath=None, tag_name=None, name=None):
        self.page = page
        self.ws_url = ""
        self.wrap_view_cls = MM_X5_CLASS_NAME
        serial = self.page.serial
        self.at = at.At(serial)
        self.web_view_rect = web_view_bounds
        self._json_element = None
        self._js_element = None
        if hid:
            word = "id"
            selector = hid
            self._selector = "#%s" % hid#根据id来进行css_selector查找
        elif css:
            word = "cssSelector"
            selector = css
            self._selector = css #css语句
        elif text:
            word = "textContent"
            selector = text
            self._selector = ':text("%s")' % text #输入文字
        elif cls_name:
            word = "className"
            selector = cls_name
            self._selector = '.%s' % text  #根据.来输入类名
        elif xpath:
            word = "xpath"
            selector = xpath
        elif tag_name:
            word = "tagName"
            selector = tag_name
            self._selector = tag_name
        elif name:
            word = "name"
            selector = name
            self._selector = name
        else:
            raise AssertionError("no way to go")
        self.word = word
        self.selector = selector

        self._instance = 0

    def instance(self, num):#相同元素中的第几个
        self._instance = num
        return self

    def word_big_first_letter(self):#转第一个字母为大写字母
        return self.word[0].upper()+self.word[1:]

    def wait_exists(self, timeout=10):#等待出现
        s = time.time()
        while time.time() -s < timeout:
            if self.exists():
                return True
            time.sleep(1)
        return False

    def screen(self, filename, quality=100):
        """
        截图，并且圈出对应的坐标点
        """
        x, y, width, height = self.rect()
        self.at.device.screen_point(filename, x, y, width, height, quality)

    def scroll_to(self, x, y):
        self.page.invoke_js(jsapi.SCROLL_TO, x, y)

    def click(self):
        if not self.page.click_by_ui:
            raise RuntimeError("not implementation")
        else:
            # self.wait_exists()
            self.find_json_element()
            if not self._js_element['in_screen']:
                self.call_js("scrollIntoView", [])
                # self.scroll_to(self._js_element['rect']['left'], self._js_element['rect']['top'])
                time.sleep(2)
                self.find_json_element(True)
            # if not self._js_element['in_screen']:
            #     raise RuntimeError(u"element invisible")
            x, y, width, height = self.rect()
            self.page.close()
            x = x + width / 2
            y = y + height / 2

            time.sleep(1)
            self.at.device.click_on_point(x, y)#点击元素的中心点
            time.sleep(1)

    def get_center_position(self):
        if not self.page.click_by_ui:
            raise RuntimeError("not implementation")
        else:
            # self.wait_exists()
            self.find_json_element()
            if not self._js_element['in_screen']:
                self.call_js("scrollIntoView", [])
                # self.scroll_to(self._js_element['rect']['left'], self._js_element['rect']['top'])
                time.sleep(2)
                self.find_json_element(True)
            if not self._js_element['in_screen']:
                raise RuntimeError(u"element invisible")
            x, y, width, height = self.rect()
            x = x + width / 2
            y = y + height / 2
            return x, y

    def long_click(self, duration=3000):
        method_name = self.word
        if not self.page.click_by_ui:
            raise RuntimeError("not implementation")
        else:
            # self.wait_exists()
            x, y, width, height = self.rect()
            x = x + width / 2
            y = y + height / 2
            time.sleep(1)
            self.at.device.long_click_on_point(x, y, duration)
            time.sleep(1)

    def web_rect(self):
        ret = self.find_json_element()
        json_rect = ret['rect']
        return json_rect["left"], json_rect['top'], json_rect["width"], json_rect["height"]

    def rect(self):
        x, y, width, height = self.web_rect()
        target_x, target_y = self.transfer_web_point(x, y)
        target_width, target_height = self.transfer_web_distance(width, height)
        return target_x, target_y, target_width, target_height

    def call_js(self, sub_method, args, timeout=10):
        r = None
        t = time.time()
        end_time = time.time()
        while end_time - t < timeout:
            try:
                r = self.page.invoke_js(jsapi.ELEMENT_OPERATION, self.selector, sub_method, args, self._instance)
                break
            except jsapi.ElementNotExists as e:
                end_time = time.time()
                if end_time - t < timeout:
                    time.sleep(2)
                else:
                    raise e
        return r

    def find_json_element(self, is_refresh=False, timeout=10):
        if self._js_element is None or is_refresh:
            self._js_element = self.call_js(None, [], timeout)
        return self._js_element

    def point_rate(self):
        rect = self.web_view_rect
        page_width = self.page.width
        page_height = self.page.height
        view_width = rect[2] - rect[0]
        view_height = rect[3] - rect[1]
        return view_width*1.0/page_width, view_height*1.0/page_height

    def transfer_web_distance(self, x, y):
        x_rate, y_rate = self.point_rate()
        return x*x_rate, y * y_rate

    def transfer_web_point(self, x, y):
        x = x if x > 0 else 0
        y = y if y > 0 else 0
        rect = self.web_view_rect
        x_rate, y_rate = self.point_rate()
        target_x = int(rect[0] + x * x_rate)
        target_y = int(rect[1] + y * y_rate)
        logger.info("%d, %d" % (target_x, target_y))
        return target_x, target_y

    def exists(self, timeout=3):
        try:
            self.find_json_element(timeout=timeout)
        except:
            return False
        return True

    def scroll_to_screen(self, max_scroll_num=10):
        for i in range(max_scroll_num):
            if self.is_in_screen():
                return True
            time.sleep(1)
        raise RuntimeError(u"scroll over %d", max_scroll_num)

    def is_in_screen(self):
        """
        元素是否在屏幕内部，但是不一定可见
        """
        if not self.exists():
            return False
        json_ret = self.find_json_element(True)
        return json_ret['in_screen']

    def is_visible(self):
        '''
        元素是否在屏幕上可见
        :return:
        '''
        if not self.exists():
            return False
        json_ret = self.find_json_element(True)
        return json_ret['visible']

    def get_element(self):
        json_e = self.find_json_element()
        if json_e:
            return json_e
        else:
            raise RuntimeError(u"Not Found")

    def get_text(self):
        json_e = self.find_json_element()
        if json_e:
            return json_e.get('text')

    def enter(self, text):
        raise RuntimeError("not implementation")

    def val(self, text=None):
        """
        直接设置dom节点的value值
        :param text:
        :return:
        """
        if text:
            return self.call_js(jsapi.ELEMENT_OPERATION_SUPPLY_METHOD.SET_PROPERTY, ["value", text])
        else:
            return self.call_js(jsapi.ELEMENT_OPERATION_SUPPLY_METHOD.SET_PROPERTY, ["value"])

    def attr(self, name, value=None):
        if value:
            return self.call_js("setAttribute", [name, value])
        else:
            return self.call_js("getAttribute", [name])
