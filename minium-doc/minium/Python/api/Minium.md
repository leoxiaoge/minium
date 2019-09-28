# `Class` minium.Minium :id=minium-Minium

> `Minium`负责初始化整个自动化框架, 提供了`Driver`的启动接口, 以及测试结束之后回收资源能力

---

## Minium() :id=init
> 初始化函数

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|uri|str|ws://localhost|开发者工具自动化 WebSocket 地址|
|dev_tool_path|str|None|开发者工具的路径|
|project_path|str|None|小程序代码文件夹路径|
|test_port|int|None|开发者工具自动化端口|

---

## launch_dev_tool() :id=launch_dev_tool
> 拉起微信开发者工具，并且与开发者工具建立连接
---
## launch_dev_tool_with_login() :id=launch_dev_tool_with_login
> 以自动化模式启动微信开发者工具, 需要重新登录, 命令行下会打印二维码, 微信扫码登录。
---
## get_app_json() :id=get_app_json
> 获取 app.json 的配置，如果初始化没有`project_path`参数，那么返回None

**Returns:** 
- APP配置, `dict`
---
## get_system_info() :id=get_system_info
> 获取系统信息, 同 [wx.getSystemInfo](https://developers.weixin.qq.com/miniprogram/dev/api/base/system/system-info/wx.getSystemInfo.html)

**Returns:** 
- 系统信息, `dict`

---
## enable_remote_debug() :id=enable_remote_debug
> 在真机上运行自动化

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|use_push|bool|True| 是否直接推送到客户端 |
|path|str|None| 远程调试二维码的保存路径 |

**Returns:** 
-  `None`


---
## shutdown() :id=shutdown
> 测试结束时调用, 停止 微信开发者IDE 以及 minium, 并回收资源





