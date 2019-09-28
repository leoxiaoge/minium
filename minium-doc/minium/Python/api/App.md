# `Class` minium.App :id=minium-App

> `App` 提供小程序应用层面的各种操作, 包括页面跳转, 获取当前页面, 页面栈等功能

---

## App() :id=init

> 小程序控制实例

!> 通常不需要你去初始化这个类，因为在初始化 Minium() 的时候，框架内部已经帮你做了这个事情，如果你想获取当前 app 实例，可以参考下面的代码：

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|connection|object|Not None|与 ide 的 websocket 连接|

**代码示例:**

``` python
#!/usr/bin/env python3
import minium

mini = minium.Minium()
tiny_app = mini.app

```

---

## enable_log() :id=enable_log
> 启动小程序日志事件

**Returns:**
- None

---

## exit() :id=exit
> 退出小程序

!> 基础库 2.7.6 开始支持

**Returns:**
- None

---

## evaluate() :id=evaluate
> 向 app Service 层注入代码并执行

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|app_function|str|Not None|代码字符串|
|args|list|Not None|参数|

**Returns:**

success 方法回调传递的对象，转成 Dict 

---

## expose_function() :id=expose_function
> 在 AppService 全局暴露方法，供小程序侧调用测试脚本中的方法

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|name|str|Not None|供小程序调用的方法名字|
|binding_function|list|Not None|脚本中的方法实现|

**Returns:**

回调传递的对象，转成 Dict 

**代码示例:**

```python
# 配合使用 expose_function() 和 evaluate() 可以实现系统事件的 hook

# 将 _on_route_changed() 方法以 onAppRouteDone 的名字暴露给小程序
self.expose_function("onAppRouteDone", self._on_route_changed)

# 将下面这段代码注入到小程序当中
# wx.onAppRouteDone() 里面调用了上面暴露给小程序的方法
# 当 wx.onAppRouteDone() 被调用的时候，就会执行 self._on_route_changed() 方法
self.evaluate(
    "function() {wx.onAppRouteDone(function(options) {onAppRouteDone(options)})}"
)

```

---

## on_exception_thrown() :id=on_exception_thrown
> 监听小程序 js 层的错误，报错的时候执行回调

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|func|function|Not None|错误回调|

**Returns:**

回调错误消息 

**代码示例:**

```python
mini = minium.Minium()

def on_exception(e):
    print(e.message)
    print(e.stack)

mini.app.on_exception_thrown(on_exception)

# 制造一个调用不存在函数的错误
navigate_page = mini.app.navigate_to("/page/component/pages/navigator/navigate")


#wx.onload is not a function

# TypeError: wx.onload is not a function
#     at ye.onLoad (http://127.0.0.1:33826/appservice/page/component/pages/navigator/navigate.js:12:8)
#     at ye.<anonymous> (WAService.js:1:1315997)
#     at ye.p.__callPageLifeTime__ (WAService.js:1:1315742)
#     at Ct (WAService.js:1:1330692)
#     at WAService.js:1:1332186
#     at At (WAService.js:1:1332232)
#     at Function.<anonymous> (WAService.js:1:1337746)
#     at i.<anonymous> (WAService.js:1:1307261)
#     at i.emit (WAService.js:1:417150)
#     at Object.emit (WAService.js:1:576442)
```

---

## call_wx_method() :id=call_wx_method
> 调用[小程序的API](https://developers.weixin.qq.com/miniprogram/dev/api/)

!> 非sync函数都会等到complete回调之后返回

**Parameters:**

!> 无需传递 success 与 fail 回调，fail 时直接当成调用错误

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|method|str|Not None|函数名|
|args|dict|None|参数|

**Returns:**

success 方法回调传递的对象，转成 Dict 

**代码示例:**
```Python
sys_info = app.call_wx_method("getSystemInfo")
print(sys_info)

{'model': 'iPhone 6', 'pixelRatio': 2, 'windowWidth': 375, 'windowHeight': 555, 'system': 'iOS 10.0.1', 'language': 'zh', 'version': '7.0.4', 'screenWidth': 375, 'screenHeight': 667, 'SDKVersion': '2.7.3', 'brand': 'devtools', 'fontSizeSetting': 16, 'batteryLevel': 100, 'statusBarHeight': 20, 'safeArea': {'right': 375, 'bottom': 667, 'left': 0, 'top': 20, 'width': 375, 'height': 647}, 'platform': 'devtools'}
```

---

## mock_wx_method() :id=mock_wx_method
> mock掉小程序API的调用，能mock的函数参考[小程序的API](https://developers.weixin.qq.com/miniprogram/dev/api/)。


**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|method|str|Not None|函数名|
|result|Any|Not None|mock之后回调的结果|

**Returns:**
- None

**代码实例:**
```Python
# 模拟武汉光谷位置
mock_location = {"latitude":30.5078502719,"longitude":114.4191741943,"speed":-1,"accuracy":65,"verticalAccuracy":65,"horizontalAccuracy":65,"errMsg":"getLocation:ok"}
app.mock_wx_method("getLocation", mock_location)
```

---

## restore_wx_method() :id=restore_wx_method
> 去掉函数的mock

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|method|str|Not None|函数名|

**Returns:**
- None

---

## get_current_page() :id=get_current_page
> 获取当前顶层页面

**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---

## get_page_stack() :id=get_page_stack
> 获取当前小程序页面栈

**Returns:** 
- [Page](minium/Python/api/Page) 对象列表, `list[object]`

---

## go_home() :id=go_home
> 跳转到小程序首页

**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---

## navigate_to() :id=navigate_to
> 以导航的方式跳转到指定页面

!> 不能跳到 tabbar 页面。支持相对路径和绝对路径, 小程序中页面栈最多十层

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|url|str|Not None|页面路径|
|params|dict|None|页面参数|
|is_wait_url_change|bool|True|是否等待新的页面跳转|

*PS: 页面路径规则：*

- /page/tabBar/API/index: 绝对路径,最前面为/
- tabBar/API/index: 相对路径, 会被拼接在当前页面父节点的路径后面

**路径后可以带参数。参数与路径之间使用 ? 分隔，参数键与参数值用 = 相连，不同参数用 & 分隔；如 'path?key=value&key2=value2'**

**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---

## navigate_back() :id=navigate_back
> 关闭当前页面，返回上一页面或多级页面。

!> 如果超出当前页面栈最大层数，返回首页

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|delta|int|1|返回的层数|


**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---

## redirect_to() :id=redirect_to
> 关闭当前页面，重定向到应用内的某个页面

!> 不允许跳转到 tabbar 页面

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|url|str|Not None|页面路径|

*PS: 页面路径规则：*

- /page/tabBar/API/index: 绝对路径,最前面为/
- tabBar/API/index: 相对路径, 会被拼接在当前页面父节点的路径后面

**路径后可以带参数。参数与路径之间使用 ? 分隔，参数键与参数值用 = 相连，不同参数用 & 分隔；如 'path?key=value&key2=value2'**

**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---

## relaunch() :id=relaunch
> 关闭所有页面，打开到应用内的某个页面

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|url|str|Not None|页面路径|

*PS: 页面路径规则：*

- /page/tabBar/API/index: 绝对路径,最前面为/
- tabBar/API/index: 相对路径, 会被拼接在当前页面父节点的路径后面

**路径后可以带参数。参数与路径之间使用 ? 分隔，参数键与参数值用 = 相连，不同参数用 & 分隔；如 'path?key=value&key2=value2'**

**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---

## switch_tab() :id=switch_tab
> 跳转到 tabBar 页面

!> 会关闭其他所有非 tabBar 页面

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|url|str|Not None|需要跳转的 tabBar 页面的路径（需在 app.json 的 tabBar 字段定义的页面），路径后不能带参数|


**Returns:** 
- [Page](minium/Python/api/Page) 对象, `object`

---