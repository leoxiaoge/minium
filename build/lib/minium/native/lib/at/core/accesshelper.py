#!/usr/local/bin/python2.7
# encoding: utf-8
import logging
from . import javadriver


logger = logging.getLogger()


class AccessHelper(object):
    def __init__(self, jd):
        self.jd = jd    # type: javadriver.JavaDriver
        self.adb = jd.adb

    def screen_when_click_sys_dialog(self, true_or_false):
        """
        在处理系统弹框的时候截图
        :param true_or_false: 
        :return: 
        """
        return self.jd.request_sys_handler("setScreenBeforeClick", [true_or_false])

    def set_app_dialog_pkg(self, pkg_name):
        self.jd.request_dialog_handler("setPkgName", [pkg_name])

    def add_rid(self, rid):
        self.jd.request_dialog_handler("addRid", [rid])

    def set_click_sys_dialog(self, true_or_false):
        return self.jd.request_sys_handler("setPermissionMonitor", [true_or_false])

    def get_sys_dialog_click_info(self):
        return self.jd.request_sys_handler("getMonitorScreen")