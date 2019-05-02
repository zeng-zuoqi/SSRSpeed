#coding:utf-8

import urllib.parse
import logging
import json
logger = logging.getLogger("Sub")

from SSRSpeed.Utils.ConfigParser.BaseParser import BaseParser
from SSRSpeed.Utils.ConfigParser.V2RayParsers.ClashParser import ParserV2RayClash
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
			for h in config.get("headers",[]):
				webSocketSettings["headers"][h["header"]] = h["value"]
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
			tlsSettings["serverName"] = config["tls-host"]
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
		if (not cfg):
			pq = ParserQuantumult()
			cfg = pq.parseConfig(link)
		if (not cfg):
			logger.error("Parse link {} failed.".format(link))
			return None
		return self.__generateConfig(cfg)
	
	def readGuiConfig(self,filename):
		pv2rc = ParserV2RayClash()
		v2rnp = ParserV2RayN()
		rawGuiConfigs = pv2rc.parseGuiConfig(filename)
		if (rawGuiConfigs == False):
			logger.info("Not Clash Config.")
			rawGuiConfigs = v2rnp.parseGuiConfig(filename)
			if (rawGuiConfigs == False):
				logger.info("Not V2RayN Config.")
				logger.critical("Gui config parse failed.")
				rawGuiConfigs = []

		for _dict in rawGuiConfigs:	
			_cfg = self.__generateConfig(_dict)
			self._configList.append()
		logger.info("Read %d node(s)" % len(self._configList))
	#	logger.critical("V2RayN configuration file will be support soon.")
		



