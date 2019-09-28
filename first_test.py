#!/user/bin/env python3
import minium

class FirsTest(minium.MiniTest):
  def test_get_system_info(self):
    sys_info = self.app.call_wx_method("getSystemInfo")
    self.assertIn("SDKVersion", sys_info.result.result)
  def test_modal(self):
    """
    操作原生modal实例
    """
    self.app.navigate_to("/pages/selfservice/orderSelf/historyOrder/historyOrder")
    self.page.get_element("button").click()
  def test_assert_failed(self):
    """
    测试assert异常
    """
    self.assertIsInstance(self.page.query, dict)
    # 这里会报错
    self.assertEqual(self.page.path, "/pages/home/user/index")
  def test_error_failed(self):
    """
    会引起异常: AttributeError: 'NoneType' object has no attribute 'click'
    """
    self.mini.call_wx_method("getLaunchOptionsSync")
    # self.page.get_element("sunny").click()