# Minium

> `Minium`负责初始化整个自动化框架, 提供了`Driver`的启动接口, 以及测试结束之后回收资源能力

---

## Minium.create
*生成Minium实例*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|uri|string| ws://localhost |否|开发者工具自动化 WebSocket 地址|
|dev_tool_path|string| Windows: C:/Program Files (x86)/Tencent/微信web开发者工具/微信web开发者工具.exe<br>Mac: /Applications/wechatwebdevtools.app|否|开发者工具的路径|
|project_path|string| |是|小程序代码文件夹路径|
|test_port|number| 9420|否|开发者工具自动化端口|
|debug_mode|string| info|否|日志打印级别，[fatal | error | warn | info | debug]|

**返回值**
- [Minium](minium/JavaScript/api/Minium#Minium-1)

## Minium
*Miniums实例*

**属性**

|名称| 类型| 默认值|  说明|
| :----- | :-----: | :-----: | :----- |
|options|Options| |Minium 驱动配置项|

### launchDevTool
*以自动化模式启动微信开发者工具*

**返回值**
- [Minium](minium/JavaScript/api/Minium#Minium-1)

### launchDevToolWithLogin
*以自动化模式启动微信开发者工具, 需要重新登录, 命令行下会打印二维码, 微信扫码登录*

**返回值**
- [Minium](minium/JavaScript/api/Minium#Minium-1)

### getApp
*获取小程序控制实例*

**返回值**
- [App](minium/JavaScript/api/App#App-1)

### getSystemInfo
*获取系统信息, 同 [wx.getSystemInfo](https://developers.weixin.qq.com/miniprogram/dev/api/base/system/system-info/wx.getSystemInfo.html)*

**返回值**
- 系统信息, `object`

### shutdown()
*测试结束时调用, 停止 微信开发者IDE 以及 Minium, 并回收资源*





