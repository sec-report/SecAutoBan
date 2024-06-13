# OPNsense

OPNsense封禁模块

## 配置OPNsense

### 添加API

查看[官方文档](https://docs.opnsense.org/development/how-tos/api.html)为用户添加API密钥

### 创建别名组

在`防火墙-别名`页面新建别名`sec_auto_ban`并保存:

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/block/opnsense/img/1.jpg)

### 为别名组创建封禁规则

在`防火墙-规则-浮动`页面新建两条规则，分别为阻止源IP为别名组及目标IP为别名组，图例:

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/block/opnsense/img/2.jpg)

### 安装依赖

```
pip3 install pycryptodome websocket-client requests
```

### 配置模块

#### 修改回连核心模块配置

更改脚本第`135`-`137`行

```
server_ip = "127.0.0.1"
server_port = 8080
sk = "sk-xxx"
```

#### 修改与WAF连接的地址

更改脚本第`138`行

```
opnsense_url = "http://xxx.xxx.xxx.xxx"
```

#### 修改刚刚获取的API

更改脚本第`140`-`141`行

```
opnsense_api_key = 'xxx'
opnsense_api_secret = 'xxx'
```
