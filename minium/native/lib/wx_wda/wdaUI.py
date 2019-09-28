#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import time
import wda
import logging

wda.DEBUG = True  # default False
wda.HTTP_TIMEOUT = 60.0  # default 60.0 seconds

logger = logging.getLogger()
WORKSPACE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, WORKSPACE_DIR)


class UiAutomatorException(Exception):
    def __init__(self, message=None, reason=None):
        self._message = message
        self._reason = reason

    def print_message(self):
        logger.debug(self._message)

    def print_reason(self):
        logger.debug(self._reason)

    @property
    def message(self):
        if not self._message:
            self._message = "No Message"
        return self.__name__, "message:", self._message

    @property
    def reason(self):
        if not self._reason:
            self._reason = "No Reason"
        return self.__name__, "reason:", self._reason

    @message.setter
    def message(self, value):
        self._message = value

    @reason.setter
    def reason(self, value):
        self._reason = value


class NoSuchElementError(UiAutomatorException):
    def __init__(self, message="Cannot find this elements", reason=None):
        super(NoSuchElementError, self).__init__(message, reason)
        self._message = message
        self._reason = reason


class ObjectInstanceEqualError(UiAutomatorException):
    pass


class ArgsMissingError(UiAutomatorException):
    pass


class NoSuchObjectException(UiAutomatorException):
    pass


sleep_time = 1.5


class WdaUI(object):
    def __init__(
        self,
        server_url=None,
        bundle_id=None,
        arguments=None,
        should_use_compact_responses=False,
    ):

        if server_url is None:
            server_url = "http://localhost:8100"
        logger.info("启动 %s" % bundle_id)
        self.client = wda.Client(server_url)
        logger.info(self.client.status())
        self.client.wait_ready(timeout=300)
        self.session = self.client.session(bundle_id)
        self._height = 0
        self._width = 0

    def set_alert_callback(self, callback):
        self.session.set_alert_callback(callback)

    def close(self):
        self.session.close()

    # 切后台若干秒再切回来
    def deactivate(self, duration):
        self.session.deactivate(duration)

    @property
    def width(self):
        self._width = self.session.window_size()[0]
        return self._width

    @property
    def height(self):
        self._height = self.session.window_size()[1]
        return self._height

    def device_size(self):
        size = self.session.window_size()
        return size

    def press_home(self):
        self.client.home()

    def status(self):
        return self.client.status()

    def source(self, data_format="xml"):
        return self.client.source(data_format)

    def screen_shot(self, filename):
        return self.client.screenshot(filename)

    def swipe(self, start_x, start_y, end_x, end_y, duration=0.1):
        self.session.drag(start_x, start_y, end_x, end_y, duration)

    def click_on_text(self, text, class_name=None, index=0):
        # type: (object, object, object) -> object
        self.session(text=text, class_name=class_name, index=index).tap()
        time.sleep(sleep_time)

    def click_on_partial_text(self, partial_text, class_name=None, index=0):
        self.session(
            partial_text=partial_text, class_name=class_name, index=index
        ).tap()
        time.sleep(sleep_time)

    def click_point(self, x, y):
        self.session.click(x, y)
        # self.session.tap(x, y)

    def click_on_center(self):
        center_x = self.width / 2
        center_y = self.height / 2
        self.click_point(center_x, center_y)

    def click_on_element_id(self, element_id):
        self.session.tapElement(element_id)

    def long_click_point(self, x, y, duration=3):
        self.session.long_tap(x, y, duration=duration)

    def long_click_view(self, class_name, text=None, index=0, duration=3):
        self.session(class_name=class_name, text=text, index=index).tap_hold(
            duration=duration
        )
        time.sleep(sleep_time)

    def long_click_text(self, text, duration=3, index=0):
        self.session(text=text, index=index).tap_hold(duration=duration)
        time.sleep(sleep_time)

    def double_click_point(self, x, y):
        self.session.double_tap(x, y)

    def double_click_view(self, class_name, text=None, index=0, duration=3):
        self.session(class_name=class_name, text=text, index=index).double_tap(duration)
        time.sleep(sleep_time)

    def force_touch_view(
        self,
        class_name=None,
        text=None,
        partial_text=None,
        index=0,
        pressure=1.0,
        duration=1.0,
    ):
        self.session(
            class_name=class_name, text=text, partial_text=partial_text, index=index
        ).force_touch(pressure, duration)
        time.sleep(sleep_time)

    def force_touch_point(self, x, y, pressure=1.0, duration=1.0):
        self.session(class_name="Window").force_touch_point(x, y, pressure, duration)
        time.sleep(sleep_time)

    def screenshot_view(
        self, filename, class_name=None, text=None, partial_text=None, index=0
    ):
        self.session(
            class_name=class_name, text=text, partial_text=partial_text, index=index
        ).screenshot(filename)
        time.sleep(sleep_time)

    def scroll_height(self, direction="up", delt_height=0.5, duration=0.1):
        center_x = self.width / 2
        center_y = self.height / 2
        height = delt_height * self.height
        if direction == "up":
            self.swipe(
                center_x,
                center_y + height / 2,
                center_x,
                center_y - height / 2,
                duration=duration,
            )
        elif direction == "down":
            self.swipe(
                center_x,
                center_y - height / 2,
                center_x,
                center_y + height / 2,
                duration=duration,
            )
        else:
            raise Exception("error parameter, must be up or down")

    def scroll_then_click(
        self, text=None, partial_text=None, index=0, direction="visible"
    ):
        if direction == "visible":
            if not self.elem(class_name="WebView").exists:
                scrollcount = 0
                scrollmaxcount = 15
                eletext = self.session(
                    text=text, partial_text=partial_text, index=index
                )
                while not eletext.displayed and scrollcount < scrollmaxcount:
                    scrollcount += 1
                    self.scroll_height()
                time.sleep(1)
                if eletext.displayed:
                    eletext.click()
                    time.sleep(1)
                else:
                    raise RuntimeError("element not found")
            # webview用坐标判断:
            else:
                wv = self.elem(class_name="WebView").bounds
                x = wv.x + wv.width
                y = wv.y + wv.height
                scrollcount = 0
                scrollmaxcount = 15
                eletext = self.session(
                    text=text, partial_text=partial_text, index=index
                )
                while (
                    not (eletext.bounds.x < x and eletext.bounds.y < y)
                    and scrollcount < scrollmaxcount
                ):
                    scrollcount += 1
                    self.scroll_height()
                time.sleep(1)
                try:
                    self.click_point(eletext.bounds.x + 10, eletext.bounds.y + 10)
                except Exception:
                    raise RuntimeError("element not found")
                time.sleep(1)
        else:
            self.session(text=text, partial_text=partial_text, index=index).scroll(
                direction
            ).click()

    def scroll_only(self, text=None, text_contains=None, index=0, direction="visible"):
        if direction == "visible":
            if not self.elem(class_name="WebView").exists:
                scrollcount = 0
                scrollmaxcount = 15
                eletext = self.session(
                    text=text, partial_text=text_contains, index=index
                )
                while not eletext.displayed and scrollcount < scrollmaxcount:
                    scrollcount += 1
                    self.scroll_height()
            else:
                wv = self.elem(class_name="WebView").bounds
                x = wv.x + wv.width
                y = wv.y + wv.height
                scrollcount = 0
                scrollmaxcount = 15
                eletext = self.session(
                    text=text, partial_text=text_contains, index=index
                )
                while (
                    not (eletext.bounds.x < x and eletext.bounds.y < y)
                    and scrollcount < scrollmaxcount
                ):
                    scrollcount += 1
                    self.scroll_height()
        else:
            self.session(text=text, partial_text=text_contains, index=index).scroll(
                direction
            )

    def enter_text(self, text, index=0, is_clear_text=False, class_name="TextView"):
        if is_clear_text:
            self.session(class_name=class_name, index=index).clear_text()
        self.session(class_name=class_name, index=index).set_text(text)
        time.sleep(sleep_time)

    def enter_field_text(self, text, index=0, is_clear_text=False):
        if is_clear_text:
            self.session(class_name="TextField", index=index).clear_text()
        self.session(class_name="TextField", index=index).set_text(text)
        time.sleep(sleep_time)

    def enter_search_text(self, text, index=0, is_clear_text=False):
        if is_clear_text:
            self.session(class_name="SearchField", index=index).clear_text()
        self.session(class_name="SearchField", index=index).set_text(text)
        time.sleep(sleep_time)

    @property
    def orientation(self):
        orient = self.session.orientation
        return orient

    def orientation_set(self, direction):
        self.session.orientationset(direction)

    def alert_accept(self):
        self.session.alert.accept()

    def alert_dismiss(self):
        self.session.alert.dismiss()

    def alert_text(self):
        return self.session.alert.text

    def alert_buttons(self):
        return self.session.alert.buttons()

    def alert_click_button(self, button_name):
        self.session.alert.click_button(button_name)

    def keyboard_dismiss(self):
        self.session.keyboard.dismiss()

    def elem(self, **kwargs):
        return self.session(**kwargs)

    def click_on_view(self, class_name, text=None, label=None, index=0):
        self.session(class_name=class_name, text=text, label=label, index=index).tap()
        time.sleep(sleep_time)

    def click_if_exists(self, class_name=None, text=None, index=0, timeout=10):
        self.elem(class_name=class_name, text=text, index=index).click_if_exists(
            timeout=timeout
        )

    def click_on_ui_view(self, view_elem):
        if view_elem is None:
            raise NoSuchElementError()
        x = view_elem.bounds.center[0]
        y = view_elem.bounds.center[1]
        self.click_point(x, y)
        time.sleep(sleep_time)

    def click_on_righttop(self, view_elem):
        if view_elem is None:
            raise NoSuchElementError()
        x = (
            view_elem.bounds.left
            + (view_elem.bounds.right - view_elem.bounds.left) * 7 / 8
        )
        y = view_elem.bounds.top + (view_elem.bounds.bottom - view_elem.bounds.top) / 8
        self.click_point(x, y)
        time.sleep(sleep_time)

    def search_text(self, text, class_name=None):
        time.sleep(sleep_time)

        if (
            self.elem(text=text, class_name=class_name).exists
            or self.elem(partial_text=text, class_name=class_name).exists
        ):
            return True

        return False

    def press_back(self):
        btns = self.elem(class_name="NavigationBar").subelems(class_name="Button")
        if btns.count > 1:
            if btns[0].bounds.x < btns[1].bounds.x:
                btns[0].tap()
            else:
                btns[1].tap()
        else:
            btns[0].tap()
        time.sleep(1)

    # view_elem and class_name
    def parent_view(self, child_elem, parent_class_name):
        count = self.elem(class_name=parent_class_name).count
        child_class_name = child_elem.class_name
        child_text = child_elem.text
        for index in range(count):
            parent_elem = self.elem(class_name=parent_class_name, index=index)
            if parent_elem.subelems(
                class_name=child_class_name, text=child_text
            ).exists:
                return parent_elem

        raise RuntimeError("parent element not found")

    def zoom_in(self, text=None, index=0):
        self.session(class_name="Image", text=text, index=index).pinch("open")

    def zoom_out(self, text=None, index=0):
        self.session(class_name="Image", text=text, index=index).pinch("close")

    def get_index(self, class_name, text):
        elements = self.elem(class_name=class_name)
        for index in range(len(elements)):
            if elements[index].text == text:
                return index
        else:
            return -1
