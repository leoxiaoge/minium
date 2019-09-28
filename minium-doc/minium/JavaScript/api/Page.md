# Page

> `Page`提供了小程序页面内包括 set data, 获取控件, 页面滚动等功能

---

## Page.create
*创建小程序页面实例*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|session|object|| 是|存储小程序会话信息|
|connection|object|| 是|与 ide 的 websocket 连接|
|id|number|| 是|页面 id|
|path|string|| 是|页面路径|
|query|object|{}| 否|页面参数|


**返回值**
- [Page](minium/JavaScript/api/Page#Page-1)

## Page
*小程序页面实例*

**属性**

|名称| 类型| 默认值|  说明|
| :----- | :-----: | :-----: | :----- |
|session|object| |小程序app实例会话信息|
|id|number| |页面 id|
|path|string| |页面路径|
|query|object| |页面参数|
|type|[PageType](minium/JavaScript/api/Page#PageType)| NormalPage|页面类型|

#### PageType :id=PageType
|属性名|说明|
| :-----: | :----- |
|NormalPage|普通页面|
|TabbarPage|tabbar页面|

### getElement
*在当前页面查询控件, 如果匹配到多个结果, 则返回第一个匹配到的结果*

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
*在当前页面查询控件, 并返回一个或者多个结果*

***PS: 支持的选择器同 [getElement](minium/JavaScript/api/Page#getElement)***

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|selector|string| |是|选择器|

**返回值**
- Array.<[Element](minium/JavaScript/api/Element#Element)>

### innerSize
*页面窗口大小*

**返回值**

|属性名| 类型| 说明|
| :----- | :-----: | :----- |
|width|number|窗口宽|
|height|number|窗口高|

### scrollTo
*滚动到指定高度*

**参数**

|名称| 类型| 默认值| 是否必须| 说明|
| :----- | :-----: | :-----: | :-----: | :----- |
|scroll_top|number| |是|高度(px)|
|duration|number| 300|否|滚动动画时长 ms|









