# InforPusher
 
 > 基于 FastAPI 创建的、为企业微信推送消息的服务端，作为 Server 酱的又一个轮子

## Why to build

自 4 月 Server 酱推出 turbo 版后，对免费用户有了更为严格的限制。由此产生了了写一个轮子的想法，在网上搜索了很多，大都采用 GO 语言编写类似的服务，无奈不会 GO 于是只好用 Python 造一个轮子喽。

## Usage

### How to send message with wechat work

1. 发送 get 请求：直接 HTTP GET 请求 `http://你的域名/wechat?msg=你的消息`，使用 get 请求也可以使用 post 中所支持的参数。
   
2. 发送 post 请求：请求路径为 `http://你的域名/wechat'`，参数类型为json，参数格式：
    1. `msg`: （必填）所要发送的消息，当发送 `textcard` 消息时，不宜过长，否则微信将会省略一部分内容，发送其他内容时，长度限制为 2048 字节。
    2. `type`: (可选)所发送的消息类型（合法参数为：`text`， `markdown`）。
        + `text`: （默认值）发送的消息为纯文本。
        + `markdown`: 通过 Markdown 方式发送。
    3. `title`: (`text` 为可选参数，`markdown` 为必填参数)所发送消息的标题。
    4. `url`: （可选）若同时存在 `title`，`url` 参数，则自动发送 `textcard` 消息，`url` 为点击 `textcard` 后跳转的网页地址。

### Markdown

企业微信默认支持 Markdown 展示，但是推送到微信后不再支持，于是对于 Markdown 文本，将发送 `textcard` 消息，并在点击后跳转到对应的 Markdown 页面，页面由 Misaka 实时翻译。

## ChangeLog

2021-05-19 替换 markdown 库为 misaka。

2021-05-18 添加 markdown 支持。

2021-05-17 将 post 请求中的参数由 json 转移到 form-data

## Todo List

- [x] 支持 Markdown。

- [ ] 支持推送到 e-mail。
