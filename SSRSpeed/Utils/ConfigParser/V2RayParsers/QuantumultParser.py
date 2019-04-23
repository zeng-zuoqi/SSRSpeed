#coding:utf-8

import urllib.parse
import logging
import json
logger = logging.getLogger("Sub")

import SSRSpeed.Utils.b64plus as b64plus

class ParserQuantumult(object):
	def __init__(self):
		pass

	def parseConfig(self,rawLink):
		link = rawLink[8:]
		linkDecoded = b64plus.decode(link).decode("utf-8")
		try:
			linkSplited = linkDecoded.split(",")
			remarks = linkSplited[0].split(" = ")[0]
			server = linkSplited[1]
			port = int(linkSplited[2])
			method = linkSplited[3]
			uuid = linkSplited[4]
			group = linkSplited[5].split("=")[1]
			tls = "none"
			if (linkSplited[6].split("=")[1] == "true"):
				tls = "tls"
			
			path = _conf.get("path","") #Websocket path, http path, quic encrypt key
			_type = _conf.get("type","none") #Obfs type
			uuid = _conf["id"]
			aid = int(_conf["aid"])
			net = _conf["net"]
			host = _conf.get("host","") # http host,web socket host,h2 host,quic encrypt method
			tls = _conf.get("tls","") #TLS
			security = _conf.get("security","auto")
			logger.debug("Server : {},Port : {},Path : {},Type : {},UUID : {},AlterId : {},Network : {},Host : {},TLS : {},Remarks : {},group={}".format(
				server,
				port,
				path,
				_type,
				uuid,
				aid,
				net,
				host,
				tls,
				remarks,
				group
			))
			_config = {
				"remarks":remarks,
				"group":group,
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
			logger.exception("Parse {} failed.(Quantumult Method)".format(rawLink))
			return None

if (__name__ == "__main__"):
	pa = ParserQuantumult()
	
