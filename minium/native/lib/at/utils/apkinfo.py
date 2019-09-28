#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2017/8/28

import logging
import zipfile
import sys
if sys.version_info[0] < 3:
    from .axmlparser import AXMLPrinter
else:
    from .axmlparser3 import AXMLPrinter

logger = logging.getLogger()


class ApkInfo(object):
    def __init__(self, apk_path):
        zf = zipfile.ZipFile(open(apk_path, 'rb'), mode='r')
        for i in zf.namelist():
            if i == "AndroidManifest.xml":
                printer = AXMLPrinter(zf.read(i))
                self.xml_obj = printer.get_xml_obj()
                break
        else:
            raise RuntimeError("AndroidManifest.xml not found in %s", apk_path)

        node = self.xml_obj.getElementsByTagName("manifest")[0]
        self.version_code = node.getAttribute("android:versionCode")
        self.version_name = node.getAttribute("android:versionName")
        self.platformBuildVersionCode = node.getAttribute("platformBuildVersionCode")
        self.platformBuildVersionName = node.getAttribute("platformBuildVersionName")
        self.pkg = node.getAttribute("package")

    @property
    def activities(self):
        return self.get_names("activity")

    @property
    def permissions(self):
        return self.get_names("uses-permission")

    def get_attribute(self, tag_name, attr_name):
        node = self.xml_obj.getElementsByTagName(tag_name)[0]
        return node.getAttribute(attr_name)

    def get_names(self, tag_name):
        ps = []
        nodes = self.xml_obj.getElementsByTagName(tag_name)
        for node in nodes:
            name = node.getAttribute("android:name")
            ps.append(name)
        return ps


if __name__ == "__main__":
    # AppBuildInfo.get_activity(ur'D:\cov973.apk')

    a = ApkInfo("/Users/mmtest/Downloads/merge.apk")
    print(a.activities)