#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2019-04-25
import tornado.web
import tornado.httpserver
import wshandler
import handlers
import logging
import logging.config
from tornado.options import define, options
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


def load_config():
    define("svc_ip", type=str, default="127.0.0.1", help="The IP this service listen", metavar="IP")
    define("svc_port", type=int, default=8000, help="The port this service listen", metavar="Port")
    define("max_proc_count", type=int, default=10, help="Max process count")


def get_routes():
    routes = [
        (r"/websocket/(\w*)", wshandler.WsHandler),
        (r"/device/(\w+)", handlers.DeviceHandler)
    ]

    return routes


def start_server():
    init_log()
    load_config()
    application = tornado.web.Application(get_routes())
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.bind(options.svc_port, options.svc_ip)
    http_server.start(num_processes=options.max_proc_count)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start_server()