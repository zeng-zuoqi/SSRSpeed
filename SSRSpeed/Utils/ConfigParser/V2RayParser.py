#coding:utf-8

import urllib.parse
import logging
import copy
logger = logging.getLogger("Sub")

from SSRSpeed.Utils.ConfigParser.BaseParser import BaseParser
from SSRSpeed.Utils.ConfigParser.V2RayParsers.V2RayNParser import ParserV2RayN
import SSRSpeed.Utils.ConfigParser.BaseConfig.V2RayBaseConfig as V2RayConfig
import SSRSpeed.Utils.b64plus as b64plus

class V2RayParser(BaseParser):
	def __init__(self):
		super(V2RayParser,self).__init__()

	def __generateConfig(self,config):
		_config = V2RayConfig.getConfig()
		_config["remarks"] = config["remarks"]
		_config["server"] = config["server"]
		_config["server_port"] = config["server_port"]
		_config["outbounds"][0]["streamSettings"]["network"] = config["network"]
		_config["outbounds"][0]["streamSettings"]["security"] = config["security"]
		outbound = _config["outbounds"][0]["settings"]["vnext"][0]
		outbound["address"] = config["server"]
		outbound["port"] = config["server_port"]
		outbound["users"][0]["id"] = config["id"]
		outbound["users"][0]["alterId"] = config["alterId"]
	#	outbound["users"][0]["security"] = config["security"]
		_config["outbounds"][0]["settings"]["vnext"][0] = outbound
		return _config

	def _parseLink(self,link):
		_config = copy.deepcopy(self._baseV2RayConfig)

		if (link[:8] != "vmess://"):
			logger.error("Unsupport link : %s" % link)
			return None
		pv2rn = ParserV2RayN()
		cfg = pv2rn.parseConfig(link)
		if (not cfg):
			pass
		if (not cfg):
			logger.error("Parse link {} failed.".format(link))
			return None
		return self.__generateConfig(cfg)
		



