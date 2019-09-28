#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2018/8/23

import logging
from .utils import decorator
from .core import uixml

logger = logging.getLogger()


class AtHook(object):
    def __init__(self):
        self.frame_changed_callbacks = []
        self._has_ran = False

    def before_operation(self):
        pass

    def register_frame_changed(self, method):
        self.frame_changed_callbacks.append(method)

    @decorator.cost_log
    def frame_changed(self, rate, last_views, current_views, act_name):
        """
        界面变化
        :param rate: 相似性(0~1)
        :param last_views: 上一个界面的元素
        :param current_views: 当前界面的元素
        :param act_name: Activtiy类名
        :type last_views: list[uixml.UiView]
        :type current_views: list[UiXml.UiView]
        :return: 
        """
        if self._has_ran:
            return
        self._has_ran = True
        for cb in self.frame_changed_callbacks:
            cb(rate, last_views, current_views, act_name)
        self._has_ran = False
