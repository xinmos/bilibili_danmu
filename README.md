# bilibili_danmu

bilibili 获取弹幕脚本

> 需安装第三方依赖 requests：`pip install requests`

#### 知识点

B 站的 websocket 有简单的封包协议，如下

| 偏移量 | 长度 | 含义                                          |
| ------ | ---- | --------------------------------------------- |
| 0      | 4    | 封包总大小                                    |
| 4      | 2    | 头部长度                                      |
| 6      | 2    | 协议版本，目前是1 （版本为 2 时，数据被压缩） |
| 8      | 4    | 操作码（封包类型）                            |
| 12     | 4    | sequence，可以取常数1                         |

操作码类型

| 操作码 | 含义                              |
| ------ | --------------------------------- |
| 2      | 客户端发送的心跳包                |
| 7      | 客户端发送认证并加入房间          |
| 3      | 人气值，数据不是JSON，是4字节整数 |
| 5      | 命令，数据中[‘cmd’]表示具体命令   |
| 8      | 服务器发送的心跳包(没见过)        |

在python 中可用 struct 模块来进行一段数据的封包

> [struct 使用说明](https://docs.python.org/zh-cn/3/library/struct.html)

Example

```python
config = {
    'uid': 0,
    "roomid": 55,
    "protover": 1,
    "platform": "web",
    "clientver": "1.4.0"
}
config_bytes = struct.pack(f'>IHHII{len(b_config)}s', len(b_config) + 16, 16, 1, 7, 1, config)
```

就可以将 json 数据 config 封包变成 bytes 数据，之后可以通过 websocket 发送给 bilibili

