#coding:utf-8

import json
import requests
import subprocess
import platform
import signal
import os
import sys
import logging
logger = logging.getLogger("Sub")

import b64plus

LOCAL_ADDRESS = "127.0.0.1"
LOCAL_PORT = 1087
TIMEOUT = 10

class SSR(object):
	def __init__(self):
		self.__configList = []
		self.__config = {}
		self.__process = None
		self.__ssrAuth = ""

	def __checkPlatform(self):
		tmp = platform.platform()
		if ("Windows" in tmp):
			return "Windows"
		elif("Linux" in tmp):
			return "Linux"
		else:
			return "Unknown"

	def __ssrWinConf(self):
		with open("./shadowsocksr-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
			f.close()
		self.__ssrAuth = tmpConf["localAuthPassword"]
		tmpConf["token"]["SpeedTest"] = "SpeedTest"
		tmpConf["localPort"] = LOCAL_PORT
		tmpConf["index"] = 0
		tmpConf["configs"] = []
		for iitem in self.__configList:
			iitem["protocolparam"] = iitem["protocol_param"]
			iitem["obfsparam"] = iitem["obfs_param"]
			tmpConf["configs"].append(iitem)
		with open("./shadowsocksr-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))
			f.close()

	def getCurrrentConfig(self):
		param = {
			"app":"SpeedTest",
			"token":"SpeedTest",
			"action":"curConfig"
		}
		rep = requests.post("http://%s:%d/api?auth=%s" % (LOCAL_ADDRESS,LOCAL_PORT,self.__ssrAuth),params = param)
		rep.encoding = "utf-8"
		if (rep.status_code == 200):
		#	logger.debug(rep.content)
			return rep.json()
		else:
			return False

	def nextWinConf(self):
		param = {
			"app":"SpeedTest",
			"token":"SpeedTest",
			"action":"nextConfig"
		}
		rep = requests.post("http://%s:%d/api?auth=%s" % (LOCAL_ADDRESS,LOCAL_PORT,self.__ssrAuth),params = param)
		if (rep.status_code == 403):
			return False
		else:
			return True

	def addConfig(self,configList):
		self.__configList = configList

	def startSsr(self,config = {}):
		if (self.__process == None):
			if (self.__checkPlatform() == "Windows"):
				self.__ssrWinConf()
				self.__process = subprocess.Popen(["./shadowsocksr-win/ShadowsocksR.exe"])
			elif(self.__checkPlatform() == "Linux"):
				self.__config = config
				self.__config["server_port"] = int(self.__config["server_port"])
				with open("./config.json","w+",encoding="utf-8") as f:
					f.write(json.dumps(self.__config))
					f.close()
				if (logger.level == logging.DEBUG):
					self.__process = subprocess.Popen(["python3","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()])
				else:
					self.__process = subprocess.Popen(["python3","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting ShadowsocksR-Python with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
			

		#	print(self.__process.returncode)


	def stopSsr(self):
		if(self.__process != None):
			if (self.__checkPlatform() == "Windows"):
				self.__process.terminate()
			else:
				self.__process.send_signal(signal.SIGQUIT)
	#		print (self.__process.returncode)
			self.__process = None
			logger.info("ShadowsocksR terminated.")
	#	self.__ssrProcess.terminate()


class SSRParse(object):
	def __init__(self):
		self.__configList = []

	def __parseLink(self,link):
		decoded = b64plus.decode(link).decode("utf-8")
		decoded1 = decoded.split("/?")[0].split(":")[::-1]
		if (len(decoded1) != 6):
			return None
			addr = ""
			for i in range(5,len(decoded1) - 1):
				addr += decoded1[i] + ":"
			addr += decoded1[len(decoded1) - 1]
			decoded1[5] = addr
		decoded2 = decoded.split("/?")[1].split("&")
	#	print(decoded1)
	#	print(decoded2)
		_config = {
			"server":decoded1[5],
			"server_port":int(decoded1[4]),
			"method":decoded1[2],
			"protocol":decoded1[3],
			"obfs":decoded1[1],
			"password":b64plus.decode(decoded1[0]).decode("utf-8"),
			"protocol_param":"",
			"obfsparam":"",
			"remarks":"",
			"group":""
		}
	#	logger.debug(decoded2)
		for ii in decoded2:
			if ("obfsparam" in ii):
				_config["obfs_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif ("protocolparam" in ii or "protoparam" in ii):
				_config["protocol_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif ("remarks" in ii):
				_config["remarks"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif("group" in ii):
				_config["group"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
		_config["local_port"] = LOCAL_PORT
		_config["local_address"] = LOCAL_ADDRESS
		_config["timeout"] = TIMEOUT
		_config["fast_open"] = False
		return _config

	def __checkInList(self,item,_list):
		for _item in _list:
			if (_item["group"] == item["group"] and _item["remarks"] == item["remarks"]):
				return True
		return False

	def __filterGroup(self,gkwl):
		_list = []
		if (gkwl == []):return
		for gkw in gkwl:
			for item in self.__configList:
				if (self.__checkInList(item,_list)):continue
				if (gkw in item["group"]):
					_list.append(item)
		self.__configList = _list

	def __filterRemark(self,rkwl):
		_list = []
		if (rkwl == []):return
		for rkw in rkwl:
			for item in self.__configList:
				if (self.__checkInList(item,_list)):continue
				if (rkw in item["remarks"]):
					_list.append(item)
		self.__configList = _list

	def filterNode(self,kwl = [],gkwl = [],rkwl = []):
		_list = []
	#	print(len(self.__configList))
	#	print(type(kwl))
		if (kwl != []):
			for kw in kwl:
				for item in self.__configList:
					if (self.__checkInList(item,_list)):continue
					if ((kw in item["group"]) or (kw in item["remarks"])):
						_list.append(item)
			self.__configList = _list
		self.__filterGroup(gkwl)
		self.__filterRemark(rkwl)

	def __excludeGroup(self,gkwl):
		if (gkwl == []):return
		for gkw in gkwl:
			_list = []
			for item in self.__configList:
				if (self.__checkInList(item,_list)):continue
				if (gkw not in item["group"]):
					_list.append(item)
			self.__configList = _list

	def __excludeRemark(self,rkwl):
		if (rkwl == []):return
		for rkw in rkwl:
			_list = []
			for item in self.__configList:
				if (self.__checkInList(item,_list)):continue
				if (rkw not in item["remarks"]):
					_list.append(item)
			self.__configList = _list

	def excludeNode(self,kwl = [],gkwl = [],rkwl = []):
	#	print((kw,gkw,rkw))
	#	print(len(self.__configList))
		if (kwl != []):
			for kw in kwl:
				_list = []
				for item in self.__configList:
					if (self.__checkInList(item,_list)):continue
					if ((kw not in item["group"]) and (kw not in item["remarks"])):
						_list.append(item)
				self.__configList = _list
		self.__excludeGroup(gkwl)
		self.__excludeRemark(rkwl)

	def printNode(self):
		for item in self.__configList:
			#print("%s - %s" % (item["group"],item["remarks"]))
			logger.info("%s - %s" % (item["group"],item["remarks"]))

	def readSubscriptionConfig(self,url):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header)
		rep.encoding = "utf-8"
		rep = rep.content.decode("utf-8")
		linksArr = (b64plus.decode(rep).decode("utf-8")).split("\n")
		for link in linksArr:
			link = link.strip()
			if (link[:6] != "ssr://"):continue
			link = link[6:]
			cfg = self.__parseLink(link)
			if (cfg):
				self.__configList.append(cfg)

		logger.info("Read %d node(s)" % len(self.__configList))
			
	def readGuiConfig(self,filename):
		with open(filename,"r",encoding="utf-8") as f:
			for item in json.load(f)["configs"]:
				_dict = {
					"server":item["server"],
					"server_port":int(item["server_port"]),
					"password":item["password"],
					"method":item["method"],
					"protocol":item["protocol"],
					"protocol_param":item["protocolparam"],
					"obfs":item["obfs"],
					"obfs_param":item["obfsparam"],
					"remarks":item["remarks"],
					"group":item["group"],
					"local_address":LOCAL_ADDRESS,
					"local_port":LOCAL_PORT,
					"timeout":TIMEOUT,
					"fast_open": False
				}
				self.__configList.append(_dict)
			f.close()

		logger.info("Read %d node(s)" % len(self.__configList))

	def getAllConfig(self):
		return self.__configList

	def getNextConfig(self):
		if (self.__configList != []):
			return self.__configList.pop(0)
		else:
			return None




