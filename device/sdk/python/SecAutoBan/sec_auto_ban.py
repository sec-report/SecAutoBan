from . import util
from multiprocessing.pool import ThreadPool
from .websocket_client import WebSocketClient

class SecAutoBan:
    init = False
    
    def __init__(self, server_ip, server_port, sk, client_type, alarm_analysis=None, block_ip=None, unblock_ip=None, get_all_block_ip=None):
        self.client_type = client_type
        if client_type == "alarm":
            if alarm_analysis is None:
                util.print("[-] 初始化失败: 未实现告警函数")
                return
            self.alarm_analysis = alarm_analysis
        self.ws_client = WebSocketClient(server_ip, server_port, sk, client_type, block_ip, unblock_ip, get_all_block_ip)
        self.init = True

    def print(self, message):
        util.print(message)

    def run(self):
        if not self.init:
            return
        processes = 1
        if self.client_type == "alarm":
            processes += 1
        pool = ThreadPool(processes=2)
        pool.apply_async(self.ws_client.connect)
        if self.client_type == "alarm":
            pool.apply_async(self.alarm_analysis, args=(self.ws_client,))
        pool.close()
        pool.join()
