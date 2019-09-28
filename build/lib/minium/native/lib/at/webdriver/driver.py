#!/usr/bin/env python
# encoding:utf-8
# created by xiazeng

import socket
import re
import json
import time
import os
import os.path
import glob
import sys

import requests
import logging

from . import jsapi
from ..core import adbwrap
from .. import At
from ..utils import decorator
from .error import *
from .webelement import WebElement
from .wspools import WsPools
from .tabdescription import TabDescription
from .tabwebsocket import TabWebSocket

if sys.version_info[0] < 3:
    basestring = (str, unicode)
logger = logging.getLogger()

LOCAL_DEBUG = False
WEBVIEW_CLASS_NAMES = [
    "com.tencent.smtt.webkit.WebView",
    "com.tencent.tbs.core.webkit.WebView",
    "android.webkit.WebView"
]

WEBVIEW_RIDS = [
    "com.tencent.mm:id/logo_wv_container"
]

local_port_wrap = r".*(webview_devtools_remote_%s.*)$"
page_mapping = {}
cache_port = {}
cache_inject = {}


class HarParseException(H5BaseException):
    pass


class H5DomNotFound(H5BaseException):
    pass


class X5NotDebug(H5BaseException):
    pass


class RunJSError(H5BaseException):
    pass


def pick_unuse_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def python_args_to_js(args):
    params = []
    for arg in args:
        if isinstance(arg, bool):
            params.append('true' if arg else 'false')
        elif isinstance(arg, basestring):
            params.append("'%s'" % arg)
        elif arg is None:
            params.append("null")
        else:
            params.append(str(arg))
    return params


def get_web_view_rect(ui_views):
    view = get_webkit_view(ui_views)
    if view:
        return view.x1, view.y1, view.x2, view.y2
    return None


def get_webkit_view(ui_views):
    maybe_view = None
    for view in ui_views:
        if view.cls_name in WEBVIEW_CLASS_NAMES or view.rid in WEBVIEW_RIDS:
            if not maybe_view:
                maybe_view = view
            else:
                if maybe_view.height < view.height:
                    maybe_view = view
    return maybe_view


class Window(object):
    _script_g_window_varable = "_g_stub_window"

    def __init__(self, ws_sock):
        self.sock = ws_sock

    def is_show(self):
        return self.run_method("isActive")

    def set_show(self, is_show="true"):
        return self.run_method("setActive", is_show)

    def get_field(self, name):
        name = name.strip()
        return self.sock.run_script_with_output(Window._script_g_window_varable+"."+name)

    def run_method(self, name, *args, **kwargs):
        name = name.strip()
        params = []
        for arg in args:
            params.append(str(arg))
        for k,v in kwargs.items():
            params.append("%s=%s" % (k, v))
        params_str = ", ".join(params)
        return self.sock.run_script_with_output(Window._script_g_window_varable + "." + name+"(" + params_str + ")")


class WebPage(object):
    "对TabWebSocket的封装"
    def __init__(self, ws_sock, serial=None, inject=True):
        self.serial = serial
        self._sock = ws_sock    # type: TabWebSocket
        self.ws_url = self.sock.url
        self.at = At(serial)
        self.desc = self.sock.desc
        self.click_by_ui = True
        self.has_inject = False
        if inject:
            self.inject_stub()

    def close(self, timeout=4):
        self.sock.close(timeout)

    def set_click_by_ui(self, true_or_false):
        self.click_by_ui = true_or_false

    @classmethod
    def from_sock_name(cls, serial, name):
        pass    # cls.p_forward(serial, name)

    @property
    def sock(self):
        if self._sock:
            return self._sock
        else:
            raise RuntimeError("sock has not connected")

    def wait_for_ready(self, timeout=30, sleep=10):
        t = time.time()
        logger.debug("wait for H5 ready ...")
        while time.time() - t < timeout - sleep:
            try:
                result = self.sock.run_script_with_output("document.readyState", 5)
            except ResponseTimeout:
                time.sleep(1)
                continue
            if "complete" in result:
                logger.debug("H5 ready")
                return True
            time.sleep(0.5)
        logger.info("H5 wait timeout")
        return False

    @classmethod
    def get_web_page(cls, serial, app_process_name):
        adb = adbwrap.AdbWrap.apply_adb(serial)
        pid = adb.get_android_pid(app_process_name)
        socks = get_all_socks(serial, pid)
        return WebPage(socks[0], serial)

    @classmethod
    def get_all_pages(cls, serial, app_process_name):
        adb = adbwrap.AdbWrap.apply_adb(serial)
        pid = adb.get_android_pid(app_process_name)
        return cls.get_all_pages_by_pid(serial, pid)

    @classmethod
    def get_all_pages_by_pid(cls, serial, pid):
        pages = []
        for sock in get_all_socks(serial, pid):
            pages.append(WebPage(sock, serial))
        return pages

    def should_inject(self):
        if self.desc.empty:
            return False
        return True

    def inject_stub(self, force=False):
        if self.has_inject:
            return
        if not force and not self.should_inject():
            return
        if not force and self.sock.url in cache_inject:
            return False
        for filename in glob.glob(os.path.join(os.path.dirname(__file__), "*js")):
            logger.info("inject %s", filename)
            script = open(filename).read()
            self.execute_script(script)
            self.has_inject = True
        cache_inject[self.sock.url] = True

    def execute_script(self, script):
        return self.sock.run_script_with_output(script)

    def _invoke_js(self, func_name, *args):
        params = []
        for arg in args:
            if isinstance(arg, bool):
                params.append('true' if arg else 'false')
            elif isinstance(arg, basestring):
                params.append("'%s'" % arg)
            else:
                params.append(str(arg))
        params.insert(0, "'%s'" % func_name)
        script = "{method}({args})".format(method="hook", args=', '.join(params))
        logger.info(script)
        result = self.sock.run_script_with_output(script)
        return result

    def _set_config(self, name, value):
        return self._invoke_js("setConfig", name, value)

    def cfg_auto_scroll(self, true_or_false):
        self._set_config("autoScroll", true_or_false)

    def scroll_one_screen(self):
        """
        向下滑动一个屏幕
        """
        self._invoke_js("scrollDown")

    def invoke_js(self, method, *args):
        params = python_args_to_js((method, ) + args)
        script = "jsstub.apiCalled(%s);" % (', '.join(params))
        logger.debug(script)
        r = self.sock.run_script_with_output(script)
        js_res = jsapi.JsResponse(json.loads(r))
        js_res.raise_error()
        return js_res.data

    @decorator.cached_property
    def width(self):
        return self.sock.run_script_with_output("window.innerWidth")

    @decorator.cached_property
    def height(self):
        return self.sock.run_script_with_output("window.innerHeight")

    @decorator.cached_property
    def web_view_bounds(self):
        views = self.at.java_driver.dump_ui()
        return get_web_view_rect(views)
        # return self.at.e.cls_name(MM_X5_CLASS_NAME).get_bounds()

    def by_id(self, cls_id):
        return WebElement(self, css="#%s" % cls_id, web_view_bounds=self.web_view_bounds)

    def by_css_selector(self, css):
        return WebElement(self, css=css, web_view_bounds=self.web_view_bounds)

    def by_cls_name(self, cls_name):
        names = re.split(r"\s+", cls_name)
        return WebElement(self, css="".join([".%s" % n for n in names]), web_view_bounds=self.web_view_bounds)

    def by_tag_name(self, tag_name):
        return WebElement(self, css=tag_name, web_view_bounds=self.web_view_bounds)

    def by_text_contains(self, text):
        return WebElement(self, css=':contains("%s")' % text, web_view_bounds=self.web_view_bounds)

    def by_text(self, text):
        return WebElement(self, css=':text("%s")' % text, web_view_bounds=self.web_view_bounds)

    def dump_dom_list(self, css_selector):
        return self.invoke_js(jsapi.DUMP_DOM_TO_JSON, css_selector)


def get_all_abstract_ports(serial, *reg_str_list):
    adb = adbwrap.AdbWrap.apply_adb(serial)
    output = adb.run_shell("cat /proc/net/unix")
    lines = output.replace("\r\n", "\n").split("\n")
    target_ports = []
    for line in lines:
        if "devtools" in line:
            logger.info(line)
        for reg_str in reg_str_list:
            m = re.search(reg_str, line)
            if m is not None:
                target_ports.append(m.group())
    logger.debug(target_ports)
    return target_ports


def abstract_port_exists(serial, port_name):
    adb = adbwrap.AdbWrap.apply_adb(serial)
    output = adb.run_shell("cat /proc/net/unix")
    lines = output.replace("\r\n", "\n").split("\n")
    for line in lines:
        if port_name in line:
            return True
    return False


def local_port(pid):
    return local_port_wrap % pid


def port_forward(serial, pid):
    cache_key = port_key(serial, pid)
    if cache_key in cache_port:
        cache_value = cache_port[cache_key]
        return cache_value.get("sock_name", None), cache_value.get("port", None)
    adb = adbwrap.AdbWrap.apply_adb(serial)
    output = adb.run_shell("cat /proc/net/unix")
    lines = output.replace("\r\n", "\n").split("\n")
    local_sock_name = local_port(pid)
    for line in lines:
        m = re.match(local_sock_name, line)
        if m is not None:
            logger.info("open_x5_debug,%s", line)
            name = m.group(1)
            port = pick_unuse_port()
            cmd = "forward tcp:%d localabstract:%s" % (port, name)
            cache_port[cache_key] = {"sock_name": local_sock_name, "port": port}
            adb.run_adb(cmd)
            return local_sock_name, port
    else:
        raise X5NotDebug("x5 inspect didn't open, tbs is on? is tbs?")


def port_key(serial, port):
    return "%s#%s" % (str(serial), str(port))


def get_all_socks(serial, pid):
    socks = []
    for tab in get_all_tabs(serial, pid):
        sock = get_sock(tab)
        if sock:
            socks.append(sock)
    return socks


def get_all_tabs(serial, pid):
    local_sock_name, port = port_forward(serial, pid)
    return tabs(port)


"""
chromium对应的源代码：https://cs.chromium.org/chromium/src/content/browser/devtools/devtools_http_handler.cc
只用到json命令的version和list
"""


def tabs(port):
    "TODO: 建议重构为retry_get_tabs"
    url = 'http://127.0.0.1:%s/json/list' % str(port)
    err = None
    for i in range(3):
        try:
            text = requests.get(url, timeout=5).text # 在有的机型上没有「/list」后缀也行
            break
        except requests.ConnectionError as e:
            time.sleep((i + 1) * 2)
            err = e
    else:
        raise err
    total_tabs = json.loads(text)
    logger.debug("find %d chrome tabs", len(total_tabs))
    # logger.debug("message: %s", total_tabs)
    return total_tabs


def get_tabs(port, timeout=5):
    "这个api没有retry逻辑"
    url = 'http://127.0.0.1:%s/json/list' % str(port)
    text = requests.get(url, timeout=timeout).text # 在有的机型上没有「/list」后缀也行
    total_tabs = json.loads(text)
    logger.debug("find %d chrome tabs: %s", len(total_tabs), total_tabs)
    return total_tabs


def get_ws_url(tab):
    return tab.get("webSocketDebuggerUrl", None)


# TODO 有点问题, WsPools的接口改过
def get_sock(tab):
    tab_id = tab["id"]
    if WsPools.has_id(tab_id):
        return WsPools.get_by_id(tab_id)
    elif "webSocketDebuggerUrl" in tab:
        ws_url = tab["webSocketDebuggerUrl"]
        if WsPools.has(ws_url):
            return WsPools.get(ws_url)
        else:
            desc = TabDescription(tab["description"])
            s = TabWebSocket(ws_url, desc, tab_id, tab["title"])
            return s
    else:
        logger.warning("invalided tab (maybe socket has used) " + json.dumps(tab))
        return None


def get_sock_by_socket_name(serial, socket_name, index=-1):
    port = p_forward(serial, socket_name)
    tbs = tabs(port)
    if len(tbs) <= index:
        return None
    tab = tbs[index]
    sock = get_sock(tab)
    return sock


def p_forward(serial, socket_name):
    if socket_name in cache_port:
        return cache_port[socket_name]["port"]
    port = pick_unuse_port()
    cmd = "forward tcp:%d localabstract:%s" % (port, socket_name)
    cache_port[socket_name] = {"sock_name": socket_name, "port": port, "serial": serial}
    adb = adbwrap.AdbWrap.apply_adb(serial)
    adb.run_adb(cmd)
    return port


def release_all_port():
    global cache_port
    for name, name_map in cache_port.items():
        # logger.info(name_map)
        if "serial" in name_map:
            adb = adbwrap.AdbWrap.apply_adb(name_map["serial"])
            adb.forward_remove(name_map["port"])
    cache_port = {}


def get_mm_sock(serial, pid):
    local_sock_name, port = port_forward(serial, pid)
    tbs = tabs(port)
    target_tab = None
    for tb in tbs:
        try:
            desc = json.loads(tb["description"])
            if desc["visible"] and not desc["empty"]:
                target_tab = tb
                break
        except:
            logger.info("drop %s", tb["description"])
            pass
    sock = get_sock(target_tab)
    return sock


def get_local_sock(serial, local_sock_name):
    port = pick_unuse_port()
    adb = adbwrap.AdbWrap.apply_adb(serial)
    adb.run_adb("forward tcp:%s localabstract:%s" % (port, local_sock_name))
    tbs = tabs(port)
    target_tab = None
    for tb in tbs:
        if "title" in tb and "about:blank" in tb['title']:
            continue
        try:
            desc = json.loads(tb["description"])
            if desc["visible"] and not desc["empty"]:
                target_tab = tb
                break
        except:
            target_tab = tb
            break
    sock = get_sock(target_tab)
    return sock


def test():
    serial = "2fc7e615" #"60661548"
    at = At(serial)
    adb = adbwrap.AdbWrap.apply_adb(serial)
    pid = adb.get_android_pid("com.tencent.mm:tools")
    web_sock = get_local_sock(serial, "xweb_devtools_remote_%d" % pid)
    # web_sock = get_local_sock(serial, "com.tencent.mm_devtools_remote%d" % pid)
    # web_sock = get_local_sock(serial, "com.tencent.mm_devtools_remote27174")
    page = WebPage(web_sock, adb.serial)
    # print page.sock.run_script_with_output("navigator.userAgent")
    page.by_css_selector("textarea").val("{'aa': 1}")
    page.close()
    at.release()
if "__main__" == __name__:
    test()
