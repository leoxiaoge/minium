#!/usr/bin/env python
# encoding:utf-8
import logging
from attestbase import AtTestBase

logger = logging.getLogger()


class AtDeviceTest(AtTestBase):
    def setUp(self):
        super(AtDeviceTest, self).setUp()
        self.device = self.at.device

    def test_enter(self):
        self.device.enter("xiazeng")

    def test_gesture(self):
        width = self.device.width()
        height = self.device.height()
        points = [
            (int(width * 0.1), int(0 + height * 0.5)),
            (int(width * 0.5), int(height * 0.1)),
            (int(width * 0.9), int(height * 0.5)),
            (int(width * 0.5), int(height * 0.9)),
            (int(width * 0.1), int(height * 0.5)),
        ]
        self.device.gesture(points)

    def test_screen(self):
        width = self.device.width()
        height = self.device.height()
        self.device.screen_shot("test.png")
        self.device.screen_point("half.png", 0, 0, width/2, height/2)

    def test_scroll(self):
        self.device.scroll_one_forth_page("up", 1)
        self.device.scroll_one_forth_page("up", 1)
        self.device.scroll_one_forth_page("down", 1)
        self.device.scroll_one_forth_page("down", 1)
