#coding:utf-8

import json
import requests
import platform
import os
import time
import sys
import urllib.parse
import logging
logger = logging.getLogger("Sub")

import SSRSpeed.Utils.b64plus as b64plus

LOCAL_ADDRESS = "127.0.0.1"
LOCAL_PORT = 1087
TIMEOUT = 10

class ShadowsocksParser(object):
	def __init__(self):
		self.__configList = []

	def __parseLink(self,link):
		_config = {
			"server":"",
			"server_port":-1,
			"method":"",
			"plugin":"",
			"password":"",
			"plugin_opts":"",
			"plugin_args":"",
			"remarks":"",
			"timeout":TIMEOUT,
			"group":"N/A"
		}
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

		if (_config["remarks"] == ""):
			_config["remarks"] = _config["server"]
		_config["local_port"] = LOCAL_PORT
		_config["local_address"] = LOCAL_ADDRESS
		_config["timeout"] = TIMEOUT
		_config["fast_open"] = False
		return _config

			
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


