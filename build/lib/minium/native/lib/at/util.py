#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2018/6/4
import socket


def iter_equal(l1, l2):
    if not isinstance(l1, (list, tuple)) or not isinstance(l2, (list, tuple)):
        return False
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False
    return True


def pick_unuse_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port