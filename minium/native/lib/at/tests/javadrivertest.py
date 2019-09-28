#!/usr/bin/env python
# encoding:utf-8
import logging
from attestbase import AtTestBase

logger = logging.getLogger()


class JavaDriverTest(AtTestBase):
    def test_dump_ui(self):
        ui_views = self.at.java_driver.dump_ui()
        self.assertTrue(len(ui_views)>1)
        for ui_view in ui_views:
            logger.info(ui_view)