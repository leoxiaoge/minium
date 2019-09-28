#!/usr/local/bin/python2.7
# encoding: utf-8
'''
Created on 2014-8-28

@author: xiazeng
'''
import logging
import os
import os.path
import re
import subprocess
import time
import traceback
import sys
import threading

from at.utils import decorator, magic
import at.keycode
import at.utils.apkinfo

logger = logging.getLogger()

if sys.version_info[0] < 3:
    basestring = (str, unicode)
else:
    basestring = str


def _run_cmd(cmd, timeout_sec, sync=True):
    """
    不支持重定向命令， 如: echo aa >> output
    """
    def _cb(p):
        logger.error("timeout %s", cmd)
        p.kill()

    if not magic.is_windows():
        if isinstance(cmd, basestring):
            args = re.split(r"\s+", cmd)
        elif isinstance(cmd, list):
            args = cmd
        else:
            raise TypeError(u"cmd should be string or list")
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if not sync:
        return proc
    timer = threading.Timer(timeout_sec, _cb, [proc])
    try:
        timer.start()
        return proc.communicate()
    finally:
        timer.cancel()


def get_device_ids():
    devices = os.popen("adb devices").read().strip().split('\n')
    devices = devices[1:]
    ret = []
    for device in devices:
        serial = re.split(r'\s+', device)[0].strip()
        status = re.split(r'\s+', device)[1].strip()
        if status == 'device':
            ret.append(serial)
    return ret


def get_device_name(device_id):
    prop = os.popen('adb -s '+device_id+' shell getprop').read()
    rets = re.findall(r"\[ro.product.model\]: \[(.*)\]", prop)
    device_name = ''
    if rets:
        device_name = rets[0]
        device_name = device_name.replace(' ', '_')
    return device_name


def get_devices_names():
    ret = {}
    for device in get_device_ids():
        ret[device] = get_device_name(device)
    return ret


def get_key_value(s, key):
    r = re.compile(key+r"\s*=\s*(.*)$", re.MULTILINE)
    m = r.search(s)
    if m:
        return m.group(1)
    return None


class AdbDumpSys(object):
    def __init__(self, serial):
        self._adb = AdbWrap.apply_adb(serial)

    def _cmd(self, args):
        return self._adb.run_shell("dumpsys " + args)

    def package(self, pkg_name):
        output = self._cmd("package " + pkg_name)

        class PackageInfo(object):
            def __init__(self, s):
                self.versionName = get_key_value(s, "versionName")
                self.firstInstallTime = get_key_value(s, "firstInstallTime")
                self.lastUpdateTime = get_key_value(s, "lastUpdateTime")

            def is_first_install(self):
                return self.firstInstallTime == self.lastUpdateTime
        if "Unable to find package" in output:
            # logger.debug(output)
            return None
        return PackageInfo(output)


class AdbException(Exception):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return repr(self._value)


class AdbWrap(object):
    _serial_kv = {}
    adb_helper_dict = {}
    default_serial = "  "
    error_tags = [
        "no devices/emulators found",
        "error: closed",
        "more than one device/emulator"
    ]

    def __init__(self, serial=None):
        self.adb_path = "adb"
        self._sdcard_path = None
        self._serial = serial
        self._last_pid = None
        self._error_msg = None
        self._last_output = None
        self._is_connected = True
        self._disconnected_cb = None
        self._call_back_list = []
        self._has_call_back = False
        serial_ids = get_device_ids()
        logger.info(str(serial_ids))
        if serial is None:
            self._serial = self.get_default_serial()
        if serial is not None and self.default_serial != serial and serial not in serial_ids:
            raise RuntimeError(u"手机不在线:"+serial)
        if self._serial is None and self.kv is None:
            self._serial_kv['none'] = {}
        elif self._serial is not None and self.kv is None:
            self._serial_kv[self._serial] = {}

    def check_connected(self):
        self.run_adb("shell echo 1")
        return self._is_connected

    def is_connected(self):
        return self._is_connected

    def add_disconnected_cb(self, _cb):
        self._call_back_list.append(_cb)
        self.check_connected()

    def set_connected_state(self, state):
        if not state:
            logger.info(id(self))
            if not self._has_call_back:
                self._has_call_back = True
                for _cb in self._call_back_list:
                    _cb(self.serial, self._last_output, self._error_msg)

        self._is_connected = state

    def is_locked(self):
        output = self.run_shell(" dumpsys window policy")
        for line in output.split("\n"):
            if "isStatusBarKeyguard" in line and "true" in line:
                return True
            if "mShowingLockscreen" in line and "true" in line:
                return True
        return False

    @classmethod
    def get_default_serial(cls):
        serial_ids = get_device_ids()
        if len(serial_ids) == 0:
            raise AdbException(u"没有在线的手机")
        elif len(serial_ids) > 1:
            raise AdbException(u"多台%d手机在线，请指定serial number" % len(serial_ids))
        else:
            return AdbWrap.default_serial

    @classmethod
    def apply_adb(cls, serial=None):
        if serial is None:
            serial = cls.get_default_serial()
        # logger.debug('serial is: %s, %s', serial, cls.adb_helper_dict.keys())
        if serial in cls.adb_helper_dict:
            # logger.debug("use cache adbHelper: " + str(serial))
            return cls.adb_helper_dict[serial]
        else:
            # logger.debug("create adbHelper: " + str(serial))
            helper = AdbWrap(serial)
            cls.adb_helper_dict[serial] = helper
            return helper

    def __run(self, cmd, sync=True):
        """
        弃用!!
        """
        logger.debug(cmd)
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except OSError as e:
            traceback.print_exc()
            raise e
        self._last_pid = process.pid
        if sync is False:
            return process.pid
        (output, error) = process.communicate()

        if error or len(error) > 0:
            logger.warning(error.strip())
        output = output.strip()
        self._last_output = output
        try:
            output = output.decode("gbk")
        except UnicodeDecodeError:
            pass    # logger.debug("decode failed")
        if len(output) < 1024:
            pass
            # logger.debug("adb output:"+output)
        return output

    def _run(self, cmd, sync=True, timeout_sec=60):
        logger.debug(cmd)
        if not sync:
            return _run_cmd(cmd, timeout_sec, sync)
        output, error = _run_cmd(cmd, timeout_sec, sync)
        try:
            if magic.is_windows():
                output = output.decode("gbk")
                error = error.decode("gbk")
            else:
                output = output.decode("utf-8")
                error = error.decode("utf-8")
        except UnicodeDecodeError:
            pass

        self._last_output = output
        self._error_msg = error
        for error_tag in self.error_tags:
            if (error and error_tag in error) or error_tag in output:
                self.set_connected_state(False)
        if error:
            logger.warning(error)

        return output

    def get_output_text(self):
        return self._last_output

    def get_output_lines(self):
        if self.get_output_text():
            lines = self.get_output_text().split("\n")
            return [l.strip() for l in lines]
        else:
            return []

    def get_error(self):
        return self._error_msg

    def clear_error(self):
        self._error_msg = None

    def set_error(self, msg):
        self._error_msg = msg

    @property
    def serial(self):
        return self._serial

    def restart_adb(self):
        self.run_adb("kill-server")
        self.run_adb("start-server")

    @property
    def kv(self):
        if self._serial is None:
            return self._serial_kv['none'] if "none" in self._serial_kv else None
        else:
            return self._serial_kv[self._serial] if self._serial in self._serial_kv else None

    def get(self, k):
        value = self.kv[k] if k in self.kv else None
        logger.debug("get in %s, %s=%s" % (str(self._serial), str(k), str(value)))
        return value

    def set(self, k, v):
        logger.debug("set in %s, %s=%s" % (str(self._serial), str(k), str(v)))
        self.kv[k] = v

    def unset(self, k):
        logger.debug("unset in %s, %s" % (str(self._serial), str(k)))
        if k in self.kv:
            del self.kv[k]

    def last_pid(self):
        return self._last_pid

    def prefix(self):
        if self._serial != AdbWrap.default_serial and self._serial is not None:
            return "%s -s %s " % (self.adb_path, self._serial)
        else:
            return "%s " % self.adb_path

    def is_pid_running(self, pid):
        if magic.is_windows():
            cmd = "tasklist /FI \"PID eq %d\"" % pid
            output = self._run(cmd)
            if str(pid) in output:
                return True
            else:
                return False
        else:
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            else:
                return True

    @at.utils.decorator.retry_in(5, 1)
    def android_pid_running(self, pid):
        cmds = ["ps", "ps -A"]
        for cmd in cmds:
            output = self.run_shell(cmd)
            lines = output.split("\n")
            for line in lines[1:]:
                line = line.strip()
                ls = re.split(r"\s+", line)
                if len(ls) < 9:
                    continue
                if pid == int(ls[1]):
                    return True
        return False

    def get_android_pid(self, pkgname):
        cmds = ["ps", "ps -A"]
        for cmd in cmds:
            output = self.run_shell(cmd)
            lines = output.split("\n")
            for line in lines[1:]:
                line = line.strip()
                ls = re.split(r"\s+", line)
                if len(ls) < 9:
                    continue
                if pkgname == ls[8]:
                    return int(ls[1])
        return None

    def get_all_android_pids(self, reg=None):
        pid_mapping = {}
        cmds = ["ps", "ps -A"]
        for cmd in cmds:
            output = self.run_shell(cmd)
            lines = output.split("\n")
            for line in lines[1:]:
                line = line.strip()
                ls = re.split(r"\s+", line)
                if len(ls) < 9:
                    continue
                elif not reg or reg.match(ls[8]):
                    pid_mapping[ls[8]] = int(ls[1])
        return pid_mapping

    def get_android_uid(self, pkgname):
        try:
            pkg_pid = self.get_android_pid(pkgname)
            status_filename = "/proc/%d/status" % pkg_pid
            output = self.run_shell("cat %s" % status_filename)
            m = re.search(r"[Uu]id:\s+(\d+)", output, re.S)
            return int(m.group(1))
        except Exception as e:
            traceback.print_exc()
            return None

    """
    流量统计相关，参考：http://stackoverflow.com/questions/12904809/tracking-an-applications-network-statistics-netstats-using-adb
    """
    def get_total_traffic_stats(self):
        output = self.run_shell("cat /proc/1/net/dev")
        lines = output.split("\n")
        m_tx = m_rx = wifi_tx = wifi_rx = 0
        for line in lines[2:]:
            line = line.strip()
            ls = re.split(r"\s+", line)
            if ls[0].startswith("rmnet") or ls[0].startswith("ccmni"):
                m_tx += int(ls[9])
                m_rx += int(ls[1])
            elif "lo" != ls[0]:
                wifi_tx += int(ls[9])
                wifi_rx += int(ls[1])
        return m_rx,m_tx, wifi_rx, wifi_tx

    def get_pkg_traffic_stats(self, pkgname):
        uid = self.get_android_uid(pkgname)
        output = self.run_shell("cat /proc/net/xt_qtaguid/stats")
        lines = output.split("\n")
        m_tx = m_rx = wifi_tx = wifi_rx = 0
        for line in lines[1:]:
            line = line.strip()
            ls = re.split(r"\s+", line)
            if len(ls)>3 and int(ls[3]) == uid:
                if ls[1].startswith("rmnet") or ls[1].startswith("ccmni"):
                    m_rx += int(ls[5])
                    m_tx += int(ls[7])
                elif ls[1] != "lo":
                    wifi_rx += int(ls[5])
                    wifi_tx += int(ls[7])
        return m_rx, m_tx, wifi_rx, wifi_tx

    def get_input_methods(self):
        outputs = self.run_shell("ime list -s")
        return [line.strip() for line in outputs.split("\n")]

    def set_input_method(self, input_method):
        return self.run_shell("ime set %s" % input_method)

    @decorator.cached_property
    def screen_size(self):
        output = self.run_shell("wm size")
        m = re.search(r"(\d+)x(\d+)", output)
        if m is not None:
            return int(m.group(1)), int(m.group(2))
        else:
            return 0, 0

    @decorator.cached_property
    def language(self):
        return self.get_property("persist.sys.language")

    @decorator.cached_property
    def sdk_version(self):
        version = self.get_property("ro.build.version.sdk")
        ret = -1
        try:
            ret = int(version)
        except Exception:
            pass
        return ret

    @decorator.cached_property
    def model(self):
        return self.get_property("ro.product.model")

    @decorator.cached_property
    def brand(self):
        return self.get_property("ro.product.brand")

    @decorator.cached_property
    def display(self):
        return self.get_property("ro.build.display.id")

    @decorator.cached_property
    def release(self):
        return self.get_property("ro.build.version.release")

    @decorator.cached_property
    def name(self):
        return self.brand

    @decorator.cached_property
    def desc(self):
        return {
            "name": self.brand,
            "model": self.model,
            "cpu": self.cpu_num,
            "language": self.language,
            "screen_size": self.screen_size,
            "release": self.release,
            "sdk_version": self.sdk_version,
            "get_mem_info": self.get_mem_info(),
            "display": self.display
        }

    @decorator.cached_property
    def cpu_num(self):
        output = self.run_shell("ls /sys/devices/system/cpu/")
        m = re.findall(r"cpu[0-9]", output, re.M)
        return len(m)

    def get_property(self, name):
        return self.run_shell("getprop "+name).strip()

    def kill_pid(self, pid):
        if not self.is_pid_running(pid):
            return
        if magic.is_windows():
            cmd = "taskkill /F /PID %d" % pid
        else:
            cmd = "kill -9 %d" % pid
        self._run(cmd)

    def kill_by_name(self, name):
        if magic.is_windows():
            cmd = "TASKKILL /F /IM %s " % name
        else:
            cmd = "killall %s" % name
        logger.info(cmd)
        self._run(cmd)

    """
    android 定义了很多keycode，如果要增加API请参考：
    https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/view/KeyEvent.java
    """
    def press_key_code(self, code):
        self.run_shell("input keyevent %d" % code)

    def press_back(self):
        self.press_key_code(at.keycode.KEYCODE_BACK)
        time.sleep(2)

    def press_enter(self):
        logger.debug("press enter")
        self.press_key_code(at.keycode.KEYCODE_ENTER)

    def press_search(self):
        self.press_key_code(at.keycode.KEYCODE_SEARCH)

    def press_delete(self, num=1):
        for i in range(num):
            self.press_key_code(at.keycode.KEYCODE_DEL)

    def press_menu(self):
        self.press_key_code(at.keycode.KEYCODE_MENU)

    def press_home(self):
        self.press_key_code(at.keycode.KEYCODE_HOME)

    def press_app_switch(self):
        self.press_key_code(at.keycode.KEYCODE_APP_SWITCH)

    def press_number(self, number):
        number = str(number)
        for i in number:
            try:
                self.run_shell("input keyevent %d" % (int(i) + 7))
            except ValueError:
                logger.error(u"number must be string")
                break

    def click_point(self, x, y):
        logger.info("click %d, %d" % (x, y))
        self.run_shell("input tap %d %d " % (x, y))
        time.sleep(0.5)

    @at.utils.decorator.retry_in(10, 1)
    def get_current_activity(self):
        act = self.get_current_activity2()
        if not act:
            output = self.run_shell("dumpsys activity activities")
            for line in output.split("\n"):
                line = line.strip()
                if "mFocusedActivity" in line:
                    m = re.search(r"((\w+?\.)+?(\w+)/(\.\w+)+)", line)
                    if m:
                        act = m.group(0)
                        break
        logger.debug('activity: %s', act)
        return act

    def _wrap_activity_name(self, pkg, act):
        pkg,  act = pkg.strip(), act.strip()
        if act.startswith("."):
            return pkg, pkg + act
        if "/" in act:
            return pkg, pkg + act.split("/")[-1]
        return pkg, act

    def _get_top_window(self, lines):
        for line in lines:
            m = re.search(r'mFocusedApp=.* ((\S*)/(.*)) ', line)
            if m:
                return self._wrap_activity_name(m.group(2), m.group(3))

        for line in lines:
           m = re.search(r'mCurrentFocus=.* ((\S*)/(.*?))[ }]', line)
           if m:
               return self._wrap_activity_name(m.group(2), m.group(3))
        return None, None

    def get_current_activity2(self):
        # as a example:
        # mCurrentFocus=Window{41d2c970 u0 com.android.launcher/com.android.launcher2.Launcher}
        # mFocusedApp=AppWindowToken{4203c170 token=Token{41b77280 ActivityRecord{41b77a28 u0 com.android.launcher/com.android.launcher2.Launcher t3}}}
        output = self.run_adb("shell dumpsys window windows") # | grep -E 'mCurrentFocus|mFocusedApp'
        lines = [line.strip() for line in output.split('\n')]
        _, act = self._get_top_window(lines)
        # logger.debug('activity: %s', act)
        return act

    def get_current_process(self):
        output = self.run_adb("shell dumpsys window windows")  # | grep -E 'mCurrentFocus|mFocusedApp'
        lines = [line.strip() for line in output.split('\n')]
        pkg, _ = self._get_top_window(lines)
        return pkg

    def get_top_process(self):
        output = self.run_shell("dumpsys activity")
        lines = [line.strip() for line in output.split('\n')]
        for line in lines:
            if "top-activity" in line:
                m = re.search(r"(\d+):(\S+)/(\w+)", line)
                return int(m.group(1)), m.group(2)
        return None, None

    def forward(self, dst_port, src_port):
        cmd = "forward tcp:%s tcp:%s" % (str(dst_port), str(src_port))
        self.run_adb(cmd)

    def forward_remove(self, port):
        cmd = "forward --remove tcp:%s" % str(port)
        self.run_adb(cmd)

    def app_is_running(self, pkg_name):
        pid = self.get_android_pid(pkg_name)
        if pid:
            return True
        else:
            return False

    def app_reset(self, packagename):
        '''
        清空应用数据，慎用
        '''
        cmd = "pm clear %s" % packagename
        return self.run_shell(cmd)

    def pkg_has_installed(self, pkg_name):
        self.run_shell("pm list packages")
        for line in self.get_output_lines():
            ls = line.split(":")
            if len(ls) == 2 and pkg_name == ls[1].strip():
                return True
        else:
            return False

    def stop_app(self, pkg_name):
        return self.run_shell("am force-stop %s" % pkg_name)

    def start_app(self, pkg_name, cls_name, option="-W -n"):
        if pkg_name.startswith(cls_name):
            outputs = self.run_shell("am start %s %s/%s" % (option, pkg_name, cls_name))
        else:
            if not cls_name.startswith("."):
                cls_name = "." + cls_name
            outputs = self.run_shell("am start %s %s/%s" % (option, pkg_name, cls_name))
        logger.debug(outputs)
        lines = outputs.split("\n")
        for line in lines:
            if "Status: ok" in line or "as been brought to the front" in line:
                return True
        else:
            return False

    def restart_app(self, pkg_name, cls_name):
        self.stop_app(pkg_name)
        time.sleep(2)
        self.start_app(pkg_name, cls_name)

    def start_service(self, pkg_name, cls_name):
        if pkg_name.startswith(cls_name):
            outputs = self.run_shell("am startservice --user 0  %s/%s" % (pkg_name, cls_name))
        else:
            if not cls_name.startswith("."):
                cls_name = "." + cls_name
            outputs = self.run_shell("am startservice --user 0 %s/%s" % (pkg_name, cls_name))
        logger.debug(outputs)
        lines = outputs.split("\n")
        for line in lines:
            if "Status: ok" in line:
                return True
        else:
            return False

    def open_activity(self, activity):
        return self.run_shell("am start %s"%activity)

    def get_cpu_rate(self, *pkg_names):
        output = self.run_shell("dumpsys cpuinfo")
        ls = re.split(r"[\r\n]+", output)
        r = re.compile(r'([\.\d]+)%')
        cmd_line_reg = r".*?(?P<all>[\.\d]+)%\s+(?P<pid>\d+)/(?P<name>.*)?:\s+(?P<user>[\.\d]+)%\s+user.*?(?P<kernel>[\.\d]+)%\s+kernel.*"
        ret = {}
        for line in ls:
            for pkg_name in pkg_names:
                if pkg_name in line:
                    m = re.match(cmd_line_reg, line)
                    if m and m.group('name') == pkg_name:
                        ret[pkg_name] = float(m.group(1))
        return ret

    def get_mem_used(self, *pkg_names):
        ret = {}
        for pkg_name in pkg_names:
            output = self.run_shell("dumpsys meminfo %s" % pkg_name)
            r = re.compile(r'TOTAL\s+(\d+)')
            r2 = re.compile(r"size:\s+\S+\s+\S+\s+\S+\s+(\d+)")
            ls = re.split(r"[\r\n]+", output)
            used = 0
            for line in ls:
                m = r.search(line)
                m2 = r2.search(line)
                if m:
                    used = int(m.group(1))/1024
                elif m2:
                    used = int(m.group(1))/1024
            ret[pkg_name] = used
        return ret


    def get_mem_info(self):
        output = self.run_shell("cat /proc/meminfo")
        m_total = re.search(r"MemTotal:\s+(\d+)\s*(\w+)", output)
        m_free = re.search(r"MemFree:\s+(\d+)\s*(\w+)", output)
        max_mem = 0
        free_mem = 0
        if None != m_total:
            max_mem = int(m_total.group(1))
            unit = m_total.group(2)
            if unit.upper() == "KB":
                max_mem /= 1024
        if None != m_free:
            free_mem = int(m_free.group(1))
            unit = m_free.group(2)
            if unit.upper() == "KB":
                free_mem /= 1024
        return max_mem, free_mem

    def ping(self, ip, num=10):
        outputs = self.run_shell("ping -c %d %s" % (num, ip))
        logger.debug(outputs)
        lines = outputs.split("\n")
        r = "(?P<num>\d+) packets.*(?P<received>\d+)\s+received, .*time (?P<costs>\d+)ms"
        for l in lines:
            m = re.match(r, l)
            if m:
                return int(m.group("num")), int(m.group("received")), int(m.group("costs"))
        return -1, -1, -1

    # ======================================================================================================
    # 底层命令
    # ======================================================================================================
    def run_shell(self, cmd, sync=True, timeout_sec=30):
        cmd = " shell " + cmd
        return self.run_adb(cmd, sync, timeout_sec=timeout_sec)

    def broadcast(self, action, params):
        s = []
        for k, v in params.items():
            if isinstance(v, int):
                s.append("-ei %s %s" % (k, v))
            else:
                s.append("-e %s %s" % (k, v))
        self.run_shell("am broadcast -a %s %s" % (action, ' '.join(s)))

    def run_adb(self, cmd, sync=True, timeout_sec=30):
        """
        运行命令: adb xxxxx
        - cmd: str || list
        """
        if not self._is_connected:
            raise RuntimeError("adb has disconnected")
        if isinstance(cmd, list):
            cmd = [self.prefix()] + cmd
        else:
            cmd = self.prefix() + cmd
        return self._run(cmd, sync, timeout_sec)

    def get_current_processes(self):
        outputs = self.run_shell("ps")
        processes = {}
        lines = outputs.replace("\r\n", "\n").split("\n")
        r = re.compile(r"\s+")
        for line in lines[1:]:
            line = line.strip()
            if line:
                ls = r.split(line)
                pid = int(ls[1])
                process = {
                    "pid": pid,
                    "ppid": int(ls[2]),
                    "name": ls[-1]
                }
                processes[pid] = process
        return processes

    def push(self, local, remote):
        if not os.path.exists(local):
            raise RuntimeError("no local file:"+local)
        cmd = "push %s %s" % (local, remote)
        outputs = self.run_adb(cmd)
        if "failed" in outputs:
            return False
        else:
            return True

    def delete(self,remote):
        self.assert_file_exists(remote)
        cmd = "shell rm %s" % remote
        return self.run_adb(cmd)

    def pull(self, remote, local):
        if local is None:
            local = os.getcwd()
        parent_directory = os.path.dirname(local)
        if not os.path.exists(parent_directory) and parent_directory.strip():
            os.makedirs(parent_directory)
        if not self.file_exists(remote):
            return False
        else:
            cmd = "pull %s %s" % (remote, local)
            outputs = self.run_adb(cmd)
            if "failed" in outputs or "error" in outputs:
                return False
            return True

    def get_sdcard_path(self):
        if self._sdcard_path is not None:
            return self._sdcard_path
        if self._serial == "f47bd83d":
            self._sdcard_path = "/storage/emulated/0"
        else:
            output = self.run_shell(" echo $EXTERNAL_STORAGE")
            if output is not None and output.strip():
                self._sdcard_path = output.strip()
            else:
                self._sdcard_path = "/sdcard"
        logger.info("sdcard:"+self._sdcard_path)
        return self._sdcard_path

    def get_file_modifytime(self, remote, is_directory=False):
        self.assert_file_exists(remote)
        if is_directory:
            opt = "-ld"
        else:
            opt = "-l"
        output = self.run_shell("ls %s %s" % (opt, remote))
        ls = output.split("\n")
        if len(ls) > 1:
            raise AdbException("%s is directry"%remote)
        m = re.search(r"\d+\-\d+\-\d+\s+\d+:\d+", output)
        if m is None:
            raise AdbException("unknow output:"+output)
        return m.group()

    def screen_cap(self, filename):
        screen_path = self.get_sdcard_path() + "/mmtest/screenshot"
        cmd = "mkdir -p "+screen_path
        self.run_shell(cmd)
        filename = os.path.basename(filename)
        filename = screen_path + "/" + filename
        cmd = "screencap -p "+filename
        self.run_shell(cmd)
        return filename

    def screen_record(self, filename, max_time, sync=True):
        screen_path = self.get_sdcard_path() + "/mmtest/record"
        cmd = "mkdir -p "+screen_path
        self.run_shell(cmd)
        filename = screen_path +"/" + filename
        cmd = "screenrecord --time-limit %s %s"%(max_time, filename)
        self.run_shell(cmd, sync)
        return filename

    @at.utils.decorator.cost_log
    def install(self, filename, opt="-r", uninstall_when_imcompatible=True):
        apk_info = at.utils.apkinfo.ApkInfo(filename)
        dumpsys = AdbDumpSys(self.serial)
        package_info = dumpsys.package(apk_info.pkg)
        cmd = " install %s %s" % (opt, filename)
        output = self.run_adb(cmd, True, 5*60)
        output += str(self._error_msg)
        if "Success" not in output:
            if "INSTALL_FAILED_UPDATE_INCOMPATIBLE" in output and uninstall_when_imcompatible:
                self.uninstall(apk_info.pkg)
                output = self.run_adb(cmd, True, 180)
                output += str(self._error_msg)
                if "Success" not in output:
                    logger.error(output)
                    return False
            else:
                logger.error(output)
                return False
        s = time.time()
        while time.time() - s < 300:
            current_package_info = dumpsys.package(apk_info.pkg)
            if package_info is None:
                if current_package_info is not None and current_package_info.is_first_install():
                    logger.info("install success, first install")
                    return True
            else:
                if current_package_info is not None:
                    if current_package_info.lastUpdateTime != package_info.lastUpdateTime:
                        return True
            time.sleep(1)
        logger.info("install timeout...")
        return False

    def push_install(self, filename, option="-r"):
        name = os.path.basename(filename)
        remote_path = "/sdcard/%s" % name
        self.push(filename, remote_path)
        output = self.run_shell("pm install %s %s" % (option, remote_path))
        if "Success" not in output:
            self.set_error(output)
            logger.error(output)
            return False
        else:
            return True

    def force_install(self, filename):
        cmd = " install -r -d "+filename
        output = self.run_adb(cmd)
        if "Success" not in output:
            self.set_error(output)
            logger.error(output)
            return False
        else:
            return True

    def uninstall(self, pkg_name):
        cmd = "uninstall "+pkg_name
        output = self.run_adb(cmd)
        return output

    def screen(self, local):
        filename = self.get_device_timefile()+".png"
        remote = self.screen_cap(filename)
        self.pull(remote, local)
        return filename

    def get_device_timefile(self):
        return self.get_device_time("%Y_%m_%d__%H_%M_%S")

    def get_device_time(self, fmt="%Y%m%d"):
        cmd = ' date "+%s"' % fmt
        return self.run_shell(cmd).strip()

    def assert_file_exists(self, filename):
        output = self.run_shell(" ls "+filename )
        if "No such" in output:
            raise AdbException(output)

    def file_exists(self, filename):
        output = self.run_shell(" ls "+filename )
        if "No such" in output:
            return False
        else:
            return True

    def get_newest_filename(self, remote_dir):
        """取指定目录下最新生成的文件"""
        self.assert_file_exists(remote_dir)
        output = self.run_shell(' "ls ' + remote_dir + ' -t | head -1"')
        return output.strip() if output and output.strip() else None

    def apk_install_info(self, pkgname):
        output = self.run_shell("pm path com.tencent.mm")
        m = re.search(r"(/\S+)+", output)
        path = m.group()
        logger.info("apk path:"+path)
        output = self.run_shell("ls -l "+path)
        m = re.search(r"\d+", output)
        return m.group(), self.get_file_modifytime(path)

    @decorator.cached_property
    def is_wetest_custom_device(self):
        model = self.get_property("ro.product.model")
        if model and "wetest" in model.lower():
            # WeTest定制手机
            return True
        return False

    @decorator.cached_property
    def is_emulator(self):
        """
        判断是否是模拟器
        :return: 
        """
        if self.is_wetest_custom_device:
            return False
        qemu = self.get_property("ro.kernel.qemu")
        if qemu and qemu != '0':
            return True
        else:
            return False


if "__main__" == __name__:
    adb = AdbWrap.apply_adb(None)
    print(adb.get_current_activity2())
    #print adb.install("/Users/mmtest/code/MMWebTest/at/bin/AtServer.apk")
