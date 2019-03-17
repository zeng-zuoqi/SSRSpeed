#coding:utf-8

import threading
import socks
import socket
import json
import time
import re
import logging
logger = logging.getLogger("Sub")

from config import config

MAX_THREAD = config["speedtestsocket"]["maxThread"]
DEFAULT_SOCKET = socket.socket
MAX_FILE_SIZE = 100 * 1024 * 1024
BUFFER = 4096
EXIT_FLAG = False
LOCAL_PORT = 1080
LOCK = threading.Lock()
TOTAL_RECEIVED = 0
MAX_TIME = 0

def setProxyPort(port):
	global LOCAL_PORT
	LOCAL_PORT = port

def restoreSocket():
	socket.socket = DEFAULT_SOCKET

def speedTestThread():
	global TOTAL_RECEIVED,MAX_TIME
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect(("cachefly.cachefly.net",80))
		s.send(b"GET /100mb.test HTTP/1.1\r\nHost: cachefly.cachefly.net\r\nUser-Agent: curl/11.45.14\r\n\r\n")
		startTime = time.time()
		received = 0
		while True:
			xx = s.recv(BUFFER)
			received += len(xx)
			if (received >= MAX_FILE_SIZE or EXIT_FLAG):
				break
		endTime = time.time()
		s.close()
		LOCK.acquire()
		TOTAL_RECEIVED += received
		MAX_TIME = max(MAX_TIME,endTime - startTime)
		LOCK.release()
	except:
		logger.exception("")
		return 0

def speedTestSocket(port):
	global EXIT_FLAG,LOCAL_PORT,MAX_TIME
	LOCAL_PORT = port
	socks.set_default_proxy(socks.SOCKS5,"127.0.0.1",LOCAL_PORT)
	socket.socket = socks.socksocket
	for i in range(0,MAX_THREAD):
		nmsl = threading.Thread(target=speedTestThread)
		nmsl.start()
	for i in range(0,100):
		time.sleep(0.1)
		if (EXIT_FLAG):
			break
	EXIT_FLAG = True
	for i in range(0,10):
		time.sleep(0.1)
		if (MAX_TIME != 0):
			break
	if (MAX_TIME == 0):
		logger.error("Socket Test Error !")
		MAX_TIME = 1
	restoreSocket()
	return TOTAL_RECEIVED / MAX_TIME

if (__name__ == "__main__"):
	print(speedTestSocket(1080))

