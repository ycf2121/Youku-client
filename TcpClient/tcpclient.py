import socket
from conf import setting
def client_conn():
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(setting.server_address)
    return client
