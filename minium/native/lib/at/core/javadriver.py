# -*- coding: utf-8 -*-
"""
@author: 'xiazeng'
@created: 2016/12/12
"""

import datetime
import json
import re
import logging
import socket
import subprocess
import threading
import time
import sys

from at.utils import magic
from . import uixml, config, resguard, basedriver

if sys.version_info[0] < 3:
    from Queue import Queue, Empty
    from urllib import unquote
else:
    from queue import Queue, Empty
    from urllib.parse import unquote


RESPONSE_ERROR_JSON_PARSE_ERROR = 6
RESPONSE_ERROR_UI_OBJECT_NOT_FOUND = 5
RESPONSE_ERROR_NO_SUCH_METHOD = 3
RESPONSE_ERROR_PARAMS_UNVALIDED = 4
UNKNOW_ERROR = 7

logger = logging.getLogger()


def pick_unuse_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


class JavaDriver(basedriver.JavaBaseDriver):
    ACTION_QUIT = "quit"
    ACTION_GET_TIMESTAMP = "timestamp"
    ACTION_PING = "ping"
    ACTION_HAS_READY = "hasReady"
    ACTION_BASEUI = "baseUi"
    ACTION_UI_DEVICE = "uiDevice"
    ACTION_UI_CFG = "uiCfg"
    ACTION_PY_CFG = "pyCfg"
    ACTION_HTTP_GET = "httpGet"
    ACTION_UI_SELECTOR = "pySelector"
    ACTION_LOGCAT = "logcat"
    ACTION_UPLOAD = "upload"
    ACTION_CONTEXT_UTIL = "contextUtil"
    ACTION_SYS_HANDLER = "sysDialogHandler"
    ACTION_DIALOG_HANDLER = "appDialogHandler"
    ACTION_AT_DEVICE = "aTDevice"
    ACTION_SCREEN_CAPTURE = "ScreenCapture"

    UPLOAD_DIR = "/data/local/tmp"
    SERVER_PORT = 9999

    java_drivers = {}

    def __init__(self, serial, uiautomator=config.UIAUTOMATOR):
        super(JavaDriver, self).__init__(serial)
        self._server_thread = None
        self.app_outputs = []
        self.device_operation_records = []
        self.ui_trace_list = []
        self._capture_op = True
        self._server_cmd = ""
        self.uiautomator_version = uiautomator

        self._init()

    def release_variable(self):
        self.device_operation_records = []
        self.ui_trace_list = []

    def reconnect(self):
        self.close_remote()
        time.sleep(1)
        self._init()

    def _init(self):
        cmd = "uiautomator runtest %s -c %s#%s " % (config.JAR_STUB_FILENAME,
                                                    config.JAR_STUB_CLASS,
                                                    config.STUB_CASE_NAME)
        if self.uiautomator_version == config.UIAUTOMATOR2:
            install_ret = self._init_uiautomator2()
            if install_ret:
                cmd = "am instrument -w -r  -e class '%s#%s' %s/android.support.test.runner.AndroidJUnitRunner" % (
                    config.TEST_APP_CLS, config.STUB_CASE_NAME, config.TEST_APP_PKG
                )
            else:
                logger.error("init uiautomator2 failed, try uiautomator1")
                self.uiautomator_version = config.UIAUTOMATOR
        if self.uiautomator_version == config.UIAUTOMATOR:
            self.adb.push(config.JAR_STUB_PATH, JavaDriver.UPLOAD_DIR)

        cmd = self.adb.prefix() + " shell " + cmd
        self._server_cmd = cmd
        self.adb.forward(self._port, JavaDriver.SERVER_PORT)
        try:
            self.set_app_server_run(False)
            self.run_remote_server()
            self.wait_for_ui_ready(120)
        except RuntimeError:
            logger.exception("remote run failed")
            self.set_app_server_run(False)

    def _init_uiautomator2(self):
        ret = True
        # self.adb.uninstall(config.TEST_APP_PKG)
        if not self.adb.pkg_has_installed(config.TEST_APP_PKG):
            ret = self.adb.install(config.TEST_APK_PATH, opt="-t -r")
            if not ret:
                return False
        # self.adb.uninstall(config.TEST_STUB_APP_PKG)
        if not self.adb.pkg_has_installed(config.TEST_STUB_APP_PKG):
            ret = self.adb.install(config.STUB_APK_PATH, opt="-t -r")
            if not ret:
                return False
        return ret

    def _init_uiautomator(self):
        ret = False
        if not self.adb.pkg_has_installed(config.TEST_APP_PKG):
            ret = self.adb.install(config.TEST_APK_PATH)
            if not ret:
                return False
        if not self.adb.pkg_has_installed(config.TEST_STUB_APP_PKG):
            ret = self.adb.install(config.STUB_APK_PATH)
        return ret

    @classmethod
    def apply_driver(cls, serial, version=config.UIAUTOMATOR):
        assert serial is not None
        if serial in cls.java_drivers:
            # logger.info("use cache JavaDriver, %s, %d" , str(serial), id(cls.java_drivers[serial]))
            return cls.java_drivers[serial]
        else:
            jd = JavaDriver(serial, version)
            # logger.info("create JavaDriver, %s, %d", str(serial), id(jd))
            cls.java_drivers[serial] = jd
            return jd

    @classmethod
    def release_driver(cls, serial):
        logger.info(serial)
        if serial in cls.java_drivers:
            jd = cls.java_drivers[serial]
            del cls.java_drivers[serial]
            jd.close()

    def run_remote_server(self, max_wait_timeout=15):
        if self._server_thread is None:
            s = time.time()
            try_count = 0
            while time.time() - s < max_wait_timeout:
                if not self.adb.app_is_running("uiautomator"):
                    break
                pid = self.adb.get_android_pid("uiautomator")
                self.adb.run_shell("kill %s" % pid)
                time.sleep(2)
                try_count += 1
                logger.error("uiautomator is running, try %d" % try_count)
            else:
                self._last_error = u"UiAutomator已经被占用"
                raise RuntimeError(u"UiAutomator已经被占用")
            t = threading.Thread(target=self._run_app_server, args=(self._server_cmd,))
            t.setDaemon(True)
            t.start()
        else:
            logger.error("last thread has not stop")

    def wait_for_ui_ready(self, timeout=30):
        s = time.time()
        logger.debug("wait_for_ui_ready start")
        t = time.time() - s
        while t < 5 and not self.is_remote_running(): # todo: 偶现adb命令阻塞卡住
            time.sleep(1)
            t = time.time() - s
            logger.debug("wait, %.2f " % t)
        if not self.is_remote_running():
            raise RuntimeError(u"launch uiautomator timeout: %dms" % ((time.time() - s)*1000))
        if time.time() - s > timeout:
            raise RuntimeError(u"手机服务未开启，可能AccessibilityServiceClient被占用，可以尝试插拔手机")
        while t < timeout:
            if self.ping():
                break
            time.sleep(1)
            t = time.time() - s
            logger.debug("ping, %.2f " % t)
        if t >= timeout:
            raise RuntimeError(u"等待超时，可能AccessibilityServiceClient被占用，或者手机巨卡")
        while t < timeout:
            if self.ui_is_ready():
                break
            time.sleep(1)
            t = time.time() - s
            logger.debug("remote_has_ready, %.2f " % t)

        logger.debug("wait_for_ui_ready stopped")

    def _run_app_server(self, cmd):
        logger.info(cmd)

        if magic.is_windows():
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True)
        else:
            args = re.split(r"\s+", cmd)
            process = subprocess.Popen(args, close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=False)
        q = Queue()
        t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
        t.daemon = True  # thread dies with the program
        t.start()
        t = threading.Thread(target=enqueue_output, args=(process.stderr, q))
        t.daemon = True  # thread dies with the program
        t.start()
        while not process.poll():
            line = None
            try:
                line = q.get_nowait()
                if magic.is_windows():
                    line = line.decode("gbk")
                else:
                    line = line.decode("utf-8")
            except Empty:
                time.sleep(0.5)
            if line is not None and len(line.strip()) > 0 and "CDS" not in line:
                if "test=%s" % config.STUB_CASE_NAME in line:
                    # 检查到用例真正运行才算启动成功
                    self._cmd_process = process
                    self.set_app_server_run(True)
                self.app_outputs.append(line)
                if "close [socket]" not in line:
                    logger.debug("java print:" + line.strip())
        self.set_app_server_run(False)
        logger.info("subprocess stopped, ret code:" + str(process.returncode))
        self._server_thread = None

    def ping(self):
        try:
            ret = self.do_request(self.ACTION_PING)
            if ret:
                return True
            else:
                return False
        except Exception:
            logger.exception("ping failed")
            return False

    def ui_is_ready(self):
        return self.do_request(self.ACTION_HAS_READY, None)

    def dump_ui(self):
        """
        获取顶层窗口的views, 获取的views是按照从上到下顺序，重试5次
        todo: 重构时要放到uidevice里面去
        """
        views = []  # type: list[uixml.UiView]
        i = 0
        for i in range(5):
            res = self.request_at_device("dumpUi", [])
            if res and len(res.strip()) != 0:
                views = uixml.window_dump_parse_str(res, resguard.Resguard.get_resguard(self.serial))
                for view in views:
                    if view.size != 0:
                        return views
            time.sleep(i+0.5)
        logger.debug('views len: %s, try:%s', len(views), i+1)
        return views

    def dump_all_views(self):
        """
        获取所有窗口的views, 获取的views是按照从上到下顺序，重试5次
        todo: 重构时要放到uidevice里面去
        """
        views_list = []  # type: list[list[uixml.UiView]]
        i = 0
        for i in range(5):
            res = self.request_at_device("dumpXmls", [])
            if res and len(res) != 0:
                for views_str in res:
                    views = uixml.window_dump_parse_str(views_str, resguard.Resguard.get_resguard(self.serial))
                    views_list.append(views)
                break
            time.sleep(i+0.5)
        logger.debug('window len: %s, try:%s', len(views_list), i+1)
        return views_list

    def dump_activity_proxy(self):
        for i in range(5):
            res = self.request_at_device("dumpUi", [])
            if res and len(res.strip()) != 0:
                return uixml.window_dump_2_activity_proxy(res, resguard.Resguard.get_resguard(self.serial))
            time.sleep(i+1)
        return None

    def network_is_ok(self, url="www.qq.com"):
        return self.request_java(self.ACTION_HTTP_GET, [url])

    def has_view(self, selector):
        for v in self.dump_ui():
            if v.match(selector):
                return True
        return False

    def request_action(self, action, method, params):
        action = action + "/" + method
        return self.request_java(action, params)

    def request_ui_method(self, method, params):
        """
        send cmd to mobile, ask for a uiautormator action
        """
        action = self.ACTION_BASEUI + "/" + method
        return self.request_java(action, params)

    def request_at_device(self, method, params=None):
        if params is None:
            params = []
        return self.request_action(self.ACTION_AT_DEVICE, method, params)

    def request_screen_capture(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_SCREEN_CAPTURE + "/" + method
        return self.request_java(action, params)

    def request_ui_device(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_UI_DEVICE + "/" + method
        return self.request_java(action, params)

    def request_ui_configure(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_UI_CFG + "/" + method
        return self.request_java(action, params)

    def request_logcat(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_LOGCAT + "/" + method
        return self.request_java(action, params)

    def request_context(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_CONTEXT_UTIL + "/" + method
        return self.request_java(action, params)

    def request_sys_handler(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_SYS_HANDLER + "/" + method
        return self.request_java(action, params, timeout=90)

    def request_dialog_handler(self, method, params=None):
        if params is None:
            params = []
        action = self.ACTION_DIALOG_HANDLER + "/" + method
        return self.request_java(action, params)

    def request_ui_selector(self, selectors, method, params=None, child_selectors=None, parent_selector=None):
        if params is None:
            params = []
        # logger.info(method)
        action = self.ACTION_UI_SELECTOR + "/" + method
        http_params = dict()
        http_params["params"] = unquote(json.dumps(params))
        http_params["UiSelector"] = unquote(json.dumps(selectors))
        # logger.info(http_params)
        return self.do_request(action, http_params)

    def request_java(self, action, params, **kwargs):
        http_params = dict()
        logger.debug("%s params %s", action, json.dumps(params, ensure_ascii=False))
        http_params["params"] = unquote(json.dumps(params))
        return self.do_request(action, http_params, **kwargs)

    def close_remote(self):
        if not self.is_remote_running():
            return
        try:
            ret = self.do_request(self.ACTION_QUIT)
            logger.info("close_remote:"+str(ret))
        except:
            logger.exception("close failed")
        finally:
            logger.info("run finally")
            if self._port:
                self.adb.forward_remove(self._port)
            self.set_app_server_run(False)

    def get_unix_ts(self):
        return self.do_request(self.ACTION_GET_TIMESTAMP)

    def set_capture_op(self, true_or_false):
        self._capture_op = true_or_false

    def push_op(self, msg, *args):
        if not self._capture_op:
            return
        plus_micro_seconds = time.time() - self._start_ts
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = msg % args
        act_name = self.adb.get_current_activity()
        # ui_views = self.dump_ui()
        # last_ui_views = self.ui_trace_list[-1] if self.ui_trace_list else None
        # self.ui_trace_list.append(ui_views)
        # same_rate = uixml.ui_views_same_rate(ui_views, last_ui_views)
        # self.trigger("frame_changed", same_rate, last_ui_views, ui_views, act_name)
        if u"检查" not in msg:
            self.trigger("event_capture", act_name)
        self.device_operation_records.append(u"%s%10.2fs %s" % (dt, plus_micro_seconds, msg))
