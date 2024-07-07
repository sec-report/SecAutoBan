# 封禁设备处理模版

安装以下脚本依赖

```
pip3 install SecAutoBan
```

## base_example

基础模版分为`fat`版和`thin`版，其中fat版需要实现4个函数完成封禁全功能。若不想使用全功能，只想粗暴的封禁IP可以使用thin版。

### fat版详细说明

需要修改`31-33`行配置信息

```
server_ip = "127.0.0.1",  # 平台IP
server_port = 8080,  # 平台端口
sk = "sk-xxx",  # 回连密钥
```

共需自行实现`5-26`行的4个函数

```
# 实现设备封禁函数
def block_ip(ip):
    if check_exist_ip(ip):  # 防止重复封禁
        return
    pass


# 实现设备解封函数
def unblock_ip(ip):
    pass


# 实现获取全量已封禁IP函数
def get_all_block_ip() -> list:  # 方法用于查重及同步全量IP库时对比差异
    ip_list = []
    return ip_list


# 若有更快速方法，请重新实现查询设备是否已封禁IP函数，返回True为已封禁，返回False为未封禁
def check_exist_ip(ip) -> bool:  # 方法用于防止重复封禁单个IP
    if ip in get_all_block_ip():
        return True
    return False
```

### thin版详细说明

> thin版不会对设备已经封禁的IP进行查重，也无法同步全量IP。

需要修改`16-18`行配置信息

```
server_ip = "127.0.0.1",  # 平台IP
server_port = 8080,  # 平台端口
sk = "sk-xxx",  # 回连密钥
```

共需自行实现`5-11`行的2个函数

```
# 实现设备封禁函数
def block_ip(ip):
    pass


# 实现设备解封函数
def unblock_ip(ip):
    pass
```
