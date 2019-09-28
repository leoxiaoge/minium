#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Author:         lockerzhang
Filename:       webDriverAgent.py
Create time:    2019/5/24 14:28
Description:

"""

import os
import socket
import subprocess
import re
import os.path
import requests
import time
import logging
import shutil

logger = logging.getLogger()


def exec_cmd(cmd):
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    return process.pid


def do_shell(command, print_msg=True):
    """
    执行 shell 语句
    :param command:
    :param print_msg:
    :return:
    """
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if print_msg:
        logger.debug(command)
    lines = []
    for line in iter(p.stdout.readline, b""):
        line = line.rstrip().decode("utf8")
        if print_msg:
            print(">>>%s" % line)
        lines.append(line)
        if "ServerURLHere->http://" in line:
            print(">>>%s" % line)
            time.sleep(5)
            break
    return lines


IOS_DEVICES = {
    "i386": "iPhone Simulator",
    "x86_64": "iPhone Simulator",
    "iPhone3,1": "iPhone 4",
    "iPhone3,3": "iPhone 4 (Verizon)",
    "iPhone4,1": "iPhone 4S",
    "iPhone5,1": "iPhone 5 (GSM)",
    "iPhone5,2": "iPhone 5 (GSM+CDMA)",
    "iPhone5,3": "iPhone 5C (GSM)",
    "iPhone5,4": "iPhone 5C (Global)",
    "iPhone6,1": "iPhone 5S (GSM)",
    "iPhone6,2": "iPhone 5S (Global)",
    "iPhone7,1": "iPhone 6 Plus",
    "iPhone7,2": "iPhone 6",
    "iPhone8,1": "iPhone 6s",
    "iPhone8,2": "iPhone 6s Plus",
    "iPhone8,3": "iPhone SE (GSM+CDMA)",
    "iPhone8,4": "iPhone SE (GSM)",
    "iPhone9,1": "iPhone 7",
    "iPhone9,2": "iPhone 7 Plus",
    "iPhone9,3": "iPhone 7",
    "iPhone9,4": "iPhone 7 Plus",
    "iPhone10,1": "iPhone 8",
    "iPhone10,2": "iPhone 8 Plus",
    "iPhone10,3": "iPhone X",
    "iPhone11,2": "iPhone XS",
    "iPhone11,4": "iPhone XS Max",
    "iPhone11,6": "iPhone XS Max",
    "iPhone11,8": "iPhone XR",
    "iPad1,1": "iPad 1",
    "iPad2,1": "iPad 2 (WiFi)",
    "iPad2,2": "iPad 2 (GSM)",
    "iPad2,3": "iPad 2 (CDMA)",
    "iPad2,4": "iPad 2 (WiFi)",
    "iPad2,5": "iPad Mini (WiFi)",
    "iPad2,6": "iPad Mini (GSM)",
    "iPad2,7": "iPad Mini (GSM+CDMA)",
    "iPad3,1": "iPad 3 (WiFi)",
    "iPad3,2": "iPad 3 (GSM+CDMA)",
    "iPad3,3": "iPad 3 (GSM)",
    "iPad3,4": "iPad 4 (WiFi)",
    "iPad3,5": "iPad 4 (GSM)",
    "iPad3,6": "iPad 4 (GSM+CDMA)",
    "iPad4,1": "iPad Air (WiFi)",
    "iPad4,2": "iPad Air (GSM+CDMA)",
    "iPad4,4": "iPad Mini Retina (WiFi)",
    "iPad4,5": "iPad Mini Retina (GSM+CDMA)",
    "iPad4,6": "iPad mini Retina (China)",
    "iPad4,7": "iPad mini 3 (WiFi)",
    "iPad4,8": "iPad mini 3 (GSM+CDMA)",
    "iPad4,9": "iPad Mini 3 (China)",
    "iPad5,3": "iPad Air 2 (WiFi)",
    "iPad5,4": "iPad Air 2 (Cellular)",
    "iPad6,3": "iPad Pro (9.7 inch, Wi-Fi)",
    "iPad6,4": "iPad Pro (9.7 inch, Wi-Fi+LTE)",
    "iPad6,7": "iPad Pro (12.9 inch, Wi-Fi)",
    "iPad6,8": "iPad Pro (12.9 inch, Wi-Fi+LTE)",
}


class DeviceToolException(Exception):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return repr(self._value)


class DeviceTool(object):
    def __init__(self, udid=None):
        self.udid = udid
        if self.udid is None:
            self.udid = self.get_default_udid()

    def exec_cmd(self, cmd, output=False):
        if output:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            return process.communicate()[0].strip()
        else:
            subprocess.call(cmd, shell=True)

    def list_devices(self):
        cmd = "idevice_id -l"
        devices = self.exec_cmd(cmd, True)
        device_list = []
        if len(devices) != 0:
            device_list = devices.split("\n")
        return device_list

    def get_default_udid(self):
        devices = self.list_devices()
        if len(devices) == 0:
            raise DeviceToolException(u"没有设备连接...")

        return devices[0]

    def list_user_app(self):
        cmd = "ideviceinstaller -u %s -l -o list_user" % self.udid
        return self.exec_cmd(cmd, True)

    def get_property(self, key):
        cmd = "ideviceinfo -u %s -k %s" % (self.udid, key)
        return self.exec_cmd(cmd, True)

    @property
    def name(self):
        return self.get_property("DeviceName")

    @property
    def type(self):
        t = IOS_DEVICES.get(self.get_property("ProductType"))
        if t != None:
            return t
        else:
            return "unkown"

    @property
    def os_version(self):
        return self.get_property("ProductVersion")

    @property
    def region(self):
        return self.get_property("RegionInfo")

    @property
    def timezone(self):
        return self.get_property("TimeZone")

    @property
    def desc(self):
        return {
            "manu": "Apple",
            "name": self.name,
            "model": self.type,
            "version": self.os_version,
        }

    def find_app(self, bundle_id="com.tencent.xin"):
        ids = []
        ids_wetest = {}
        installed_apps = self.list_user_app()
        for id in installed_apps.decode("utf-8").split("\n"):
            if re.search("-", id):
                str = id[0 : id.find("-")].strip()
                ids.append(str)
            if re.search(",", id):
                str_wetest = id[0 : id.find(",")].strip()
                ids_wetest[str_wetest] = id.split(", ")[1][1:-1]

        if bundle_id in ids or bundle_id in ids_wetest.keys():
            logger.info(
                "检测到已安装 %s 版本的微信" % ids_wetest[bundle_id]
            ) if bundle_id in ids_wetest.keys() else logger.info("微信已安装...")
            return True
        else:
            logger.error("检测到设备未安装微信, 请前往 APP store 安装最新版微信...")
            return False

    def screenshot(self, filename):
        cmd = "idevicescreenshot -u %s '%s'" % (self.udid, filename)
        return self.exec_cmd(cmd, True)

    def get_crashes(self, dir, app_name="WeChat"):
        """
        获取指定app的crash文件列表
        比如：
            WeChat-2018-06-13-105022.ips (计入crash)
            WeChat.wakeups_resource-2018-06-13-005223.ips (使用资源太多太频繁才被系统kill, 不计入crash)
        """
        cmd = "idevicecrashreport -k -u %s %s" % (self.udid, dir)
        report = self.exec_cmd(cmd, True)
        result = []
        for line in report.split("\n"):
            if "%s-" % app_name in line:
                index = line.index("W")
                value = line[index:].strip()
                result.append(value)
        return result

    def remove_crashes(self, dir):
        cmd = "idevicecrashreport -u %s %s" % (self.udid, dir)
        return self.exec_cmd(cmd, True)


class WebDriverRunner(object):
    def __init__(self, device_id, driver_path):
        self.device_id = device_id
        self.driver_path = driver_path
        port = self.pick_unuse_port()
        self.port = port
        self.iproxy_pid = None
        self.listen_port(port=port, device_id=device_id)

    def pick_unuse_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        addr, port = s.getsockname()
        s.close()
        return port

    def listen_port(self, port=None, device_id=None):
        filename = self.get_log_dir() + "/iproxy_" + device_id + ".log"
        cmd = "iproxy {port} 8100 {device_id} 1>{log_filename} 2>&1 &"
        cmd = cmd.format(port=port, device_id=device_id, log_filename=filename)
        logger.info("start listen: %s" % cmd)
        self.iproxy_pid = exec_cmd(cmd)

    def remove_iproxy(self):
        cmd = "kill -9 %s" % self.iproxy_pid
        logger.debug(cmd)
        exec_cmd(cmd)

    def start_driver(self):
        logger.info("driver_path: %s" % self.driver_path)

        base_cmd = "/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild"

        driver_data_home = os.path.join(self.driver_path, self.device_id)
        if os.path.exists(driver_data_home):
            shutil.rmtree(driver_data_home)
        log_dir = self.get_log_dir()
        # cmd = base_cmd + " -project {driver_path}/WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -derivedDataPath {driver_path}/{device_id} -destination 'id={device_id}' test 1>{log_dir}/driver_{device_id}.log 2>&1"
        cmd = (
            base_cmd
            + " -project {driver_path}/WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -derivedDataPath {driver_path}/{device_id} -destination 'id={device_id}' test"
        )
        cmd = cmd.format(
            driver_path=self.driver_path, device_id=self.device_id, log_dir=log_dir
        )
        logger.info(cmd)
        do_shell(cmd)

    def kill_driver(self):
        cmd = "pkill -f id=%s" % self.device_id
        exec_cmd(cmd)

    def ping_driver(self, timeout):
        url = "http://localhost:%s/status" % self.port

        try:
            res = requests.get(url, timeout=timeout)
            if res.status_code == requests.codes.ok:
                logger.info("WebDriver在线")
                return True
        except:
            logger.info("获取不到Driver状态...")
            return False

    def wait_for_driver_ready(self, timeout=100):
        s = time.time()
        while time.time() - s < timeout:
            time.sleep(10)
            if self.ping_driver(self.port, 5):
                break
        else:
            message = "%d秒后，仍获取不到Driver状态，请检查..." % timeout
            logger.error(message)
            raise RuntimeError(message)

    def get_log_dir(self):
        log_dir = os.path.join(os.path.dirname(__file__), "../log")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir


if __name__ == "__main__":
    runner = WebDriverRunner(
        device_id="00008020-000445EE3684002E",
        driver_path="/Users/sherlock/github/WebDriverAgent",
    )
    device = DeviceTool(udid="00008020-000445EE3684002E")
    device.find_app("com.tencent.xin")
