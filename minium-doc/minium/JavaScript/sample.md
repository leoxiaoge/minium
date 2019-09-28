# 样例
小程序既不属于HTML5，也不属于传统的App，所以小程序的测试也会区别于传统的测试，下面我们给出几个不同场景的测试例子，更多例子请参考[测试样例](todo)

以下例子皆是基于[小程序示例](https://github.com/wechat-miniprogram/miniprogram-demo)
测试示例目录结构如下
```
|
|- minium/
|- miniprogram-demo/
|- minium_test.js
```
## UI测试示例

我们可以通过对元素的点击驱动小程序自动化。

```javascript
const Minium = require("./minium")
const path = require("path")
const project_path = path.join(__dirname, "miniprogram-demo")
async function sleep(ms) {
    return new Promise( (rs, rj) => {
        setTimeout(rs, ms);
    } )
}
async function main() {
    try {
        const client = await Minium.create(undefined, undefined, project_path, undefined, "info")
        const app = await client.getApp()
        let page = await app.getCurrentPage()
        const element = await page.getElement("view", inner_text = "视图容器")
        await element.click()
        await sleep(2000)
        await client.shutdown()
    } catch (e) {
        console.error(e)
    }
    process.exit(0)
}

main()
```

?> 更多示例，请查看[小程序测试示例](todo)
