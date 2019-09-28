#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2017/8/28


def is_windows():
    import platform
    pf = platform.platform()
    if "Windows" in pf:
        return True
    else:
        return False

