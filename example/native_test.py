#!/usr/bin/env python3
#原生组件示例-小程序依赖于微信生态，有很多API涉及到微信内部的回调，对于这部分的UI操作我们提供一些函数封装
import minium

class NativeTest(minium.MiniTest):
  def test_modal(self):
    """
    操作原生modal实例
    """
    self.app.navigate_to("/page/API/pages/modal/modal")
    self.page.get_element("button", inner_test="有标题的modal").click()
    self.captrue("有标题的小程序modal")
    self.native.handle_modal("确定")
    self.page.get_element("button", inner_test="无标题的modal").click()
    self.captrue("无标题的小程序modal")
    self.native.handle_modal("取消")