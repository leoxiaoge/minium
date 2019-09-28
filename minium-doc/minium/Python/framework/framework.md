# 测试框架

minium提供一个基于[unittest](https://docs.python.org/3/library/unittest.html)封装好的测试框架，利用这个简单的框架对小程序测试可以起到事半功倍的效果。

## 测试基类
测试基类MiniTest会根据[测试配置](minium/Python/framework/config.md)进行测试，minitest向上继承了unittest.TestBase，并做了以下改动：

1. 加载读取测试配置
1. 在合适的时机初始化minium.Minium和minium.Native
1. 拦截assert调用，记录检验结果
1. 记录运行时数据和截图，用于测试报告生成

使用MiniTest可以大大降低小程序测试成本。

## 测试执行

测试用例的执行可以用执行unittest的方式，也可以用我们提供的脚本`miniruntest`来加载用例，相关的参数说明如下:

- **-h /--help**: 使用帮助。

- **-v /--version**:  查看 minium 的版本。

- **-t PATH/--path PATH**: 用例所在的文件夹，默认当前路径。

- **-p PKG/--pkg PKG**: 用例的包名或者文件名

- **-c CASE/--case CASE**: `test_`开头的用例名

- **-s SUITE/--suite SUITE**:测试计划文件，比如我们的测试demo，测试文件的格式如下:

  ```json
  {
    "pkg_list": [
      {
        "pkg": "pkg1.*",
        "case_list": [
          "test_*"
        ]
      },
       {
        "pkg": "pkg2.*",
        "case_list": [
          "test_*"
        ]
      }
    ]
  }
  ```
  suite.json的`pkg_list`字段说明要执行用例的内容和顺序，`pkg_list`是一个数组，每个数组元素是一个匹配规则，会根据`pkg`去匹配包名，找到测试类，然后再根据`case_list`里面的规则去查找测试类的测试用例。可以根据需要编写匹配的粒度。注意匹配规则不是正则表达式，而是[通配符](https://www.gnu.org/software/findutils/manual/html_node/find_html/Shell-Pattern-Matching.html)。

  ?> 测试文件可以指定特定的用例，规定执行顺序


- **-f CONFIG/ --config CONFIG**:配置文件名，配置项目参考[配置文件](minium/Python/framework/config.md)

- **-g /--generate**: 生成网页测试报告。



## 测试结果

每条用例的测试结果我们会存放到一个目录里面，里面包含:

1. 包含用例执行信息的json文件
2. 用例运行中的截图
3. 用例运行中的日志
4. 小程序运行中的日志

基于这些数据可以生成测试报告，也可以做一些存档的事情。

## 测试报告
根据用例的执行结果，我们基于[Vue](https://cn.vuejs.org/v2/guide/installation.html)和[element](https://element.eleme.cn/#/zh-CN)提供一个简单的测试报告：[例子](http://localhost:3000/minium/Python/minium_report/index.html)。


报告生成有2种方式:

1. 执行用例的时候加上`-g`参数
1. 针对已经生成的用例结果目录
   ```shell
   minireport input_path output_path
   ```
   `output_path`里面会生成有报告的入口。


生成报告之后，在对应的目录下面有index.html文件，但是我们不能直接用浏览器打开这个
文件，需要把这个目录放到一个静态服务器上。以下方式都是可行的:

1. 本地执行`python3 -m http.server 8080 -d /path/to/dir/of/report `，然后浏览器输入:`http://localhost:8080/`
   
  PS: *其中`/path/to/dir/of/report`为上文的`output_path`*
2. Jenkins部署用例之后，把所有
3. 利用nginx的配置:
    ```nginx
    server {
      listen 80;
      server_name  your.domain.com;

      location / {
        alias /path/to/dir/of/report;
        index index.html;
      }
    }
    ```



