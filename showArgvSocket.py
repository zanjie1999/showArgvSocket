# -*- encoding:utf-8 -*-

# 展示传入的参数 并启动转发

import socket
import sys
import threading
import time
from sys import argv

# 转发目标端口
lPort = 22345

streams = [None, None]  # 存放需要进行数据转发的两个数据流（都是 SocketObj 对象）
debug = 0

# 从streams获取另外一个流对象，如果当前为空，则等待
def _get_another_stream(num):
    if num == 0:
        num = 1
    elif num == 1:
        num = 0
    else:
        raise 'ERROR'

    while True:
        if streams[num] == 'quit':
            print('can not connect to the target, quit now!')
            sys.exit(1)

        if streams[num] is not None:
            return streams[num]
        else:
            time.sleep(1)

# 交换两个流的数据 num为当前流编号,主要用于调试目的，区分两个回路状态用
def _xstream(num, s1, s2):
    try:
        while True:
            # 注意，recv 函数会阻塞，直到对端完全关闭（close 后还需要一定时间才能关闭，最快关闭方法是 shutdow）
            buff = s1.recv(1024)
            if debug > 0:
                print('%d recv' % num)
            if len(buff) == 0:  # 对端关闭连接，读不到数据
                print('%d one closed' % num)
                break
            s2.sendall(buff)
            if debug > 0:
                print('%d sendall' % num)
    except:
        print('%d one connect closed.' % num)

    try:
        s1.shutdown(socket.SHUT_RDWR)
        s1.close()
    except:
        pass

    try:
        s2.shutdown(socket.SHUT_RDWR)
        s2.close()
    except:
        pass

    streams[0] = None
    streams[1] = None
    print('%d CLOSED' % num)

# 处理服务情况，num 为流编号（第 0 号还是第 1 号）
def _server(port, num):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', port))
    srv.listen(1)
    while True:
        conn, addr = srv.accept()
        print('connected from: %s' % str(addr))
        streams[num] = conn  # 放入本端流对象
        s2 = _get_another_stream(num)  # 获取另一端流对象
        _xstream(num, conn, s2)

# 处理连接，num 为流编号（第 0 号还是第 1 号）如果连接不到远程，会 sleep 36s，最多尝试 200（即两小时）
def _connect(host, port, num):
    not_connet_time = 0
    wait_time = 36
    try_cnt = 199
    while True:
        if not_connet_time > try_cnt:
            streams[num] = 'quit'
            print('not connected')
            return None

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((host, port))
        except Exception:
            print('can not connect %s:%s!' % (host, port))
            not_connet_time += 1
            time.sleep(wait_time)
            continue

        print('connected to %s:%i' % (host, port))
        streams[num] = conn  # 放入本端流对象
        s2 = _get_another_stream(num)  # 获取另一端流对象
        _xstream(num, conn, s2)


# main
print()
print(argv)
print()

print('File name:', argv[0])

cmd = argv[0]
cHost = -1
cPort = -1
isUrl = ''
url = ''
local = ''
userAndPwd = []
for i in range(1, len(argv)):
    print(i, " -> ", argv[i])
    cmd += " " + argv[i]
    if argv[i] == '-h':
        cHost = i + 1
    if argv[i] == '-p':
        cPort = i + 1
    if argv[i].startswith('sftp://'):
        # Fz sftp
        isUrl = 'sftp'
        url=argv[i].split(' ')[0]
        userAndPwd = url.split('@')[0].replace('sftp://', '', 1).split(':', 1)
        cHost = url.split('@')[1]
    if argv[i].startswith('ssh://'):
        # Xshell url
        isUrl = 'ssh'
        url=argv[i]
        userAndPwd = url.split('@')[0].replace('ssh://', '', 1).split(':', 1)
        cHost = url.split('@')[1]

print()
print(cmd)
print()
if isUrl:
    print()
    print('Url:', url)
    if isUrl == 'sftp' and '/' in cHost:
        print('Local:', '' + cHost.split('/')[1])
        cHost = cHost.split('/')[0]
    if ':' in cHost:
        cPort = cHost.split(':')[1]
        cHost = cHost.split(':')[0]
    else:
        cPort = '22'
    print('Username:',userAndPwd[0])
    if len(userAndPwd) > 1:
        print('Password:',userAndPwd[1])

# 如果找到了目标端口，开启转发
if cPort != -1:
    if not isUrl:
        cPort = argv[cPort]
    lT = threading.Thread(target=_server, args=(lPort, 0))
    if cHost != -1:
        if not isUrl:
            cHost = argv[cHost]
        # 避免hosts问题，ip写死
        if cHost == 'localhost':
            cHost = '127.0.0.1'
    else:
        cHost = '127.0.0.1'
    cT = threading.Thread(target=_connect, args=(cHost, int(cPort), 1))
    cT.start()
    lT.start()
    print('Socket: 127.0.0.1:' + str(lPort) + ' -> ' + cHost + ':' + cPort)
    lT.join()
    cT.join()
else:
    while(True):
        input()