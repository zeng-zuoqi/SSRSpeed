#coding:utf-8

import urllib.parse
import logging
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



