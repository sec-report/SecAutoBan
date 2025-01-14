# 长亭WAF社区版

长亭WAF社区版非专业版没有Syslog权限，采用前端轮询的方式获取告警数据。

![](./img/1.jpg)

## 下载模块

```
wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/alarm/chaitin_waf_ce/chaitin_waf_ce.py
```

## 配置说明

### 安装依赖

```
pip3 install SecAutoBan requests PyJWT
```

### 配置模块

#### 修改回连核心模块配置

更改脚本第`82`-`84`行

```
server_ip = "127.0.0.1",
server_port = 80,
sk = "sk-xxx",
```

#### 修改与WAF连接的地址

更改脚本第`74`行

```
"url": "https://xxx.xxx.xxx.xxx:9443",
```

#### 修改登录配置

WAF登录方案分为四种，适配不同情况。

##### 方案一: API连接(长亭WAF版本大于等于6.6.0)（永久使用，推荐）

登录WAF管理界面，在系统设置-API Token处生成Token并复制

![](./img/api.jpg)

将Token填写在脚本第`75`行

```
chaitin_waf_config = {
    "url": "https://xxx.xxx.xxx.xxx:9443",
    "apikey": "xxxxxxx",  # <-填写这个字段
    "jwt-secret": "", 
    "username": "",
    "password": "",
    "bearer": ""
}
```

##### 方案二: 能登录长亭WAF主机shell的情况（永久使用）

在WAF主机上执行以下命令获取JWT密钥，用于自动登录：

```shell
echo "select string_value from options where key='jwt-secret';" | sqlite3 /data/safeline/resources/mgt/mgt.db
```

![](./img/2.jpg)

> 若提示没有sqlite3，请手动安装，例如ubuntu为: `apt install -y sqlite3`。

> `/data/safeline`为长亭WAF默认安装目录，若存放在其他地方请修改。

拿到JWT密钥后填入脚本第`72`行

```
chaitin_waf_config = {
    "url": "https://xxx.xxx.xxx.xxx:9443",
    "apikey": "",
    "jwt-secret": "xxxxxxx",  # <-填写这个字段
    "username": "",
    "password": "",
    "bearer": ""
}
```

> 优先识别jwt-secret，其他字段留空即可

##### 方案三: 前端登录（永久有效，不支持TOTP）

将用户名密码填入脚本第`73`-`74`行

```
chaitin_waf_config = {
    "url": "https://xxx.xxx.xxx.xxx:9443",
    "apikey": "",
    "jwt-secret": "",
    "username": "",  # <-填写这个字段
    "password": "",  # <-填写这个字段
    "bearer": ""
}
```

##### 方案四: 前端登录，有TOTP令牌的情况（7天有效，到期需人工更新Token）

登录WAF后，F12打开开发者工具，复制浏览器中任意网络连接请求头中`Authorization`字段`Bearer`下面的字符串

![](./img/3.jpg)

拿到Token后填入脚本第`75`行

```
chaitin_waf_config = {
    "url": "https://xxx.xxx.xxx.xxx:9443",
    "apikey": "",
    "jwt-secret": "",
    "username": "",
    "password": "",
    "bearer": "xxx.xxx.xxx"  # <-填写这个字段
}
```

## 运行

```shell
python3 chaitin_waf_ce.py
```
