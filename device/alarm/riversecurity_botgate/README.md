# 瑞数动态安全Botgate

## 下载模块

```shell
wget https://raw.githubusercontent.com/SecAegis/SecAutoBan/main/device/alarm/riversecurity_botgate/riversecurity_botgate.py
```

## 安装依赖

```shell
pip3 install SecAutoBan
```

## 配置说明

### 配置瑞数

登录瑞数管理后台，在日志外发（Syslog）配置中添加服务器，日志格式选择JSON，IP填写本模块运行的主机IP，端口可自定义配置。

配置完成保存即可。

## 运行

```shell
server_ip=127.0.0.1 server_port=80 sk=sk-xxx listen_port=514 python3 riversecurity_botgate.py
```

## 告警逻辑说明

瑞数动态安全对无动态token的请求会返回412并下发JS，正常浏览器算出token后续请求即200，因此**并非所有412都是攻击**（正常用户首次访问也会412一次）。本模块用两条路径区分：

1. **强特征即时告警**：命中瑞数明确的爬虫特征（`ua_bot`）或矛盾特征（`ChromeNoAcceptLanguage`，声称Chrome却无Accept-Language）时，立即告警。
2. **弱特征滑动窗口计数**：其余412在 `window_seconds` 秒内累计达到 `count_threshold` 次才告警。正常浏览器算出token后不再412、会被放过；算不出token持续412的爬虫会被抓出。

阈值建议上线后按实际流量观察调整。

## 环境变量说明

| 变量名            | 样例        | 描述                      |
|----------------|-----------|-------------------------|
| server_ip      | 127.0.0.1 | 平台IP                    |
| server_port    | 80        | 平台端口                    |
| sk             | sk-xxx    | 连接密钥                    |
| listen_port    | 514       | 监听Syslog端口              |
| window_seconds | 30        | 弱特征统计窗口（秒），默认30         |
| count_threshold| 20        | 窗口内412达到几次才告警，默认20      |
