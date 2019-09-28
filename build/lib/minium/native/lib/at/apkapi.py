# encoding:utf-8
# created 2018/11/8
import os.path
import logging
import base64
import requests
import time
from .util import pick_unuse_port
from .core import adbwrap

logger = logging.getLogger()


class AppApi(object):
    PACKAGE = "com.tencent.mm.atstub"
    ACT = ".ui.LauncherUI"
    action = "com.tencent.mm.atstub.api"

    def __init__(self, _adb):
        """
        :type adb: adbwrap.AdbWrap
        """
        self.adb = _adb

    def launch(self):
        if not self.adb.pkg_has_installed(self.PACKAGE):
            apk_path = os.path.join(os.path.dirname(__file__), "bin", "AtServer.apk")
            if not self.adb.install(apk_path):
                logger.error("%s install failed", apk_path)
                return False
        r = self.adb.start_app(self.PACKAGE, self.ACT)
        time.sleep(2)
        return r

    def add_gallery(self, path):
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            encode_byte = base64.b64encode(f.read())
            encode_str = encode_byte.decode()

        port = pick_unuse_port()
        self.adb.forward(port, 56788)
        session = requests.Session()
        session.trust_env = False
        r = session.request("post", "http://localhost:%d/storage" % port,
                            params={"filename": filename, "q": "postBase64Image", "data": encode_str})
        self.adb.forward_remove(port)
        logger.debug(r.text)
        r.raise_for_status()

    def scan_gallery(self, name):
        """
        Android 8将会不兼容，请用add_gallery
        :param name:
        :return:
        """
        self.adb.broadcast(self.action, {"api": "SCAN_ALBUM", "name": name})


if __name__ == '__main__':
    pass
