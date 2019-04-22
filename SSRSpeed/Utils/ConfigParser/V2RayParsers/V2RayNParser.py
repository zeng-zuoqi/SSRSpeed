#coding:utf-8

import urllib.parse
import logging
import json
import copy
logger = logging.getLogger("Sub")

from SSRSpeed.Utils.ConfigParser.BaseParser import BaseParser
import SSRSpeed.Utils.ConfigParser.BaseConfig.V2RayBaseConfig as V2RayConfig
import SSRSpeed.Utils.b64plus as b64plus

class ParserV2RayN(object):
	def __init__(self):
		self.__baseV2RayConfig = V2RayConfig.getConfig()

	def parseConfig(self,rawLink):
		link = rawLink[8:]
		linkDecoded = b64plus.decode(link).decode("utf-8")
		try:
			_conf = json.loads(linkDecoded,encoding="utf-8")
		except json.JSONDecodeError:
			return None
		try:
			server = _conf["add"]
			port = int(_conf["port"])
			path = _conf.get("path","") #Websocket path, http path, quic encrypt key
			_type = _conf.get("type","none") #Obfs type
			uuid = _conf["id"]
			aid = int(_conf["aid"])
			net = _conf["net"]
			host = _conf.get("host","") # http host,web socket host,h2 host,quic encrypt method
			tls = _conf.get("tls","") #TLS
			security = _conf.get("security","auto")
			remarks = _conf.get("ps",server)
			logger.debug("Server : {},Port : {},Path : {},Type : {},UUID : {},AlterId : {},Network : {},Host : {},TLS : {},Remarks : {}".format(
				server,
				port,
				path,
				_type,
				uuid,
				aid,
				net,
				host,
				tls,
				remarks
			))
			_config = {
				"remarks":remarks,
				"server":server,
				"server_port":port,
				"id":uuid,
				"alterId":aid,
				"security":security,
				"type":_type,
				"path":path,
				"network":net,
				"host":host,
				"tls":tls
			}
			return _config
		except:
			logger.exception("Parse {} failed.".format(rawLink))
			return None

if (__name__ == "__main__"):
	pa = ParserV2RayN()
	
