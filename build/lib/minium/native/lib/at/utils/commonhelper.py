#!/usr/bin/env python3
# Created by xiazeng on 2019/3/12
import base64


def base64_to_file(base64_str, path):
    image_data = base64.b64decode(base64_str)
    open(path, "wb").write(image_data)
