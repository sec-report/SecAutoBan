# 钉钉告警通知

本模块不会对IP进行封禁，仅作为向钉钉机器人推送通知

## 下载模块

```
wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/device/block/dingtalk_robot/dingtalk_robot.py
```

## 配置说明

### 安装依赖

```
pip3 install SecAutoBan
```

### 配置模块

#### 修改回连核心模块配置

更改脚本第`55`-`57`行

```
server_ip = "127.0.0.1",
server_port = 80,
sk = "sk-xxx",
```

#### 修改钉钉机器人配置

创建机器人后，安全设置选择加签

![](./img/1.jpg)

更改脚本第`51`、`52`行，修改Webhook地址以及签名密钥：

```
webhook = "https://oapi.dingtalk.com/robot/send?access_token="
secret = "this is secret"
```
## 运行

```shell
python3 dingtalk_robot.py
```
