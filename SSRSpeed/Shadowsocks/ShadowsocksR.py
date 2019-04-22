#coding:utf-8

import json
import subprocess
import requests
import socket
import platform
import signal
import os
import time
import sys
import logging
logger = logging.getLogger("Sub")

from SSRSpeed.Shadowsocks.ClientBase import Base

class ShadowsocksR(Base):
	def __init__(self):
		super(ShadowsocksR,self).__init__()
		self.__ssrAuth = ""

	def __winConf(self):
		with open("./clients/shadowsocksr-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
			f.close()
		self.__ssrAuth = tmpConf["localAuthPassword"]
		tmpConf["token"]["SpeedTest"] = "SpeedTest"
		tmpConf["localPort"] = self._localPort
		tmpConf["index"] = 0
		tmpConf["proxyRuleMode"] = 2
		tmpConf["configs"] = []
		for iitem in self._configList:
			try:
				iitem["protocolparam"] = iitem["protocol_param"]
			except KeyError:
				iitem["protocolparam"] = ""
			try:
				iitem["obfsparam"] = iitem["obfs_param"]
			except KeyError:
				iitem["obfsparam"] = ""
			tmpConf["configs"].append(iitem)
		with open("./clients/shadowsocksr-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))
			f.close()

	def getCurrrentConfig(self):
		param = {
			"app":"SpeedTest",
			"token":"SpeedTest",
			"action":"curConfig"
		}
		i = 0
		while (True):
			try:
				rep = requests.post("http://%s:%d/api?auth=%s" % (self._localAddress,self._localPort,self.__ssrAuth),params = param,timeout=5)
				break
			except (requests.exceptions.Timeout,socket.timeout):
				logger.error("Connect to ssr api server timeout.")
				i += 1
				if (i >= 4):
					return False
				continue
			#	self.nextWinConf()
			#	return False
			except:
				logger.exception("Get current config failed.")
				return False
		rep.encoding = "utf-8"
		if (rep.status_code == 200):
		#	logger.debug(rep.content)
			return rep.json()
		else:
			logger.error(rep.status_code)
			return False

	def nextWinConf(self):
		param = {
			"app":"SpeedTest",
			"token":"SpeedTest",
			"action":"nextConfig"
		}
		i = 0
		while(True):
			try:
				rep = requests.post("http://%s:%d/api?auth=%s" % (self._localAddress,self._localPort,self.__ssrAuth),params = param,timeout=5)
				break
			except (requests.exceptions.Timeout,socket.timeout):
				logger.error("Connect to ssr api server timeout.")
				i += 1
				if (i >= 4):
					return False
				continue
			#	return False
			except:
				logger.exception("Request next config failed.")
				return False
		if (rep.status_code == 403):
			return False
		else:
			return True

	def startClient(self,config = {}):
		if (self._process == None):
			if (self._checkPlatform() == "Windows"):
				self.__winConf()
			#	sys.exit(0)
				self._process = subprocess.Popen(["./clients/shadowsocksr-win/ShadowsocksR.exe"])
			elif(self._checkPlatform() == "Linux" or self._checkPlatform() == "MacOS"):
				self._config = config
				self._config["server_port"] = int(self._config["server_port"])
				with open("./config.json","w+",encoding="utf-8") as f:
					f.write(json.dumps(self._config))
					f.close()
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["python3","./clients/shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["python3","./clients/shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting ShadowsocksR-Python with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
		#	print(self.__process.returncode)
