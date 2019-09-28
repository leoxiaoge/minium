# 项目配置
为了保证同一套代码在IDE，Android，IOS上运行，环境组成比较复杂，所以测试用例的运行依赖于配置文件。相关配置项说明如下表：

|配置项| 类型| 默认值| 说明|
| :----- | :----- | :----- | :----- |
|platform|String|ide| 小程序运行的平台，可选值为：`ide, Android, IOS`|
|project_path|String|空| 小程序代码的项目路径，如果配置了之后，那么需要同时配置dev_tool_path|
|dev_tool_path|String|空|小程序[IDE cli](https://developers.weixin.qq.com/miniprogram/dev/devtools/cli.html)的路径|
|enable_app_log|Boolean|True| 是否监听小程序代码返回的日志|
|outputs|String|outputs| 用例运行的结果存放目录|
|debug_mode|String|info|日志打印级别，可选:` error, warn, info, debug`|
|close_ide|Boolean|False| 是否恢复测试环境，会在结束的时候关闭IDE|
|device_desire|Object|null| 连接手机的参数，跟手机平台有关系|
|test_port|int|null| IDE监听的端口，默认为`9420`|
|no_assert_capture|Boolean|False| 在assert的时候是否不截图，False的时候截图，True的时候不截图|

其中，`device_desire`跟平台有关系，不同平台配置不一样。

## Android的device_desire配置项

|配置项| 类型| 默认值| 说明|
| :----- | :----- | :----- | :----- |
|serial|String|null| Android设备号, `adb devices`查看|
|uiautomator_version|int|1| 底层使用的Ui Automator版本， 可选: `1`, `2`|



## IOS的device_desire配置项

device_desire：

|配置项| 类型| 默认值| 说明|
| :----- | :----- | :----- | :----- |
|wda_project_path|String|not null| 自定义 wda 的路径|
|device_info|Dict|not null| 真机信息|

其中device_info：

|配置项| 类型| 默认值| 说明|
| :----- | :----- | :----- | :----- |
|udid|String|not null| 手机的 uuid |
|model|String|null| 机型|
|version|String|null| 系统版本|
|name|String|null| 设备名称|

## 例子

```json
{
  "debug_mode": "debug",
  "project_pathxx": "/Users/mmtest/code/weapp/demo",
  "enable_app_log": false,
  "platform": "ide",
  "dev_tool_path": "path/to/devTool",
  "not_restore": true,
  "device_desire":{
    "wda_project_path": "/Users/sherlock/github/appium/WebDriverAgent",
    "device_info": {
          "udid": "aee531018e668ff1aadee0889f5ebe21a2292...",
          "model": "iPhone XR",
          "version": "12.2.5",
          "name": "sherlock's iPhone"
    }
  }
}
```






