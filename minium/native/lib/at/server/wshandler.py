#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2019-04-25
import logging
import json
import at
import tornado.websocket
import traceback

logger = logging.getLogger()


class WsErrorCode(object):
    SUCCESS = 0
    ERROR_UNKNOWN = -100000
    ERROR_AT_INIT = -100001
    ERROR_METHOD_NOT_IMPLEMENTATION = -200001

    @classmethod
    def msg(cls, ret):
        return {
            cls.SUCCESS: "success",
            cls.ERROR_AT_INIT: "at init failed",
            cls.ERROR_METHOD_NOT_IMPLEMENTATION: "method not implementation",
            cls.ERROR_UNKNOWN: "not define error"
        }.get(ret, "unknown error")


class WsReq(object):
    def __init__(self, message):
        cmd = json.loads(message)
        self.args = cmd["params"]["args"]
        self.kwargs = cmd["params"]["kwargs"]
        self.method = cmd["method"]
        self.id = cmd["id"]

    def to_res_dict(self, result, ret=WsErrorCode.SUCCESS):
        return {
            'id': self.id,
            'result': result,
            'error': WsErrorCode.msg(ret),
            'error_code': ret
        }


class WsHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.at = None
        self.serial = None

    def is_connection(self):
        return self.ws_connection is not None

    def send_event(self, method, params):
        self.write_message({"method": method, "params": params})

    def on_message(self, message):
        req = WsReq(message)
        logger.debug(message)
        try:
            method_imp = getattr(self.at, req.method, None)
            if method_imp is None:
                self.write_message(req.to_res_dict("%s not exists" % req.method,
                                                   WsErrorCode.ERROR_METHOD_NOT_IMPLEMENTATION))
                return
            result = method_imp(*req.args, **req.kwargs)
            self.write_message(req.to_res_dict(result))
        except tornado.websocket.WebSocketClosedError:
            logger.warning("connection has closed")
        except:
            self.write_message(req.to_res_dict(traceback.format_exc(), WsErrorCode.ERROR_UNKNOWN))


    def on_close(self):
        logger.warning("on_close")

    def on_ping(self, data):
        logger.warning("on_ping")

    def open(self, serial=None):
        self.serial = serial
        logger.warning("opened serial:%s", serial)
        try:
            self.at = at.At(serial)
        except:
            self.send_event("error", traceback.format_exc())
            self.close()
