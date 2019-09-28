# -*- coding: utf-8 -*-
"""
@author: 'xiazeng'
@created: 2016/12/2 
"""
import re
import time
import datetime


class LogRecord(object):
    reg_str = r"(?P<time>(\d{4}-)?\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+" \
              r"(?P<level>[VDIWEFS])\/" \
              r"(?P<tag>.*(?=\(\s*\d+\s*\)))\(\s*" \
              r"(?P<pid>\d+)\s*\)\s*:\s+" \
              r"(?P<msg>.*)"
    reg = re.compile(reg_str, flags=re.VERBOSE | re.MULTILINE)

    def __init__(self, line):
        self.raw_line = line
        m = LogRecord.reg.match(line)
        if m is None:
            raise RuntimeError("invalided line:"+line)
        self.time = m.group("time")
        self.level = m.group("level")
        self.tag = m.group("tag")
        self.pid = m.group("pid")
        self.msg = m.group("msg")

    @property
    def ts(self):
        t = self.time.split(".")
        if len(self.time.split("-")) != 3:
            time_str = "%s-%s" % (datetime.datetime.now().year, t[0])
        else:
            time_str = int(t[0])
        timetuple = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        ts = time.mktime(timetuple) * 1000 + int(t[1])
        return ts

    @classmethod
    def is_valid_line(cls, line):
        m = cls.reg.match(line)
        return m is not None

    def __repr__(self):
        return "%s %s %s %s" % (self.time, self.level, self.tag, self.msg)


class JLogCat(object):
    def __init__(self, jd):
        """
        :type ui: JavaDriver.JavaDriver
        """
        self.remote = jd

    def start_record(self, name, *args):
        """
        开始等待
        :param name:标识名称
        :param java_regex: java的正则表达式
        :return:
        """
        ret = True
        for java_regex in args:
            ret &= self.remote.request_logcat("startRecord", [name, java_regex])
        return ret

    def get_lines(self, name):
        lines = self.remote.request_logcat("getFilterResult", [name])
        if lines:
            return [LogRecord(line) for line in lines]
        else:
            return [] if self.remote.uiautomator_version == 1 else ["fake date"]  # ["fake data"]   # fake return

    def wait_records(self, name, count=1, timeout=10):
        s = time.time()
        while time.time() - s < timeout:
            ls = self.get_lines(name)
            if isinstance(ls, list) and len(ls) >= count:
                return ls
            time.sleep(1)
        return []

    def wait_log_count(self, count=1000, timeout=10):
        s = time.time()
        while time.time() - s < timeout:
            c = self.log_count()
            if c >= count:
                return True
            time.sleep(2)
        return False

    def stop_record(self, name):
        lines = self.remote.request_logcat("stopRecord", [name])
        if not lines:
            return [] if self.remote.uiautomator_version == 1 else ["fake data"]
        return [LogRecord(line) for line in lines]

    def log_speeds(self):
        speeds = self.remote.request_logcat("getLogSpeed")
        return speeds

    def log_is_idle(self, idle_num=300):
        speeds = self.log_speeds()
        if not speeds or len(speeds) == 0 or speeds[-1] < idle_num:
            return True
        return False

    def wait_log_idle(self, timeout=20, idle_num=200):
        s = time.time()
        while time.time() - s < timeout:
            if self.log_is_idle(idle_num):
                return True
            time.sleep(1)
        return False

    def log_count(self):
        speeds = self.remote.request_logcat("getLogCount")
        return speeds

    def stop(self):
        self.remote.request_logcat("stop")

