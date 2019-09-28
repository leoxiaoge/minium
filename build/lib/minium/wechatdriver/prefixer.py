#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
class MediaType(Enum):
 UNKNOW=1
 VIDEO=2
 AUDIO=3
 LIVE_PLAY=4
 LIVE_PUSH=5
class MediaStatus(Enum):
 PLAYING=10
 STOP=11
 RESUME=12
 PAUSE=13
 PUSHING=14
class AppStatus(Enum):
 FOREGROUND=1001
 BACKGROUND=1002
class Orientation(Enum):
 ORIENTATION_UP=1010
 ORIENTATION_DOWN=1011
 ORIENTATION_LEFT=1012
 ORIENTATION_RIGHT=1013
# Created by pyminifier (https://github.com/liftoff/pyminifier)
