# 报警设备处理模版

安装依赖

```
pip3 install SecAutoBan
```

## base_example

基础模版，需要修改`13-15`行配置信息

```
server_ip = "127.0.0.1",  # 平台IP
server_port = 80,  # 平台端口
sk = "sk-xxx",  # 回连密钥
```

解析函数在`5-8`行，需自行实现解析函数后调用`ws_client.send_alarm("攻击IP", "被攻击资产", "攻击方式")`函数将报警发送至平台

```
# 函数为每一秒将攻击IP：127.1.0.3，发送至平台，报警原因是：NMAP 扫描 127.0.0.1
def alarm_analysis(ws_client):
    while True:
        time.sleep(1)
        ws_client.send_alarm("127.1.0.3", "127.0.0.1", "NMAP 扫描")
```

## syslog_example

syslog模版，自带了一个syslog服务器（默认监听567端口），需要修改`26-30`行配置信息

```
listen_syslog_udp_port = 567  # syslog监听端口
...
server_ip = "127.0.0.1",  # 平台IP
server_port = 80,  # 平台端口
sk = "sk-xxx",  # 回连密钥
```

解析函数在`9-16`行，需自行实现解析函数后调用`self.ws_client.send_alarm("攻击IP", "被攻击资产", "攻击方式")`函数将报警发送至平台

```
def handle(self):
    data = self.request[0]
    message = data.decode('utf-8')
    messages = message.split('\n')
    for msg in messages:
        if msg == "":
            continue
        self.ws_client.send_alarm(msg.split('\t')[0], msg.split('\t')[1], msg.split('\t')[2])  # 按照`\t`分割字符串，第一部分作为攻击IP，第二部分作为被攻击资产，第三部分作为报警原因发送自后台。
```

> 其中`syslog_example_test.py`文件为发送UDP数据包的测试文件。
