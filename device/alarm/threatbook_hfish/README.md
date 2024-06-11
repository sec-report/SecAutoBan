# 微步蜜罐HFish

## 配置说明

### 安装依赖

```
pip3 install pycryptodome websocket-client
```

### 配置模块

#### 修改回连核心模块配置

更改脚本第`120`-`122`行

```
server_ip = "127.0.0.1"
server_port = 8080
sk = "sk-xxx"
```

#### 配置与WAF连接的地址

更改脚本第`123`行

```
hfish_url = "https://xxx.xxx.xxx.xxx:4433"
```

#### 配置`api_key`

进入`平台管理-系统配置-API配置`页面，复制api_key

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/alarm/threatbook_hfish/img/1.jpg)

更改脚本第`124`行

```
hfish_api_key = "xxx"
```
