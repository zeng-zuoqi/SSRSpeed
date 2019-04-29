#coding:utf-8

import urllib.parse
import logging
import requests
import json
logger = logging.getLogger("Sub")

from SSRSpeed.Utils.ConfigParser.BaseParser import BaseParser
import SSRSpeed.Utils.b64plus as b64plus

class ShadowsocksParser(BaseParser):
	def __init__(self):
		super(ShadowsocksParser,self).__init__()

	def _parseLink(self,link):
		_config = self._getShadowsocksBaseConfig()

		if (link[:5] != "ss://"):
			logger.error("Unsupport link : %s" % link)
			return None

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

		if (_config["remarks"] == ""):
			_config["remarks"] = _config["server"]
	#	print(_config["remarks"])
		return _config

	def readSubscriptionConfig(self,url):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header)
		rep.encoding = "utf-8"
		rep = rep.content.decode("utf-8")
		if (rep[:6] == "ssd://"):
			self.__parseShadowsocksDSubscription(rep[6:])
			return
		linksArr = (b64plus.decode(rep).decode("utf-8")).split("\n")
		for link in linksArr:
			link = link.strip()
		#	print(link)
			cfg = self._parseLink(link)
			if (cfg):
			#	print(cfg["remarks"])
				self._configList.append(cfg)
		logger.info("Read %d node(s)" % len(self._configList))

	def __parseShadowsocksDSubscription(self,ssdSubs):
		ssdConfig = json.loads(b64plus.decode(ssdSubs).decode("utf-8"))
		group = ssdConfig.get("airport","N/A")
		defaultPort = int(ssdConfig["port"])
		defaultMethod = ssdConfig["encryption"]
		defaultPassword = ssdConfig["password"]
		defaultPlugin = ssdConfig.get("plugin","")
		defaultPluginOpts = ssdConfig.get("plugin_options","")
		servers = ssdConfig["servers"]
		for server in servers:
			_config = self._getShadowsocksBaseConfig()
			_config["server"] = server["server"]
			_config["server_port"] = int(server.get("port",defaultPort))
			_config["method"] = server.get("encryption",defaultMethod)
			_config["password"] = server.get("password",defaultPassword)
			_config["plugin"] = server.get("plugin",defaultPlugin)
			_config["plugin_opts"] = server.get("plugin_options",defaultPluginOpts)
			_config["group"] = group
			_config["remarks"] = server.get("remarks",server["server"])
			self._configList.append(_config)
		logger.info("Read %d node(s)" % len(self._configList))



