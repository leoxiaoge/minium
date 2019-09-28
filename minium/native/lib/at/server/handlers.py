#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2019-04-25
import tornado.web
import json


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class BaseHandler(tornado.web.RequestHandler):
    cls_recent_login_users = []

    def initialize(self):
        self.action_result = {}

    def get_header(self, _name, _default):
        return self.request.headers.get(_name, _default)

    def check_action( self ):
        if self.action.startswith( "_" ):
            self.action_result[ "msg" ] = "Illegal action %s" %self.action
            self.action_result[ "rtn" ] = 402
            return False

        if not hasattr( self, self.action ):
            self.action_result[ "msg" ] = "Action func %s doesn't exist!" %self.action
            self.action_result[ "rtn" ] = 403
            return False

        return True

    def write_response(self):
        resp_buffer = json.dumps( self.action_result)
        self.write(resp_buffer)

    def get(self, action):
        self.action = action

        if self.check_action():
            try:
                func_result = getattr( self, self.action )()
                # 不返回dict说明是web页面，不是后台api
                if not isinstance( func_result, dict ):
                    return
            except:
                raise

            self.action_result.update( func_result )

        self.write_response()

    post = get


class DeviceHandler(BaseHandler):
    def register(self):
        return {"rtk": 1, "data": "okxx"}


class ProtocolHandle(BaseHandler):
    pass

