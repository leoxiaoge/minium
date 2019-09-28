#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2019-04-25
import logging
import requests
import sys
import websocket
import threading
import logging
import logging.config
import time
import json

SERVER_HOST = "ws://localhost:8000/websocket/%s"
CLOSE_TIMEOUT = 10
logger = logging.getLogger()

LOG_LEVEL = logging.DEBUG


def init_log():
    log_formatter = '%(levelname)-5.5s %(asctime)s %(filename)-18.18s %(funcName)-26.26s %(lineno)-3d %(message)s'

    log_settings = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': log_formatter
                # 'datefmt': None # 如果这里使用格式化字符串, 则logging模块内部将走无法获取毫秒的分支, 参考源码
            }
        },
        'handlers': {
            'console': {
                'level': LOG_LEVEL,
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': LOG_LEVEL,
            },
        }
    }

    logging.config.dictConfig(log_settings)


class RemoteCall(object):
    def __init__(self, ap, prop_name=None):
        self.ap = ap
        self.prop_name = prop_name

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        elif not item.startswith("_"):
            if self.prop_name is None:
                return RemoteCall(self.ap, item)
            else:
                return RemoteCall(self.ap, "%s.%s" % (self.prop_name, item))
        else:
            raise AttributeError("%s instance has no attribute '%s" % (self.__class__.__name__, item))

    def __call__(self, *args, **kwargs):
        params = {
            "args": args,
            "kwargs": kwargs
        }
        self.ap.sync_request(self.prop_name, params)


class WsProxy(object):
    def __init__(self, serial=None):
        self.serial = serial
        self._msg_lock = threading.Condition()
        self._ws_event_queue = dict()
        self.url = SERVER_HOST % serial
        self._req_id_counter = int(time.time()*1000) % 10000000000
        self._is_connected = False
        self._client = websocket.WebSocketApp(self.url, on_open=self._on_open, on_message=self._on_message, on_error=self._on_error, on_close=self._on_close)
        self._connect()

    def _connect(self, timeout=10):

        self._thread = threading.Thread(target=self._ws_run_forever, args=())
        self._thread.daemon = True
        self._thread.start()

        s = time.time()
        while time.time() - s < timeout:
            if self._is_connected:
                break
        else:
            raise RuntimeError('connect to server timeout: %s', self.url)

    def _ws_run_forever(self):
        try:
            self._client.run_forever()
        except:
            logger.exception('websocket run error')
            return
        logger.debug("%s, %s, run forerver shutdown", self.serial)

    def _on_message(self, ws, message):
        logger.debug(message)
        msg = json.loads(message)
        if msg is not None and "id" in msg:  # response
            req_id = msg["id"]
            if req_id == self._sync_wait_msg_id:
                self._sync_wait_msg_id = None
                self._sync_wait_msg = msg
                self._msg_lock.acquire()
                self._msg_lock.notify()
                self._msg_lock.release()
            else:
                logger.error('abandon msg: %s', req_id)
        else:  # event from server
            if "method" in msg and "params" in msg:
                self._push_event(msg["method"], msg["params"])

    def _push_event(self, method, params):
        if method in self._ws_event_queue:
            self._ws_event_queue[method].append(params)
        else:
            self._ws_event_queue[method] = [params, ]

    def _on_error(self, ws, error):
        pass

    def _on_close(self, ws):
        self._is_connected = False

    def _on_open(self, ws):
        """
        :type ws: websocket.WebSocketApp
        """
        self._is_connected = True

    def __del__(self):
        self._client.close()
        self._thread.join(CLOSE_TIMEOUT)

    def async_request(self, domain, params=None):
        "不阻塞异步执行, 不需要返回数据"
        req = {"method": domain, "params": params}
        req_id = self._send_request(req)
        return req_id

    def sync_request(self, domain, params=None):
        "不阻塞异步执行, 不需要返回数据"
        req = {"method": domain, "params": params}
        req_id = self._send_request(req)
        return req_id

    def _send_request(self, params):
        if "id" in params:
            req_id = params["id"]
        else:
            params["id"] = req_id = self._get_req_id()
        serialize = json.dumps(params)
        # logger.debug('send: %s', serialize)
        self._client.send(serialize)
        return req_id

    def _get_req_id(self):
        self._req_id_counter += 1
        return self._req_id_counter

    def _remote_call(self, prop, *args, **kwargs):
        pass


class AtProxy(RemoteCall):
    def __init__(self, serial=''):
        self.ws = WsProxy(serial)
        super(AtProxy, self).__init__(self.ws)


if __name__ == '__main__':
    init_log()
    for i in range(1):
        print(i)
        a = AtProxy()
        print(a.page("getElement", {"fuck": "zengxia"}))
        print(a.page.xxxxx.xxx("getElement", {"fuck": "zengxia"}))

