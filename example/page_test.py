#!/usr/bin/env python3
#小程序单页面示例/一般的UI测试在前期的条件构建上面会花费很多时间，但是基于小程序的开发模式和我们的测试机接口，可以直接跳过中间页面，直接跳转到测试的页面
import time
import minium

class ComponentTest(minium.MiniTest):
  def test_set_data(self):
    self.app.navigate_to("/page/components/pages/test/test")
    self.page.data = {
      'text': "只能加文字，不能删除文字",
      'canAdd': True,
      'canRamove': False
    }
    time.sleep(1)
    self.captrue("canAdd")
    self.page.data = {
      'text': "只能删除文字，不能加文字",
      'canAdd': False,
      'canRamove': True
    }
    time.sleep(1)
    self.captrue("canRamove")
    self.page.data("button")
    
