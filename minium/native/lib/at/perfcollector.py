#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2017/6/13
from __future__ import print_function
import time
import threading
from at import At


class PerfCollector(threading.Thread):
    def __init__(self, at, interval=2):
        super(PerfCollector, self).__init__()
        self.at = at
        self._interval = interval
        self._should_stop = False
        self._cpu_process_names = None
        self._mem_process_names = None
        self._flow_pkg_names = None
        self._pre_shell_cmd = None
        self.data = {}

    def collect_cpu(self, *process_names):
        self._cpu_process_names = process_names

    def collect_mem(self, *process_names):
        self._mem_process_names = process_names

    def collect_flow(self, *pkg_names):
        self._flow_pkg_names = pkg_names

    def stop(self):
        self._should_stop = True
        for i in range(self._interval):
            if not self.isAlive():
                break
            time.sleep(1)

    def run(self):
        while not self._should_stop:
            if self._pre_shell_cmd:
                if isinstance(self._pre_shell_cmd, str):
                    self.at.adb.run_shell(self._pre_shell_cmd)
                else:
                    for cmd in self._pre_shell_cmd:
                        self.at.adb.run_shell(cmd)

            if self._cpu_process_names:
                ret = self.at.adb.get_cpu_rate(*self._cpu_process_names)
                ts = int(time.time())
                for k, v in ret.items():
                    if "cpu" not in self.data:
                        self.data["cpu"] = {}
                    if k not in self.data["cpu"]:
                        self.data["cpu"][k] = []
                    self.data["cpu"][k].append((ts, v))
            if self._mem_process_names:
                ret = self.at.adb.get_mem_used(*self._mem_process_names)
                ts = int(time.time())
                for k, v in ret.items():
                    if "mem" not in self.data:
                        self.data["mem"] = {}
                    if k not in self.data["mem"]:
                        self.data["mem"][k] = []
                    self.data["mem"][k].append((ts, v))
            if self._flow_pkg_names:
                for pkg_name in self._flow_pkg_names:
                    m_rx, m_tx, wifi_rx, wifi_tx = self.at.adb.get_pkg_traffic_stats(pkg_name)
                    ts = int(time.time())
                    if "flow" not in self.data:
                        self.data["flow"] = {}
                    if pkg_name not in self.data["flow"]:
                        self.data["flow"][pkg_name] = []
                    self.data["flow"][pkg_name].append((ts, m_rx, m_tx, wifi_rx, wifi_tx))
            time.sleep(self._interval)

    def register_pre_shell_cmd(self, cmd):
        if not isinstance(cmd, str):
            raise RuntimeError("Invalid args")

        if not self._pre_shell_cmd:
            self._pre_shell_cmd = cmd
        elif isinstance(self._pre_shell_cmd, str):
            self._pre_shell_cmd = [self._pre_shell_cmd, cmd]
        elif isinstance(self._pre_shell_cmd, list):
            self._pre_shell_cmd.append(cmd)




def run(serial):
    at = At(serial)
    c = PerfCollector(at)
    process = ["com.tencent.mm", "com.tencent.mm:appbrand0"]
    c.collect_cpu(*process)
    c.collect_mem(*process)
    c.setDaemon(True)
    c.start()
    for i in range(1200):
        # print c.data
        for key in c.data:
            for process_name in c.data[key]:
                print(key, process_name)
                values = c.data[key][process_name]
                print(', '.join([str(v[1]) for v in values]))
        time.sleep(5)
    c.stop()

if __name__ == '__main__':
    run("7253a40d")