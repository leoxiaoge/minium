#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2018/5/8
import logging

logger = logging.getLogger()

ELEMENT_OPERATION = "elementOperation"
SCROLL_TO = "scrollTo"
DUMP_DOM_TO_JSON = "dumpDomJson"


class JsApiError(RuntimeError):
    pass


class CallJsFailed(JsApiError):
    pass


class ElementNotExists(JsApiError):
    pass


class CallJsError(JsApiError):
    pass


class JsResponse(object):
    class ErrorCode:
        success = 0
        unknown = -1
        failed = 1
        error = 2
        notExists = 3

    def __init__(self, json_dict):
        self.ret = json_dict["ret"]
        self.msg = json_dict["msg"]
        self.data = json_dict["data"]

    def is_ok(self):
        return self.ret == JsResponse.ErrorCode.success

    def raise_error(self):
        if not self.is_ok():
            logger.error(self.data)
            if self.ret == JsResponse.ErrorCode.notExists:
                raise ElementNotExists(self.msg)
            elif self.ret == JsResponse.ErrorCode.failed:
                raise CallJsFailed(self.msg)
            elif self.ret == JsResponse.ErrorCode.error:
                raise CallJsError(self.msg)
            else:
                raise CallJsFailed(self.msg)


class ELEMENT_OPERATION_SUPPLY_METHOD:
    SET_PROPERTY = "_setProperty"
    GET_PROPERTY = "_getProperty"
