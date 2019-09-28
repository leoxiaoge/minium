#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2018/11/15


class H5BaseException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __repr__(self):
        return self._msg


class OpenWebSocketException(H5BaseException): pass


class CloseWebSocketException(H5BaseException): pass


class ResponseTimeout(H5BaseException): pass


class WebSocketLoseError(H5BaseException): pass