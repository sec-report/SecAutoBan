# SecAutoBan
安全设备告警IP全自动封禁平台，支持百万IP秒级分析处理。

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/index.jpg)

封禁流水：

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/flow.gif)

# 开始使用

平台分为三大模块，分别为：告警日志解析处理模块、核心处理模块、IP封禁/解禁模块。

其中，告警模块处理的IP会传入核心模块，核心模块会对IP进行去重过滤等处理，处理后IP会发送到封禁模块进行封禁。

具体流程思维导图如下：

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/mind.jpg)

## 核心模块安装
```shell
mkdir SecAutoBan && cd SecAutoBan
wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/docker-compose.yml
wget https://raw.githubusercontent.com/sec-report/SecAutoBan/main/run.sh
chmod +x run.sh
./run.sh

# 停止
./run stop

# 更新
./run update
```

Docker全部运行后访问 [http://127.0.0.1/](http://127.0.0.1/) 访问管理后台，初始化管理员账号

## 告警模块使用
首先在管理后台添加告警设备：

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/alarm1.jpg)

添加设备后，复制设备连接Key。（注意：设备连接Key仅显示一次，请妥善保存）

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/alarm2.jpg)

使用获得的设备Key运行告警模块，具体使用详情请跳转至：[device/alarm](https://github.com/sec-report/SecAutoBan/tree/main/device/alarm) 查看。

目前仓库中仅有少量模版，未适配的设备只需手动实现一个函数。对于通用类设备，欢迎适配后提起PR推送至`device/alarm`目录，方便其他人使用。

## 封禁模块使用
首先在管理后台添加封禁设备：

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/block1.jpg)

添加设备后，复制设备连接Key。（注意：设备连接Key仅显示一次，请妥善保存）

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/block2.jpg)

使用获得的设备Key运行封禁模块，具体使用详情请跳转至：[device/block](https://github.com/sec-report/SecAutoBan/tree/main/device/block) 查看。

目前仓库中仅有少量模版，未适配的设备只需手动实现两个函数。对于通用类设备，欢迎适配后提起PR推送至`device/block`目录，方便其他人使用。

## 黑/白名单说明

* 黑名单就是已经封禁的IP，已封禁的IP都可以在该列表查询到。如果设置了有效期，到期后会自动解禁、删除。
* 新增白名单时会回溯一遍已经封禁的IP，若IP已经封禁会立即封禁，并从黑名单中删除。

## 网络连接说明

* 核心模块：核心模块不会主动发起TCP连接，只需模块和管理机器能访问Web端口即可。
* 告警模块：如需监听Syslog请打开安全设备到告警模块对应UDP端口，同时告警模块需要正向访问核心模块Web端口（`WebSocket`通讯）。
* 封禁模块：封禁模块无需监听任何端口，只需要正向访问核心模块Web端口（`WebSocket`通讯），及需要连接的封禁设备即可。

## Star History

<a href="https://github.com/sec-report/SecAutoBan/stargazers">
    <img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=sec-report/SecAutoBan&type=Date">
</a> 
