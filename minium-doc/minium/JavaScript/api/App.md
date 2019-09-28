# App

> `App` 提供小程序应用层面的各种操作, 包括页面跳转, 获取当前页面, 页面栈, 以及获取 App.json 配置等功能

---

##  App.create
*生成小程序控制实例,静态方法*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|session|object|| 是|存储小程序会话信息|
|connection|object|| 是|与 ide 的 websocket 连接|

**返回值**
- [App](minium/JavaScript/api/App#App-1)

## App
*小程序控制实例*

**属性**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|session|object||存储小程序会话信息|
|connection|object||与 ide 的 websocket 连接|
|launched|boolean|false|小程序是否加载完成|
|wx|Proxy||简便调用小程序方法的代理|

### getAppJson
*获取app.json的配置*

**返回值**
- [APP配置]([minium/JavaScript/api/App#App-1](https://developers.weixin.qq.com/miniprogram/dev/reference/configuration/app.html)), `object`

### getCurrentPage
*获取当前顶层页面*

**返回值**
- [Page](minium/JavaScript/api/Page)

### getPageStack
*获取当前小程序所有的页面*

**返回值**
- Array.<[Page](minium/JavaScript/api/Page)>

### goHome
*跳转到小程序首页*

**返回值**
- [Page](minium/JavaScript/api/Page)

### navigateTo
*以导航的方式跳转到指定页面, 但是不能跳到 tabbar 页面。支持相对路径和绝对路径, 小程序中页面栈最多十层*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|url|string| |是|目标页面路径<br> • /page/tabBar/API/index: 绝对路径,最前面为/<br> • tabBar/API/index: 相对路径, 会被拼接在当前页面的路径后面<br>• 路径后可以带参数。如 'path?key=value&key2=value2'|

**返回值**
- [Page](minium/JavaScript/api/Page)

### navigateBack
*关闭当前页面，返回上一页面或多级页面。*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|delta|number|1|否|返回的层数, 如果超出 page stack 最大层数返回首页|

**返回值**
- [Page](minium/JavaScript/api/Page)


### redirectTo
*关闭当前页面，重定向到应用内的某个页面。但是不允许跳转到 tabbar 页面*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|url|string| |是|目标页面路径<br> • /page/tabBar/API/index: 绝对路径,最前面为/<br> • tabBar/API/index: 相对路径, 会被拼接在当前页面的路径后面<br>• 路径后可以带参数。如 'path?key=value&key2=value2'|

**返回值**
- [Page](minium/JavaScript/api/Page)


### reLaunch
*关闭所有页面，打开到应用内的某个页面*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|url|string| |是|目标页面路径<br> • /page/tabBar/API/index: 绝对路径,最前面为/<br> • tabBar/API/index: 相对路径, 会被拼接在当前页面的路径后面<br>• 路径后可以带参数。如 'path?key=value&key2=value2'|

**返回值**
- [Page](minium/JavaScript/api/Page)


### switchTab
*跳转到 tabBar 页面，并关闭其他所有非 tabBar 页面*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|url|string| |是|需要跳转的 tabBar 页面的路径（需在 app.json 的 tabBar 字段定义的页面），路径后不能带参数|

**返回值**
- [Page](minium/JavaScript/api/Page)


### mockCodeScan
*采用 mock 返回结果的方式处理小程序扫描二维码或者条形码*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|content|string| |是|二维码内容|
  
### restoreCodeScan
*恢复小程序扫描二维码或者条形码*

