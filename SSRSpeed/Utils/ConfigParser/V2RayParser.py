#coding:utf-8

import urllib.parse
import logging
import json
logger = logging.getLogger("Sub")

from SSRSpeed.Utils.ConfigParser.BaseParser import BaseParser
from SSRSpeed.Utils.ConfigParser.V2RayParsers.V2RayNParser import ParserV2RayN
from SSRSpeed.Utils.ConfigParser.V2RayParsers.QuantumultParser import ParserQuantumult
import SSRSpeed.Utils.ConfigParser.BaseConfig.V2RayBaseConfig as V2RayConfig
import SSRSpeed.Utils.b64plus as b64plus

class V2RayParser(BaseParser):
	def __init__(self):
		super(V2RayParser,self).__init__()

	def __generateConfig(self,config):
		_config = V2RayConfig.getConfig()

		_config["inbounds"][0]["listen"] = self._getLocalConfig()[0]
		_config["inbounds"][0]["port"] = self._getLocalConfig()[1]

		#Common
		_config["remarks"] = config["remarks"]
		_config["group"] = config.get("group","N/A")
		_config["server"] = config["server"]
		_config["server_port"] = config["server_port"]

		#stream settings
		streamSettings = _config["outbounds"][0]["streamSettings"]
		streamSettings["network"] = config["network"]
		if (config["network"] == "tcp"):
			if (config["type"] == "http"):
				tcpSettings = V2RayConfig.getTcpSettingsObject()
				tcpSettings["header"]["request"]["path"] = config["path"].split(",")
				tcpSettings["header"]["request"]["headers"]["Host"] = config["host"].split(",")
				streamSettings["tcpSettings"] = tcpSettings
		elif (config["network"] == "ws"):
			webSocketSettings = V2RayConfig.getWebSocketSettingsObject()
			webSocketSettings["path"] = config["path"]
			webSocketSettings["headers"]["Host"] = config["host"]
			streamSettings["wsSettings"] = webSocketSettings
		elif(config["network"] == "h2"):
			httpSettings = V2RayConfig.getHttpSettingsObject()
			httpSettings["path"] = config["path"]
			httpSettings["host"] = config["host"].split(",")
			streamSettings["httpSettings"] = httpSettings
		elif(config["network"] == "quic"):
			quicSettings = V2RayConfig.getQuicSettingsObject()
			quicSettings["security"] = config["host"]
			quicSettings["key"] = config["path"]
			quicSettings["header"]["type"] = config["type"]
			streamSettings["quicSettings"] = quicSettings

		streamSettings["security"] = config["tls"]
		if (config["tls"] == "tls"):
			tlsSettings = V2RayConfig.getTlsSettingsObject()
			tlsSettings["allowInsecure"] = True if (config.get("allowInsecure","false") == "true") else False
			tlsSettings["serverName"] = config["host"]
			streamSettings["tlsSettings"] = tlsSettings

		_config["outbounds"][0]["streamSettings"] = streamSettings

		outbound = _config["outbounds"][0]["settings"]["vnext"][0]
		outbound["address"] = config["server"]
		outbound["port"] = config["server_port"]
		outbound["users"][0]["id"] = config["id"]
		outbound["users"][0]["alterId"] = config["alterId"]
		outbound["users"][0]["security"] = config["security"]
		_config["outbounds"][0]["settings"]["vnext"][0] = outbound
		return _config

	def _parseLink(self,link):

		if (link[:8] != "vmess://"):
			logger.error("Unsupport link : %s" % link)
			return None
		pv2rn = ParserV2RayN()
		cfg = pv2rn.parseConfig(link)
	#	if (not cfg):
	#		pq = ParserQuantumult()
	#		cfg = pq.parseConfig(link)
		if (not cfg):
			logger.error("Parse link {} failed.".format(link))
			return None
		return self.__generateConfig(cfg)
	
	def readGuiConfig(self,filename):
		with open(filename,"r",encoding="utf-8") as f:
			config = json.load(f)
			f.close()
		subList = config.get("subItem",[])
		for item in config["vmess"]:
			_dict = {
				"server":item["address"],
				"server_port":item["port"],
				"id":item["id"],
				"alterId":item["alterId"],
				"security":item.get("security","auto"),
				"type":item.get("headerType","none"),
				"path":item.get("path",""),
				"network":item["network"],
				"host":item.get("requestHost",""),
				"tls":item.get("streamSecurity",""),
				"allowInsecure":item.get("allowInsecure",""),
				"subId":item.get("subid",""),
				"remarks":item.get("remarks",item["address"]),
				"group":"N/A"
			}
			subId = _dict["subId"]
			if (subId != ""):
				for sub in subList:
					if (subId == sub.get("id","")):
						_dict["group"] = sub.get("remarks","N/A")
			self._configList.append(self.__generateConfig(_dict))
		logger.info("Read %d node(s)" % len(self._configList))
	#	logger.critical("V2RayN configuration file will be support soon.")
		



