# SecAutoBan
安全设备告警IP全自动封禁平台，支持百万IP秒级分析处理。

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/index.jpg)
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

使用该Key运行告警处理模块，请跳转：[device/alarm](https://github.com/sec-report/SecAutoBan/tree/main/device/alarm) 查看模块编写及运行方式。

目前仓库中仅有少量模版，未适配的设备需手动实现少量函数。对于通用类设备，欢迎适配后提起PR推送至`device/alarm`目录，方便其他人使用。

## 封禁模块使用
首先在管理后台添加封禁设备：

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/block1.jpg)

添加设备后，复制设备连接Key。（注意：设备连接Key仅显示一次，请妥善保存）

![](https://raw.githubusercontent.com/sec-report/SecAutoBan/main/img/block2.jpg)

使用该Key运行告警处理模块，请点击：[device/block](https://github.com/sec-report/SecAutoBan/tree/main/device/block) 查看模块编写及运行方式。

目前仓库中仅有少量模版，未适配的设备需手动实现少量处理函数。对于通用类设备，欢迎适配后提起PR推送至`device/block`目录，方便其他人使用。

## Star History

<a href="https://github.com/sec-report/SecAutoBan/stargazers">
    <img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=sec-report/SecAutoBan&type=Date">
</a> 
