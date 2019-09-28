# `Class` minium.Page :id=minium-page

> `Page`提供了小程序页面内包括 set data, 获取控件, 页面滚动等功能

**Properties:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|page_id|str|Not None|页面 ID|
|path|str|Not None|页面路径|
|query|str|Not None|页面参数|
|data|str|Not None|页面数据|
|inner_size|dict|Not None|窗口的大小|
|scroll_height|int|Not None| 可滚动高度|
|scroll_width|int|Not None| 可滚动宽度|
|scroll_x|int|Not None| 当前窗口顶点的 x 坐标|
|scroll_y|int|Not None| 当前窗口顶点的 y 坐标|

---

## Page() :id=init
> 创建小程序页面实例

!> 通常不需要你去初始化这个类，如果你想获取当前页面实例，可以调用 [App 层](minium/Python/api/App?id=get_current_page) 的方法获取



**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|page_id|int|Not None|页面 id|
|path|str|Not None|页面路径|
|query|str|None|页面参数|
|connection|object|Not None|与 ide 的 websocket 连接|

---

## get_element() :id=get_element
> 在当前页面查询控件, 如果匹配到多个结果, 则返回第一个匹配到的结果

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|selector|str|Not None|选择器|
|inner_text|str|None|通过控件内的文字识别控件|
|text_contains|str|None|通过控件内的文字模糊匹配控件|
|value|str|None|通过控件的 value 识别控件|
|max_timeout|int|20|超时时间，单位 s|

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

### get_elements() :id=get_elements
> 在当前页面查询控件, 并返回一个或者多个结果

**PS: 支持的选择器同 `get_element()`**

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|selector|str|Not None|选择器|
|max_timeout|int|20|超时时间，单位 s|

**Returns:**
- [Element](minium/Python/api/element) 对象列表, ` list[object]`

---

### inner_size() :id=inner_size
> 页面窗口大小

**Returns:**
- e.g. {"width": 828, "height": 1792} , `dict`

---

## scroll_to() :id=scroll_to
> 滚动到指定高度

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|scroll_top|int|Not None|高度，单位 px|
|duration|int|300|滚动动画时长，单位 ms|

**Returns:**
- `None`

---

## call_method()  :id=call_method
> 调用[page的函数](https://developers.weixin.qq.com/miniprogram/dev/reference/api/Page.html)

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|method|str|Not None|函数名称|
|args|dict|None|函数参数|

**Returns:**
- `None`

---

## wait_data_contains() :id=wait_data_contains
> 等待相应的data出现

**Parameters:**

|名称| 类型| 默认值| 说明|
| :----- | :-----: | :-----: | :----- |
|keys_list|list|Not None|等待的页面的data包含的key|
|max_timeout|int|10|超时时间，单位 s|

**Returns:**
- `None`

---





