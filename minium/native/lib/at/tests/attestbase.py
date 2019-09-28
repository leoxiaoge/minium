#!/usr/bin/env python
# encoding:utf-8
import unittest
import logging
import logging.config
import at
import at.core.config


logger = logging.getLogger()


class AtTestBase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        at.uiautomator_version = at.core.config.UIAUTOMATOR2
        self.at = at.At()

    def tearDown(self):
        self.at.release()