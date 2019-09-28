#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2017/8/25
import requests
import time
import socket
import json
from . import adbwrap
import logging

logger = logging.getLogger()


def pick_unuse_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class RemoteError(RuntimeError):
    pass


class UiNotFoundError(RemoteError):
    pass


class NoSuchMethodError(RemoteError):
    pass


class ParamError(RemoteError):
    pass


class ClickPermissionError(RemoteError):
    pass


def raise_from_res(ret, msg, data):
    if ret == 0:
        return
    if "stack" in data:
        logger.error(data["stack"])
    elif "result" in data:
        logger.error(data["result"])
    else:
        logger.error(json.dumps(data, indent=3))

    if ret == 3:
        raise NoSuchMethodError(msg)
    elif ret == 5:
        raise UiNotFoundError(msg)
    elif ret == 7:
        raise ClickPermissionError(msg)
    elif ret == 4:
        raise ParamError(msg)
    else:
        raise RemoteError(msg)


class JavaBaseDriver(object):
    SERVER_PORT = 9999
    instance_cache = {}

    def __init__(self, serial):
        name = self.unique_name(serial)
        if name in JavaBaseDriver.instance_cache:
            raise RuntimeError("%s has init, you should call apply to create a object")
        self.serial = serial
        adb = adbwrap.AdbWrap.apply_adb(serial)
        self._last_error = None
        self.adb = adb
        self._port = pick_unuse_port()
        self._app_server_is_run = False
        self._cmd_process = None
        self._start_ts = time.time()
        self.req_costs = []
        self.max_init_retry = 5

        self.hook_list = []

    def reconnect(self):
        pass

    def register(self, hook):
        self.hook_list.append(hook)

    def trigger(self, event_name, *args, **kwargs):
        for hook in self.hook_list:
            if getattr(hook, event_name):
                getattr(hook, event_name)(*args, **kwargs)

    def _init(self):
        pass

    def is_remote_running(self):
        return self._app_server_is_run

    def set_app_server_run(self, true_or_false):
        logger.info(true_or_false)
        self._app_server_is_run = true_or_false

    @classmethod
    def apply(cls, serial):
        raise NotImplementedError()

    @classmethod
    def unique_name(cls, name):
        return "%s(%s)" % (cls.__name__, name)

    @classmethod
    def get_cache(cls, serial):
        name = cls.unique_name(serial)
        if name in cls.instance_cache:
            logger.info("get cache %s = %d", name, id(cls.instance_cache[name]))
            return cls.instance_cache[name]
        return None

    @classmethod
    def cache(cls, obj):
        name = obj.page_name(obj.serial)
        if name not in cls.instance_cache:
            logger.info("set cache %s = %d", name, id(obj))
            cls.instance_cache[name] = obj

    @classmethod
    def destroy(cls, serial):
        name = cls.unique_name(serial)
        logger.info(name)
        if name in cls.instance_cache:
            jd = cls.instance_cache[name]
            del cls.instance_cache[name]
            jd.close()

    @staticmethod
    def __redo_ret(res, costs):
        if res:
            if res.status_code == requests.codes.ok:
                ret = json.loads(res.text)
                if len(res.text) < 128:
                    logger.debug(res.text + ", java request costs %sms" % costs)
                else:
                    logger.debug("java request costs %sms" % costs)
                assert "ret" in ret
                assert "msg" in ret
                assert "data" in ret
                errno = ret["ret"]
                raise_from_res(errno, ret["msg"], ret["data"])
                return ret["data"]
            else:
                raise RuntimeError(u"pc与手机通讯异常，异常码：" + str(res.status_code))
        else:
            raise RuntimeError(u"返回结果为空，理论上不应该出现的！" + str(res.status_code))

    @property
    def remote_url(self):
        return "http://127.0.0.1:%d/" % self._port

    def _check_env(self):
        if not self.is_remote_running():
            if self._last_error:
                raise RuntimeError(self._last_error)
            else:
                raise RuntimeError(u"远程服务开启失败，或者提前被中断, %d", id(self))
        if not self.adb.is_connected():
            raise RuntimeError("adb has disconnected")

    def do_request(self, action, http_params=None, method="GET", timeout=60, **kwargs):
        url = self.remote_url + action
        t = time.time()
        ret = self.request(method.lower(), url, http_params, timeout=timeout, **kwargs)

        self.req_costs.append((action, t, time.time()))
        res = ret["result"] if ret is not None and "result" in ret else None
        return res

    def request(self, method, url, params=None, **kwargs):
        logger.debug("id=%s, %s, params:%s", id(self), url, params)
        self._check_env()
        retry_count = 2
        last_exception = None
        s = time.time()

        for i in range(retry_count):
            try:

                try:
                    session = requests.Session()
                    session.trust_env = False
                    res = session.request(method, url, params=params, **kwargs)
                    costs = "%d" % ((time.time() - s) * 1000,)
                    return self.__redo_ret(res, costs)
                except UiNotFoundError:
                    self.reconnect()
                    res = requests.request(method, url, params=params, **kwargs)
                    costs = "%d" % ((time.time() - s) * 1000,)
                    return self.__redo_ret(res, costs)

            except (requests.ConnectionError, requests.ReadTimeout) as e:
                check_status = self.check_forward()
                uiautomator_exists = True if self._cmd_process.poll() is None else False
                logger.warning("%d, forward:%s, %s, uiautomator exists:%s, poll:%s", i, check_status, e.message, uiautomator_exists, self._cmd_process.poll())
                last_exception = e
                if not uiautomator_exists and self.max_init_retry > 0:
                    self.max_init_retry -= 1
                    time.sleep(10)  # 资源太紧张，被系统kill掉，先等待一段时间，然后再次拉起uiautomator
                    self._init()
            time.sleep(1+retry_count*2)
        else:
            logger.error(u"网络异常，超过重试次数:%d，adb连接状态:%s" % (retry_count, self.adb.is_connected()))
            raise last_exception

    def check_forward(self):
        if not self.adb.is_connected():
            return False
        is_forward = False
        if str(self._port) in self.adb.run_adb("forward --list"):
            is_forward = True
        else:
            self.adb.forward(self._port, self.SERVER_PORT)
            time.sleep(1)
            if str(self._port) in self.adb.run_adb("forward --list"):
                logger.info("re forward success")
                is_forward = True
        logger.info("forward status %s", is_forward)
        return is_forward

    def close(self, timeout=5):
        if not self.is_remote_running():
            return
        self.close_remote()
        s = time.time()
        time.sleep(1)
        if not self._cmd_process:
            return
        while time.time() - s < timeout:
            if not self._cmd_process.poll() or not self.is_remote_running():
                break
            time.sleep(1)
        else:
            self.adb.kill_pid(self._cmd_process.pid)

    def close_remote(self):
        pass

    def print_req_costs(self):
        a = {}
        for req, start, end in self.req_costs:
            if req not in a:
                a[req] = []
            a[req].append((end-start)*1000)
        for req, costs in a.items():
            logger.info("%s num:%s avg_costs:%dms", req, len(costs), sum(costs)/len(costs))

    def __del__(self):
        JavaBaseDriver.close_remote(self.serial)

