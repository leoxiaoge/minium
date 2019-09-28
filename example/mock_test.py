#!/usr/bin/env python3
# mock示例-现在市面上很多基于定位设计功能的小程序，利用mock函数，我们可以根据自定义的位置信息编写基于定位的用例
import minium

class MockTest(minium.MiniTest):
  def test_mock_location(self):
    self.app.navigate_to("/page/API/pages/get-location/get-location")
    # 模拟武汉光谷位置
    mock_location = {"latitude": 30.5078502719, "longitude": 114.4191741943, "speed": -1,
      "accuracy": 65, "verticalAccuracy": 65, "horizontalAccuracy": 65, "errMsg": "getLocation:ok"}
    self.app.mock_wx_method("getLocation", mock_location)
    # 检查mock数据
    self.page.get_element("button", inner_text="获取位置").click()
    locations = self.page.get_element(
      ".page-body-text-location").get_elements("text")
    self.assertEqual(locations[0].inner_text, "E: 114°42′", "经度校验")
    self.assertEqual(locations[1].inner_text, "N: 30°51′", "纬度校验")
    # 去掉mock
    self.app.restore_wx_method("getLocation")
    self.page.get_element("button", inner_text="获取位置").click()
    locations = self.page.get_element(
      ".page-body-text-location").get_elements("text")
    self.assertNotEqual(locations[0].inner_text, "E: 114°42′", "经度校验")
    self.assertNotEqual(locations[1].inner_text, "N: 30°51′", "纬度校验")
