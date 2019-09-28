# 快速开始

## 运行环境

- node （>= 8.7.0）
- 微信公共库版本 >= 2.7.3
- 下载并安装自动化内测版本开发者工具 [Windows 64](https://dldir1.qq.com/WechatWebDev/auto/wechat_devtools_1.03.1906182_x64.exe)、[Windows 32](https://dldir1.qq.com/WechatWebDev/auto/wechat_devtools_1.03.1906182_ia32.exe)、[macOS](https://dldir1.qq.com/WechatWebDev/auto/wechat_devtools_1.03.1906182.dmg)


## 安装

1. 打开开发者工具的[安全模式](https://developers.weixin.qq.com/miniprogram/dev/devtools/settings.html#%E4%BB%A3%E7%90%86%E8%AE%BE%E7%BD%AE)

    ![cli/http](../resources/cli-http.png)

2. 安装 minium

    - 直接npm/tnpm安装
    ```shell
    tnpm install http://minitest.weixin.qq.com/minium/JavaScript/dist/minium-0.0.1.tar.gz
    ```

    - 下载[minium安装包](http://minitest.weixin.qq.com/minium/JavaScript/dist/minium-0.0.1.tar.gz) ，在你的项目中运行以下语句安装，`YOUR_MINIUM_TAR_FILE_PATH` 为你刚下载的安装包路径
    ```shell
    tnpm i YOUR_MINIUM_TAR_FILE_PATH
    ```


## 开始
安装完之后，新建一个`minium_test.js`文件，里面编写以下代码( 以下例子皆是基于[小程序示例](https://github.com/wechat-miniprogram/miniprogram-demo) ):

```javascript
const Minium = require("minium")
const project_path = path.join(__dirname, "miniprogram-demo")
async function main() {
    try {
        const client = await Minium.create(undefined, undefined, project_path, undefined, "info")        
        const app = await client.getApp()
        const system_info = await client.getSystemInfo()
        console.log("system_info: ", system_info)
        await client.shutdown()
    } catch (e) {
        console.error(e)
    }
    process.exit(0)
}

main()
```
然后`node minium_test.js`运行:

```shell
$ node minium_test.js
Initializing...

idePortFile: /Users/yopofeng/Library/Application Support/微信开发者工具/Default/.ide

starting ide...

IDE server has started, listening on http://127.0.0.1:11977

initialization finished

Open project with automation enabled success /Users/yopofeng/Desktop/workspace/miniprograms/demo

[warn][Wed Jun 26 2019 22:18:09 GMT+0800 (CST)]  @connect to wechat devtools fail, retry after 1 second
[info][Wed Jun 26 2019 22:18:10 GMT+0800 (CST)]  connect to wechat devtools successfully
[info][Wed Jun 26 2019 22:18:10 GMT+0800 (CST)]  devtool started
[info][Wed Jun 26 2019 22:18:10 GMT+0800 (CST)]  Start dev tool successfully
system_info:  { result:
   { errMsg: 'getSystemInfo:ok',
     model: 'iPhone X',
     pixelRatio: 3,
     windowWidth: 375,
     windowHeight: 642,
     system: 'iOS 10.0.1',
     language: 'zh',
     version: '7.0.4',
     screenWidth: 375,
     screenHeight: 812,
     SDKVersion: '2.7.0',
     brand: 'devtools',
     fontSizeSetting: 16,
     batteryLevel: 100,
     statusBarHeight: 44,
     safeArea:
      { right: 375,
        bottom: 812,
        left: 0,
        top: 44,
        width: 375,
        height: 768 },
     platform: 'devtools' } }
Initializing...

idePortFile: /Users/yopofeng/Library/Application Support/微信开发者工具/Default/.ide

IDE server has started, listening on http://127.0.0.1:11977

initialization finished

quit IDE success

[info][Wed Jun 26 2019 22:18:17 GMT+0800 (CST)]  Dev tool has quit, Minium Test complete
```

其他SDK提供的接口请参考[API文档](minium/JavaScript/api/readme.md)







