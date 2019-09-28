# minium
minium 是为小程序专门开发的自动化框架, 提供了 Python 和 JavaScript 版本

依赖

    先安装minium的python版本
    下载小程序示例代码： https://github.com/leoxiaoge/minium/tree/master/example

运行用例

minitest -p apptest -g

## 特性 

- 支持一套脚本，iOS & Android & 模拟器，三端运行

- 提供丰富的页面跳转方式，看不到也能去得到

- 可以获取和设置小程序页面数据，让测试不止点点点

- 可以直接触发小程序元素绑定事件

- 支持往 AppSerive 注入代码片段

- 可以调用部分 wx 对象上的接口

- ...

## 文档使用说明

该文档使用 [docsify](https://docsify.js.org/#/zh-cn/quickstart) 框架, checkout 到本地之后，执行下面的命令即可运行：

 

安装 docsify

```shell

npm i docsify-cli -g

```

 

Checkout 

```shell

git clone https://git.weixin.qq.com/minitest/minium-doc

```


安装依赖

```shell

cd minium-doc

npm install

```

本地部署

```shell

docsify serve .

```
 

浏览器访问 http://localhost:3000 即可查看