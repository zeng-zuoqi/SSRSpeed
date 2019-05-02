#coding:utf-8

import logging
import yaml
import json

logger = logging.getLogger("Sub")

class ParserV2RayClash(object):
	def __init__(self):
		self.__clashVmessConfigs = []
		self.__decodedConfigs = []

	def __clashConfigigConvert(self,clashCfg):
		server = clashCfg["server"]
		remarks = clashCfg.get("name",server)
		group = "N/A"
		port = int(clashCfg["port"])
		uuid = clashCfg["uuid"]
		aid = int(clashCfg["alterId"])
		security = clashCfg.get("cipher","auto")
		tls = "tls" if (clashCfg.get("tls",False)) else "" #TLS
		allowInsecure = True if (clashCfg.get("skip-cert-verity",False)) else False
		net = clashCfg.get("network","tcp") #ws,tcp
		_type = clashCfg.get("type","none") #Obfs type
		wsHeader = clashCfg.get("ws-headers",{})
		host = wsHeader.get("Host","") # http host,web socket host,h2 host,quic encrypt method
		headers = {}
		for header in wsHeader.keys():
			if (header != "Host"):
				headers[header] = wsHeader[header]
		tlsHost = host
		path = clashCfg.get("ws-path","") #Websocket path, http path, quic encrypt key
		return {
			"remarks":remarks,
			"group":group,
			"server":server,
			"server_port":port,
			"id":uuid,
			"alterId":aid,
			"security":security,
			"type":_type,
			"path":path,
			"allowInsecure":allowInsecure,
			"network":net,
			"headers":headers,
			"tls-host":tlsHost,
			"host":host,
			"tls":tls
		}

	def parseGuiConfig(self,filename):
		with open(filename,"r+") as f:
			try:
				clashCfg = yaml.load(f)
			except:
				logger.exception("Not Clash config.")
				f.close()
				return False
			f.close()
		for cfg in clashCfg["Proxy"]:
			if (cfg.get("type","N/A").lower() == "vmess"):
				self.__clashVmessConfigs.append(cfg)
			else:
				logger.info("Config {}, type {} not support.".format(
					cfg["name"],
					cfg["type"]
					)
				)
		logger.debug("Read {} configs.".format(
			len(self.__clashVmessConfigs)
			)
		)
		for cfg in self.__clashVmessConfigs:
			self.__decodedConfigs.append(self.__clashConfigigConvert(cfg))
		return self.__decodedConfigs

if (__name__ == "__main__"):
	cvp = ParserV2RayClash()
	cvp.parseGuiConfig("./config.example.yml")


