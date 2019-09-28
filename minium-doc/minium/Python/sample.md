# 示例
小程序既不属于HTML5，也不属于传统的App，所以小程序的测试也会区别于传统的测试，下面我们给出几个不同场景的测试例子
## UI测试示例

我们可以通过对元素的点击驱动小程序自动化。

```python
import time
import minium


class ComponentTest(minium.MiniTest):
    def test_ui_op(self):
        self.page.get_element("view", inner_text="视图容器").click()
        self.page.get_element(".navigator-text", inner_text="swiper").click()
        self.page.get_elements("switch")[0].click()
        self.page.get_elements("switch")[1].click()

```

## 单页面示例
一般的UI测试在前期的条件构建上面会花费很多时间，但是基于小程序的开发模式和我们的测试机接口，可以直接跳过中间页面，直接跳转到测试的页面。如：

```python
import time
import minium


class ComponentTest(minium.MiniTest):
    def test_set_data(self):
        self.app.navigate_to("/page/component/pages/text/text")
        self.page.data = {
            'text': "只能加文字，不能删除文字",
            'canAdd': True,
            'canRemove': False
        }
        time.sleep(1)
        self.capture("canAdd")
        self.page.data = {
            'text': "只能删除文字，不能加文字",
            'canAdd': False,
            'canRemove': True
        }
        time.sleep(1)
        self.capture("canRemove")
```

## 原生组件示例
小程序依赖于微信生态，有很多API涉及到微信内部的回调，对于这部分的UI操作我们提供一些函数封装。当然也可以参考[mock示例](#mock示例)。

```python
import minium


class NativeTest(minium.MiniTest):
    def test_modal(self):
        """
        操作原生modal实例
        """
        self.app.navigate_to("/page/API/pages/modal/modal")
        self.page.get_element("button", inner_text="有标题的modal").click()
        self.capture("有标题的modal")
        self.native.handle_modal("确定")
        self.page.get_element("button", inner_text="无标题的modal").click()
        self.capture("无标题的modal")
        self.native.handle_modal("取消")

```

## mock示例
现在市面上很多基于定位设计功能的小程序，利用mock函数，我们可以根据自定义的位置信息编写基于定位的用例。关于mock，请参考[mock函数](minium/Python/api/App.md#mock_wx_method)

```python
import minium


class MockTest(minium.MiniTest):

    def test_mock_location(self):
        self.app.navigate_to("/page/API/pages/get-location/get-location")

        # 模拟武汉光谷位置
        mock_location = {"latitude":30.5078502719,"longitude":114.4191741943,"speed":-1,"accuracy":65,"verticalAccuracy":65,"horizontalAccuracy":65,"errMsg":"getLocation:ok"}
        self.app.mock_wx_method("getLocation", mock_location)

        # 检查mock数据
        self.page.get_element("button", inner_text="获取位置").click()
        locations = self.page.get_element(".page-body-text-location").get_elements("text")
        self.assertEqual(locations[0].inner_text, "E: 114°42′", "经度校验")
        self.assertEqual(locations[1].inner_text, "N: 30°51′", "纬度校验")

        # 去掉mock
        self.app.restore_wx_method("getLocation")
        self.page.get_element("button", inner_text="获取位置").click()
        locations = self.page.get_element(".page-body-text-location").get_elements("text")
        self.assertNotEqual(locations[0].inner_text, "E: 114°42′", "经度校验")
        self.assertNotEqual(locations[1].inner_text, "N: 30°51′", "纬度校验")

```

## 接口测试示例

```python
import minium
class MockTest(minium.MiniTest):
    def test_mock_location(self):
        # 将 on_load()函数以 onLoad 为名字暴露给小程序
        self.app.expose_function("onLoad", self.on_load)
        # 将代码注入到 APPService hook 生命周期函数，在 this.onLoad() 被调用时，执行上面暴露的self.on_load()函数
        self.app.evaluate("function() {this.onLoad(function(options) {onLoad(options)})}")
        self.app.navigate_to("/page/component/pages/slider/slider")

    def on_load(self, message):
        # 注入 js 代码，测试小程序的接口
        print(message)
        self.app.evaluate(
            """function () {
                console.log(this.getCurrentPages().slice(-1)[0])
            }"""
        )
```
?> 更多示例，请查看[小程序测试示例](https://git.weixin.qq.com/minitest/miniprogram-demo-test.git)
