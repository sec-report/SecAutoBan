# 报警设备处理模版

安装以下脚本依赖

```
pip3 install pycryptodome
```

## base_example

基础模版，需要修改`91-93`行配置信息

```
server_ip = "127.0.0.1"  # 平台IP
server_port = 8080  # 平台端口
sk = "sk-xxx"  # 回连密钥
```

解析函数在`84-87`行，需自行实现解析函数后调用`send_alarm_ip("ip", "备注")`函数将报警发送至平台

```
# 函数为每一秒将攻击IP：127.1.0.3，发送至平台，报警原因是：NMAP 扫描 127.0.0.1
def analysis_alarm():
    while True:
        time.sleep(1)
        send_alarm_ip("127.1.0.3", "NMAP 扫描 127.0.0.1")
```

## syslog_example

syslog模版，自带了一个syslog服务器（默认监听514端口），需要修改`102-105`行配置信息

```
server_ip = "127.0.0.1"  # 平台IP
server_port = 8080  # 平台端口
sk = "sk-xxx"  # 回连密钥
listen_syslog_udp_port = 514  # syslog监听端口
```

解析函数在`86-92`行，需自行实现解析函数后调用`send_alarm_ip("ip", "备注")`函数将报警发送至平台
```
def handle(self):
    data = self.request[0]
    message = data.decode('utf-8')
    messages = message.split('\n')
    for msg in messages:
        if msg != "":  # 如果消息不是空
            send_alarm_ip(msg.split('\t')[0], msg.split('\t')[1])  # 按照`\t`分割字符串，前一部分作为IP发送至平台，后一部分作为报警原因发送自后台
```

> 其中`syslog_example_test.py`文件为发送UDP数据包的测试文件。
