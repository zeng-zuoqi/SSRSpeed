#coding:utf-8

import json
import requests
import subprocess
import platform
import signal
import socket
import os
import time
import sys
import urllib.parse
import logging
logger = logging.getLogger("Sub")

import b64plus

LOCAL_ADDRESS = "127.0.0.1"
LOCAL_PORT = 1087
TIMEOUT = 10

class Shadowsocks(object):
	def __init__(self):
		self._configList = []
		self._config = {}
		self._process = None
	
	def _checkPlatform(self):
		tmp = platform.platform()
		if ("Windows" in tmp):
			return "Windows"
		elif("Linux" in tmp):
			return "Linux"
		else:
			return "Unknown"

	def addConfig(self,configList):
		self._configList = configList

	def startClient(self,config={}):
		pass

	def getCurrrentConfig(self):
		pass
	
	def nextWinConf(self):
		pass

	def stopClient(self):
		if(self._process != None):
			if (self._checkPlatform() == "Windows"):
				self._process.terminate()
			else:
				self._process.send_signal(signal.SIGQUIT)
				self._process.send_signal(signal.SIGINT)
	#		print (self.__process.returncode)
			self._process = None
			logger.info("Shadowsocks(R) terminated.")
	#	self.__ssrProcess.terminate()

class SS(Shadowsocks):
	def __init__(self):
		super(SS,self).__init__()

	def getCurrrentConfig(self):
		with open("./shadowsocks-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
			f.close()
		curIndex = tmpConf["index"]
		return tmpConf["configs"][curIndex]

	def nextWinConf(self):
		self.stopClient()
		with open("./shadowsocks-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
			f.close()
		tmpConf["configs"] = []
		try:
			curConfig = self._configList.pop(0)
		except IndexError:
			return None
		tmpConf["configs"].append(curConfig)
	#	curIndex = tmpConf["index"] + 1
	#	maxIndex = len(tmpConf["configs"])
	#	if (curIndex >= maxIndex):
	#		return None
	#	tmpConf["index"] = curIndex
		with open("./shadowsocks-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))
			f.close()
		logger.info("Wait {} secs to start client.".format(3))
		for i in range(0,6):
			time.sleep(0.5)
		self.startClient({},True)
		return curConfig
	#	return tmpConf["configs"][curIndex]

	def __winConf(self):
		with open("./shadowsocks-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
			f.close()
		tmpConf["localPort"] = LOCAL_PORT
		tmpConf["index"] = 0
		tmpConf["global"] = False
		tmpConf["enabled"] = False
		tmpConf["configs"] = []
		for iitem in self._configList:
			tmpConf["configs"].append(iitem)
		with open("./shadowsocks-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))
			f.close()

	def startClient(self,config={},testing=False):
		if (self._process == None):
			if (self._checkPlatform() == "Windows"):
				if (not testing):
					self.__winConf()
			#	sys.exit(0)
				self._process = subprocess.Popen(["./shadowsocks-win/Shadowsocks.exe"])
			elif(self._checkPlatform() == "Linux"):
				self._config = config
				self._config["server_port"] = int(self._config["server_port"])
				with open("./config.json","w+",encoding="utf-8") as f:
					f.write(json.dumps(self._config))
					f.close()
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["ss-local","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["ss-local","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting ShadowsocksR-Python with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
	
class SSR(Shadowsocks):
	def __init__(self):
		super(SSR,self).__init__()
		self.__ssrAuth = ""

	def __winConf(self):
		with open("./shadowsocksr-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
			f.close()
		self.__ssrAuth = tmpConf["localAuthPassword"]
		tmpConf["token"]["SpeedTest"] = "SpeedTest"
		tmpConf["localPort"] = LOCAL_PORT
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
		with open("./shadowsocksr-win/gui-config.json","w+",encoding="utf-8") as f:
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
				rep = requests.post("http://%s:%d/api?auth=%s" % (LOCAL_ADDRESS,LOCAL_PORT,self.__ssrAuth),params = param,timeout=5)
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
				rep = requests.post("http://%s:%d/api?auth=%s" % (LOCAL_ADDRESS,LOCAL_PORT,self.__ssrAuth),params = param,timeout=5)
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
				self._process = subprocess.Popen(["./shadowsocksr-win/ShadowsocksR.exe"])
			elif(self._checkPlatform() == "Linux"):
				self._config = config
				self._config["server_port"] = int(self._config["server_port"])
				with open("./config.json","w+",encoding="utf-8") as f:
					f.write(json.dumps(self._config))
					f.close()
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["python3","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["python3","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting ShadowsocksR-Python with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
		#	print(self.__process.returncode)

class SSRParse(object):
	def __init__(self):
		self.__configList = []

	def parseLink(self,link):
		pass

	def __parseLink(self,link):
		_config = {
			"server":"",
			"server_port":-1,
			"method":"",
			"protocol":"",
			"obfs":"",
			"plugin":"",
			"password":"",
			"protocol_param":"",
			"obfsparam":"",
			"plugin_opts":"",
			"plugin_args":"",
			"remarks":"",
			"timeout":5,
			"group":"N/A"
		}
		serverType = ""
		if (link[:6] == "ssr://"):
			serverType = "SSR"
		elif(link[:5] == "ss://"):
		#	link = link[5:]
			serverType = "SS"
		if (serverType == ""):
			logger.error("Unsupport link : %s" % link)
			return None
			
		if (serverType == "SSR"):
			link = link[6:]
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
			_config["server"] = decoded1[5]
			_config["server_port"] = int(decoded1[4])
			_config["method"] = decoded1[2]
			_config["protocol"] = decoded1[3]
			_config["obfs"] = decoded1[1]
			_config["password"] = b64plus.decode(decoded1[0]).decode("utf-8")
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
		elif(serverType == "SS"):
			urlData = urllib.parse.unquote(link)
			urlResult = urllib.parse.urlparse(urlData)
			decoded = b64plus.decode(urlResult.netloc[:urlResult.netloc.find("@")]).decode("utf-8")
			method = decoded.split(":")[0]
			password = decoded.split(":")[1]
			addrPort = urlResult.netloc[urlResult.netloc.find("@") + 1:].split(":")
			remarks = urlResult.fragment
			if (len(addrPort) != 2):
				return None
			serverAddr = addrPort[0]
			serverPort = int(addrPort[1])

			queryResult = urlResult.query
		#	qsResult = urllib.parse.parse_qs(urlResult.query)
		#	plugin = qsResult.get("plugin")
			plugin = ""
			pluginOpts = ""
			group = "N/A"

			if ("group=" in queryResult):
				index1 = queryResult.find("group=") + 6
				index2 = queryResult.find("&",index1)
				group = b64plus.decode(queryResult[index1:index2 if index2 != -1 else None]).decode("utf-8")
			if ("plugin=" in queryResult):
				index1 = queryResult.find("plugin=") + 7
				index2 = queryResult.find(";",index1)
				plugin = queryResult[index1:index2]
				index3 = queryResult.find("&",index2)
				pluginOpts = queryResult[index2 + 1:index3 if index3 != -1 else None]

			_config["server"] = serverAddr
			_config["server_port"] = serverPort
			_config["method"] = method
			_config["password"] = password
			_config["group"] = group
			_config["remarks"] = remarks
			_config["plugin"] = plugin
			_config["plugin_opts"] = pluginOpts

		#	decoded1 = decoded.split("@")[1].split(":")[::-1]
		#	decoded2 = decoded.split("@")[0].split(":")
		#	if (len(decoded1) != 2):
		#		return None
		#		addr = ""
		#		for i in range(1,len(decoded1) - 1):
		#			addr += decoded1[i] + ":"
		#		addr += decoded1[len(decoded1) - 1]
		#		decoded1[1] = addr
		#	_config["server"] = decoded1[1]
		#	_config["port"] = int(decoded1[0])
		#	_config["method"] = decoded2[0]
		#	_config["password"] = decoded2[1]
		#	_config["group"] = "Shadowsocks"
		#	_config["remarks"] = _config["server"]
		#print(decoded)
		#print(decoded2)
		if (_config["remarks"] == ""):
			_config["remarks"] = _config["server"]
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
			#	print(item["remarks"])
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
					#	print(item["remarks"])
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
		#	print("%s - %s" % (item["group"],item["remarks"]))
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
		#	print(link)
			link = link.strip()
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
					"protocol":item.get("protocol",""),
					"protocol_param":item.get("protocolparam",""),
					"plugin":item.get("plugin",""),
					"obfs":item.get("obfs",""),
					"obfs_param":item.get("obfsparam",""),
					"plugin_opts":item.get("plugin_opts",""),
					"plugin_args":item.get("plugin_args",""),
					"remarks":item.get("remarks",item["server"]),
					"group":item.get("group","N/A"),
					"local_address":LOCAL_ADDRESS,
					"local_port":LOCAL_PORT,
					"timeout":TIMEOUT,
					"fast_open": False
				}
				if (_dict["remarks"] == ""):
					_dict["remarks"] = _dict["server"]
			#	logger.info(_dict["server"])
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

if (__name__ == "__main__"):
	ssrp = SSRParse()
	
	#print(ssrp.parseLink("ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNToxMjM0NTY@127.0.0.1:152/?plugin=obfs-local%3bobfs%3dtls%3bobfs-host%3d921aa27135.wns.windows.com&group=DlerCloud#Test"))



