# SecAutoBan Python SDK

## 安装

```Shell
pip3 install SecAutoBan
```

## 样例

### 告警模块

```Python
from SecAutoBan import SecAutoBan

def alarm_analysis(ws_client):
    ws_client.send_alarm("127.1.0.3", "NMAP 扫描 127.0.0.1")

sec_auto_ban = SecAutoBan(
    server_ip="127.0.0.1",
    server_port=8000,
    sk="sk-*****",
    client_type="alarm",
    alarm_analysis = alarm_analysis
)
sec_auto_ban.run()
```

### 封禁模块

```Python
from SecAutoBan import SecAutoBan

def block_ip(ip):
    if check_exist_ip(ip):
        return
    pass

def unblock_ip(ip):
    pass

def get_all_block_ip() -> list:
    ip_list = []
    return ip_list

def check_exist_ip(ip) -> bool:
    return ip in get_all_block_ip()

sec_auto_ban = SecAutoBan(
    server_ip="127.0.0.1",
    server_port=8000,
    sk="sk-*****",
    client_type="block",
    block_ip = block_ip,
    unblock_ip = unblock_ip,
    get_all_block_ip= get_all_block_ip
)
sec_auto_ban.run()
```

## 参数说明

| 参数           | 描述                    | 是否需要填写          |
| ---------------- | ------------------------- | --------------- |
| server_ip        | 核心模块回连IP      | 需要             |
| server_port      | 核心模块回连端口  | 需要             |
| sk               | 设备页面生成的密钥 | 需要             |
| client_type      | 模块类型(`alarm`/`block`) | 需要             |
| alarm_analysis   | 告警分析函数        | `alarm`模块必填 |
| block_ip         | 封禁函数              | `block`模块必填 |
| unblock_ip       | 解禁函数              | `block`模块必填 |
| get_all_block_ip | 获取设备中全部封禁IP函数 | `block`模块可选 |
