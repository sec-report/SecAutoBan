# 奇安信防火墙

奇安信防火墙封禁模块

> 其他被剪裁的类奇安信防火墙设备也可适配，例如SSL编排器等。使用API的功能点在`策略配置`-`黑白名单`-`批量黑IP封堵`，请自行测试。

## 下载模块

```
wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/block/qianxin_firewall/qianxin_firewall.py
```

## 配置奇安信防火墙

### 开启RESTful API

登录管理后台，通过`系统配置`-`设备管理`-`本机设置`-`RESTful API`启用。

### 添加RESTful API用户

通过`系统配置`-`设备管理`-`管理账号`添加账号，角色选择`RESTful API管理员`

![](./img/1.jpg)

## 配置模块

### 安装依赖

```
pip3 install SecAutoBan requests
```

### 修改配置

#### 修改回连核心模块配置

更改脚本第`123`-`125`行

```
server_ip = "127.0.0.1",
server_port = 80,
sk = "sk-xxx",
```

#### 修改与奇安信防火墙连接的地址

更改脚本第`118`行

```
"url": "http://xxx.xxx.xxx.xxx",
```

#### 填写奇安信防火墙用户名密码

更改脚本第`119`-`120`行

```
"username": "admin",
"password": "",
```

## 运行

```shell
python3 qianxin_firewall.py
```
