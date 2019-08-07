# showArgvSocket
本程序绕过堡垒机对ssh软件的限制，然后可以愉快的使用自己熟悉终端程序，或是提供给其他操作系统直连，甚至当做跳板直连生产数据库

## 如何使用
将他代替ssh连接工具设置在堡垒机/运维管理系统的执行路径中，点击指定工具连接ssh，本工具将会把随机的ssh端口转发到本机的指定端口上（请用文本编辑器打开配置，exe的打包文件为22345，改完之后进行打包）

如果他不能识别目标主机和端口，可以根据输出的参数手动连接

## 如何自己修改的版本打包exe
首先这是一个Python3程序，你需要有Python3标准环境和自带的pip

安装打包工具pyinstaller

`
python3 -m pip install pyinstaller
`

如果是windows在安装时勾选了设置path，那么就是

`
python -m pip install pyinstaller
`

打包

`
python -m pyinstaller -F showArgvSocket.py
`

或者

`
python -m pyinstaller -F showArgvSocket.py
`
