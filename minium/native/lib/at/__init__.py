# encoding:utf-8


from .apkapi import AppApi
from .core.uixml import UiView
from .core.adbwrap import AdbWrap
from .core import config
from .core import element, accesshelper, javadriver, uidevice
from .core import accesshelper
from .utils import decorator
from .eventmonitor import EventMonitor
from .jlogcat import JLogCat


uiautomator_version = config.UIAUTOMATOR


class At(object):
    at_cache = {}
    device_status = {}

    def __init__(self, serial=None):
        if serial is None:
            serial = AdbWrap.get_default_serial()
        self.serial = serial
        self.adb = AdbWrap.apply_adb(serial)
        self.apkapi = AppApi(self.adb)
        self.java_driver = core.javadriver.JavaDriver.apply_driver(serial, uiautomator_version)
        element.Element.bind_java_driver(self.java_driver)
        self.logcat = JLogCat(self.java_driver)
        self.device = uidevice.PyUiDevice(self.java_driver)
        self.access_helper = accesshelper.AccessHelper(self.java_driver)
        self.event_monitor = EventMonitor(self.java_driver)
        self._app_driver = None

    @classmethod
    def set_uiautomator_version(cls, version):
        logger.info("set uiautomator_version=%s", version)
        cls.uiautomator_version = version

    def register_hook(self, hook):
        self.java_driver.register(hook)

    @property
    def e(self):
        return element.Element(jd_instance=self.java_driver)

    def release(self):
        core.javadriver.JavaDriver.release_driver(self.serial)
        if self.serial in At.at_cache:
            del At.at_cache[self.serial]


class AtProxy(object):
    pass


if __name__ == '__main__':
    import logging
    import logging.config
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    uiautomator_version = config.UIAUTOMATOR2
    a = At()

    try:
        for ui_view in a.java_driver.dump_ui():
            logger.info(ui_view)
        # print a.e.text(u"消息免打扰").parent().instance(2).child().rid("com.tencent.mm:id/k2").get_desc()
    finally:
        a.release()
