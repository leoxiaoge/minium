# Element
> `Element` 提供了对页面元素控件进行操作, 以及在控件内查找子控件的能力

---

## Element.create
*生成小程序控件实例*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|session|object| |是|小程序app实例会话信息|
|connection|object|| 是|与 ide 的 websocket 连接|
|page_id|number| |是|页面 id|
|element_id|string| |是|元素 id|
|tag_name|string| |是|标签名称|

**返回值**
- [Element](minium/JavaScript/api/Element#BaseElement)

## BaseElement
*基础小程序控件实例*

**属性**

|名称| 类型| 默认值|  说明|
| :----- | :-----: | :-----: | :----- |
|page_id|number| |页面 id|
|id|string| |元素 id|
|tag_name|string| |标签名称|
|attributes|Proxy| |属性获取函数代理|
|styles|Proxy| |样式获取函数代理|

### getElement
*在当前控件内查询控件, 如果匹配到多个结果, 则返回第一个匹配到的结果*

[selector](https://developers.weixin.qq.com/miniprogram/dev/api/wxml/SelectorQuery.select.html) 类似于 CSS 的选择器，但仅支持下列语法:

- ID选择器：#the-id
- class选择器（可以连续指定多个）：.a-class.another-class
- 子元素选择器：.the-parent > .the-child
- 后代选择器：.the-ancestor .the-descendant
- 跨自定义组件的后代选择器：.the-ancestor >>> .the-descendant
- 多选择器的并集：#a-node, .some-other-nodes

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|selector|string| |是|选择器|
|inner_text|string| |否|通过控件内的文字识别控件|
|value|string| |否|通过控件的 value 识别控件|

**返回值**
- [Element](minium/JavaScript/api/Element#Element)

### getElements
*在当前控件内查询控件, 并返回一个或者多个结果*

***PS: 支持的选择器同 [getElement](JavaScript/api/Element#getElement)***

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|selector|string| |是|选择器|

**返回值**
- Array.<[Element](minium/JavaScript/api/Element#Element)>

### attribute
*获取元素属性*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|name|string| |是|属性名称|

**返回值**
- 属性值, `string`

### handlePicker
*处理 picker 组件*

**参数**

|名称| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :----- |
| [value](minium/JavaScript/api/Element#value) | |是|属性名称|

#### value :id=value

|选择器类型|类型| 说明|
| :----- | :-----: | :----- |
|selector: 普通选择器|int|表示选择了 range 中的第几个 (下标从 0 开始) |
|multiSelector: 多列选择器|int|表示选择了 range 中的第几个 (下标从 0 开始) |
|time: 时间选择器|str|表示选中的时间，格式为"hh:mm"|
|date: 日期选择器|str|表示选中的日期，格式为"YYYY-MM-DD"|
|region: 省市区选择器|int|表示选中的省市区，默认选中每一列的第一个值|


### trigger
*触发元素事件*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|event_type|string| |是|触发事件类型, 可参考[小程序-事件类型](https://developers.weixin.qq.com/miniprogram/dev/framework/view/wxml/event.html#事件分类)|
|detail|object| |否|触发事件时传递的 detail 值，可参考[小程序-事件对象](https://developers.weixin.qq.com/miniprogram/dev/framework/view/wxml/event.html#事件对象)|

### click
*点击元素*

### longPress
*长按元素*