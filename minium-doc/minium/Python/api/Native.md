# `Class` minium.Native :id=minium-native

> `Native` 提供了针对小程序内涉及原生控件的操作封装

---

## Native() :id=init
> 初始化

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|json_conf|dict|Not None|native 操作初始化参数|

Android 和 iOS 使用的 json_conf 有些许差别：

*Android json_conf ：*

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|serial|str|Not None|手机 serial 序列号|

*iOS json_conf ：*

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|wda_project_path|str|Not None|自定义 wda 的路径|
|device_info|dict|Not None|真机信息|

关于 device_info：

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|udid|str|Not None|手机的 uuid |
|model|str|None|机型|
|version|str|None|系统版本|
|name|str|None|设备名称|

---

## start_wechat() :id=start_wechat
> 启动微信


**Returns:**
- `None`

---

## stop_wechat() :id=stop_wechat
> 杀掉微信


**Returns:**
- `None`

---

## screen_shot() :id=screen_shot
> 截屏

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|filename|str|Not None|截图文件名|

**Returns:**
- `None`

---

## allow_login() :id=allow_login
> 处理微信登陆确认弹框，点击允许或者取消

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|answer|bool|True|True 或 False|

**Returns:**
- `None`

---


## allow_get_user_info() :id=allow_get_user_info
> 处理获取用户信息确认弹框

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|answer|bool|True|True 或 False|

**Returns:**
- `None`

---

## allow_get_location() :id=allow_get_location
> 处理获取位置信息确认弹框

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|answer|bool|True|True 或 False|


**Returns:**
- `None`

---

## handle_modal() :id=handle_modal
> 处理模态弹窗

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|title|str|None|传入弹窗的 title 可以校验当前弹窗是否为预期弹窗|
|btn_text|str|确定|根据传入的 name 进行点击|


**Returns:**
- `None`

---

## handle_action_sheet() :id=handle_action_sheet
> 处理上拉菜单

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|item|str|Not None|要选择的 item|

**Returns:**
- `None`

---

## forward_miniprogram() :id=forward_miniprogram
> 通过右上角更多菜单转发小程序

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|name|str|Not None|要分享的人|
|text|str|None|分享携带的内容|
|create_new_chat|bool|True|是否新建聊天|

**Returns:**
- `None`

---

## forward_miniprogram_inside() :id=forward_miniprogram_inside
> 小程序内触发转发小程序

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|name|str|Not None|要分享的人|
|text|str|None|分享携带的内容|
|create_new_chat|bool|True|是否新建聊天|

**Returns:**
- `None`

---