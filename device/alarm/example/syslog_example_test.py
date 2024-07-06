import socket

socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto("127.1.0.3\tNMAP 扫描 127.0.0.1".encode(), ("127.0.0.1", 567))
