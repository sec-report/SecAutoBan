# 长亭WAF社区版

长亭WAF社区版非专业版没有Syslog权限，采用前端轮询的方式获取告警数据。

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/alarm/chaitin_waf_ce/img/1.jpg)

## 配置说明

### 安装依赖

```
pip3 install pycryptodome websocket-client PyJWT
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
chaitin_waf_url = "https://xxx.xxx.xxx.xxx:9443"
```

#### 修改登录配置

由于长亭WAF前端登录Token的有效期为7天，存在7天后Token失效的问题，所以登录方案分为两种，适配两种不同情况。

##### 方案一，能登录长亭WAF主机shell的情况（永久使用，无需二次管理）

在WAF主机上执行以下命令获取JWT密钥，用于自动登录：

```shell
echo "select string_value from options where key='jwt-secret';" | sqlite3 /data/safeline/resources/mgt/mgt.db
```

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/alarm/chaitin_waf_ce/img/2.jpg)

> 若提示没有sqlite3，请手动安装，例如ubuntu为: `apt install -y sqlite3`。

> `/data/safeline`为长亭WAF默认安装目录，若存放在其他地方请修改。

拿到JWT密钥后填入脚本第`140`行

```
chaitin_waf_login_conf = {
    "jwt-secret": "xxxxxxx",  # <-填写这个字段
    "bearer": "xxx.xxx.xxx"  # 优先识别jwt-secret，无需修改这个Key
}
```

##### 方案二，只有Web权限的情况（7天有效，需人工更新）

登录WAF后，F12打开开发者工具，复制浏览器中任意网络连接请求头中`Authorization`字段`Bearer`下面的字符串

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/alarm/chaitin_waf_ce/img/3.jpg)

拿到Token后填入脚本第`141`行

```
chaitin_waf_login_conf = {
    "jwt-secret": "",  # jwt-secret请保持留空
    "bearer": "xxx.xxx.xxx"  # <-填写这个字段
}
```

### 运行

```shell
python3 chaitin_waf_ce.py
```
