# `Class` minium.BaseElement :id=minium-element
> `Element` 提供了对页面元素控件进行操作, 以及在控件内查找子控件的能力

**Properties:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|size|dict|Not None|元素宽高：{w, h}|
|offset|dict|Not None|元素偏移：{x, y}|
|rect|dict|Not None|元素位置：{x, y, w, h}|
|value|str|Not None|元素值|
|inner_text|str|Not None|元素文本|
|inner_wxml|str|Not None|获取元素子元素的 wxml（不包含本身）|
|outer_wxml|str|Not None|获取元素自身的 wxml（只包含其本身）|

---

## BaseElement() :id=init
> 小程序控件实例

!> 通常不需要你去初始化这个类，如果你想获取当前页面元素，可以调用 [Page 层](minium/Python/api/Page?id=get_element) 的方法获取

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|element_id|str|Not None|元素 id|
|page_id|int|Not None|页面 id|
|tag_name|str|Not None|标签名称|
|connection|object|Not None|与 ide 的 websocket 连接|

---

## get_element() :id=get_element
> 在当前控件内查询控件, 如果匹配到多个结果, 则返回第一个匹配到的结果

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|selector|str|Not None|选择器|
|inner_text|str|None|通过控件内的文字识别控件|
|text_contains|str|None|通过控件内的文字模糊匹配控件|
|value|str|None|通过控件的 value 识别控件|
|max_timeout|int|10|超时时间，单位 s|

*PS:[selector](https://developers.weixin.qq.com/miniprogram/dev/api/wxml/SelectorQuery.select.html) 类似于 CSS 的选择器，但仅支持下列语法:*

- ID选择器：#the-id
- class选择器（可以连续指定多个）：.a-class.another-class
- 子元素选择器：.the-parent > .the-child
- 后代选择器：.the-ancestor .the-descendant
- 跨自定义组件的后代选择器：.the-ancestor >>> .the-descendant
- 多选择器的并集：#a-node, .some-other-nodes

**Returns:**
- [Element](minium/Python/api/element) 对象, `object`

---

## get_elements() :id=get_elements
> 在当前控件内查询控件, 并返回一个或者多个结果

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|selector|str|Not None|选择器|
|max_timeout|int|20|超时时间，单位 s|

**PS: 支持的选择器同 [get_element()](minium/Python/api/Element?id=get_element)**

**Returns:**
- [Element](minium/Python/api/element) 对象列表, ` list[object]`

---

## attribute() :id=attribute
> 获取元素属性

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|name|str|Not None|属性名称|


**Returns:**
- 属性值, `str`

---

## handle_picker() :id=handle_picker
> 处理 picker 组件

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|value|看下表|Not None|属性名称|

**value 的取值：**

|选择器类型|类型| 说明|
| :----- | :-----: | :----- |
|selector: 普通选择器|int|表示选择了 range 中的第几个 (下标从 0 开始) |
|multiSelector: 多列选择器|int|表示选择了 range 中的第几个 (下标从 0 开始) |
|time: 时间选择器|str|表示选中的时间，格式为"hh:mm"|
|date: 日期选择器|str|表示选中的日期，格式为"YYYY-MM-DD"|
|region: 省市区选择器|int|表示选中的省市区，默认选中每一列的第一个值|

**Returns:**
- `None`

---

## trigger() :id=trigger
> 触发元素事件

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|trigger_type|str|Not None|触发事件类型|
|detail|dict|None|触发事件时传递的 detail 值|

**Returns:**
- `None`

---


## tap() :id=tap
> 点击元素

---

## click() :id=click
> 点击元素, 同 [tap()](minium/Python/api/Element?id=tap)

--- 

## long_press() :id=long_press
> 长按元素

---

## styles() :id=styles
> 获取元素的样式属性

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|names|str \| list |Not None|需要获取的 style 属性|


**Returns:**
- `List`

---