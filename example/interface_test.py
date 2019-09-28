#!/usr/bin/env python3
import minium

class MockTest(minium.MiniTest):
  def test_mock_location(self):
    # 将 on_load()函数以 onLoad 为名字暴露给小程序
    self.app.expose_function("onLoad", self.on_load)
    # 将代码注入到 APPService hook 生命周期函数，在 this.onLoad() 被调用时，执行上面暴露的self.on_load()函数
    self.app.evaluate(
    "function() {this.onLoad(function(options) {onLoad(options)})}")
    self.app.navigate_to("/page/component/pages/slider/slider")
    def on_load(self, message):
      # 注入 js 代码，测试小程序的接口
      print(message)
      self.app.evaluate(
        """function () {
          console.log(this.getCurrentPages().slice(-1)[0])
        }"""
    )
