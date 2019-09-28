#!/usr/bin/env python3
#UI测试示例,通过对元素的点击驱动小程序自动化
import time
import minium

class ComponentTest(minium.MiniTest):
  def test_ui_op(self):
    self.page.get_element("view", inner_test="视图容器").click()
    self.page.get_element(".navigator-text", inner_test="swiper").click()
    self.page.get_element("switch")[0].click()
    self.page.get_element("switch")[1].click()
