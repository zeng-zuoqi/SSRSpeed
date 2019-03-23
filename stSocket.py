#coding:utf-8

import threading
import socks
import socket
import requests
import json
import time
import re
import logging
logger = logging.getLogger("Sub")
"""
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
"""

from config import config

MAX_THREAD = config["speedtestsocket"]["maxThread"]
DEFAULT_SOCKET = socket.socket
MAX_FILE_SIZE = 100 * 1024 * 1024
BUFFER = config["speedtestsocket"]["buffer"]
EXIT_FLAG = False
LOCAL_PORT = 1080
LOCK = threading.Lock()
TOTAL_RECEIVED = 0
DELTA_RECEIVED = 0
MAX_TIME = 0

def setProxyPort(port):
	global LOCAL_PORT
	LOCAL_PORT = port

def restoreSocket():
	socket.socket = DEFAULT_SOCKET

def parseLocation():
	try:
		rep = requests.get("http://ip-api.com/json",proxies = {
			"http":"socks5h://127.0.0.1:%d" % LOCAL_PORT,
			"https":"socks5h://127.0.0.1:%d" % LOCAL_PORT
		})
		tmp = rep.json()
		if (tmp["status"] == "success"):
			logger.info("Server Country Code : %s,Timezone : %s" % (tmp["countryCode"],tmp["timezone"]))
			return (True,tmp["countryCode"],tmp["timezone"])
	except:
		logger.exception("Parse location failed.")
		try:
			logger.error(rep.content)
		except:
			pass
	return(False,"ALL","ALL")

def speedTestThread(link):
	global TOTAL_RECEIVED,MAX_TIME,DELTA_RECEIVED
	link = link.replace("https://","").replace("http://","")
	host = link[:link.find("/")]
	requestUri = link[link.find("/"):]
	logger.debug("\nLink: %s\nHost: %s\nRequestUri: %s" % (link,host,requestUri))
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			s.connect((host,80))
		except socks.GeneralProxyError:
			pass
		s.send(b"GET %b HTTP/1.1\r\nHost: %b\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36\r\n\r\n" % (requestUri.encode("utf-8"),host.encode("utf-8")))
		startTime = time.time()
		received = 0
		while True:
			xx = s.recv(BUFFER)
		#	received += len(xx)
			LOCK.acquire()
			TOTAL_RECEIVED += len(xx)
			LOCK.release()
			if (received >= MAX_FILE_SIZE or EXIT_FLAG):
				break
		endTime = time.time()
		s.close()
		LOCK.acquire()
	#	TOTAL_RECEIVED += received
		MAX_TIME = max(MAX_TIME,endTime - startTime)
		LOCK.release()
	except:
		logger.exception("")
		return 0

def speedTestSocket(port):
	global EXIT_FLAG,LOCAL_PORT,MAX_TIME,TOTAL_RECEIVED,MAX_FILE_SIZE,DELTA_RECEIVED
	LOCAL_PORT = port
	useDefault = config["speedtestsocket"]["useDefault"]
	res = (False,"ALL","ALL")
	if (not useDefault):
		res = parseLocation()
	link = ""
	if (not useDefault and res[0]):
		isFound = False
		for _item in config["speedtestsocket"]["downloadLinks"]:
		#	logger.debug(_item)
			for code in _item["countries"]:
				if (res[1].strip() == code.strip()):
					link = _item["link"]
					MAX_FILE_SIZE = _item["fileSize"] * 1024 * 1024
					isFound = True
					logger.info("Server location : %s, using download link : %s" % (res[1],link))
					break
			if (_item["Continent"] != "" and _item["Continent"].strip() in res[2].strip()):
				link = _item["link"]
				logger.info("Server timezone : %s, using download link : %s" % (res[2],link))
				MAX_FILE_SIZE = _item["fileSize"] * 1024 * 1024
				isFound = True
			if (isFound):
				break
		if (not isFound):
			logger.warn("No download link match,using default.")
			link = config["speedtestsocket"]["defaultDownloadLink"]["link"]
			MAX_FILE_SIZE = config["speedtestsocket"]["defaultDownloadLink"]["fileSize"] * 1024 * 1024
	elif (useDefault):
		link = config["speedtestsocket"]["defaultDownloadLink"]["link"]
		MAX_FILE_SIZE = config["speedtestsocket"]["defaultDownloadLink"]["fileSize"] * 1024 * 1024
		logger.info("Using default download link %s" % link)
	else:
		logger.warn("Parse location failed, using default link.")
		link = config["speedtestsocket"]["defaultDownloadLink"]["link"]
		MAX_FILE_SIZE = config["speedtestsocket"]["defaultDownloadLink"]["fileSize"] * 1024 * 1024
	#return 0
	#logger.debug("Actived threads: %d" % threading.active_count())
	MAX_TIME = 0
	TOTAL_RECEIVED = 0
	EXIT_FLAG = False
	socks.set_default_proxy(socks.SOCKS5,"127.0.0.1",LOCAL_PORT)
	socket.socket = socks.socksocket
	for i in range(0,MAX_THREAD):
		nmsl = threading.Thread(target=speedTestThread,args=(link,))
		nmsl.start()
	maxSpeed = 0
	currentSpeed = 0
	OLD_RECEIVED = 0
	for i in range(1,21):
		time.sleep(0.5)
		LOCK.acquire()
	#	print("Delta Received : %d" % DELTA_RECEIVED)
		currentSpeed = (TOTAL_RECEIVED - OLD_RECEIVED) / 0.5
		OLD_RECEIVED = TOTAL_RECEIVED
		LOCK.release()
		maxSpeed = max(maxSpeed,currentSpeed)
	#	print("maxSpeed : %f" % maxSpeed)
		print("\r[" + "="*i + "> [%d%%/100%%] [%.2f MB/s] [%.2f MB/s]" % (int(i * 5),currentSpeed / 1024 / 1024,maxSpeed / 1024 / 1024),end='')
		if (EXIT_FLAG):
			break
	print("\r[" + "="*i + "] [100%%/100%%] [%.2f MB/s] [%.2f MB/s]" % (currentSpeed / 1024 / 1024,maxSpeed / 1024 / 1024),end='\n')
	EXIT_FLAG = True
	for i in range(0,10):
		time.sleep(0.1)
		if (MAX_TIME != 0):
			break
	if (MAX_TIME == 0):
		logger.error("Socket Test Error !")
		return(0,0)
	restoreSocket()
	return (TOTAL_RECEIVED / MAX_TIME,maxSpeed)

if (__name__ == "__main__"):
	print(speedTestSocket(1080)[0] / 1024 / 1024)

