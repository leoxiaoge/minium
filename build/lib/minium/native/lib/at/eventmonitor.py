# -*- coding: utf-8 -*-
"""
@author: 'xiazeng'
@created: 2017/5/3 
"""
import urllib
import json
from .core import javadriver
from .core import element


class EventMonitor(object):
    def __init__(self, jd):
        self.jd = jd       # type: javadriver.JavaDriver

    def add_selector_filter(self, name, match_element, action_element):
        """
        :type match_element: element.Element
        :type action_element: element.Element
        """
        params = {
            "MatchSelector": urllib.unquote(json.dumps(match_element._selector)),
            "ActionSelector": urllib.unquote(json.dumps(action_element._selector)),
            "name": name
        }
        self.jd.do_request("AddEventMonitor", params)

    def sync_event(self):
        self.jd.do_request("syncEventMonitor", {})

    def clear(self):
        self.jd.do_request("clearEventMonitor", {})

    def action_when_screen(self, true_or_false):
        self.jd.do_request("setEventMonitorShouldScreen", {"should": true_or_false})

    def get_all_screen(self):
        return self.jd.do_request("getMonitorScreen", {})

    def clear_all_screen(self):
        return self.jd.do_request("clearMonitorScreen", {})

    def remove_selector_filter(self, name):
        params = {
            "name": name
        }
        self.jd.do_request("removeEventMonitor", params)

