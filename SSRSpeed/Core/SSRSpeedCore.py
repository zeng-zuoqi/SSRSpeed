#coding:utf-8

import time
import logging
import json
import threading
import sys
import os

logger = logging.getLogger("Sub")

from SSRSpeed.Shadowsocks.Shadowsocks import Shadowsocks as SSClient
from SSRSpeed.Shadowsocks.ShadowsocksR import ShadowsocksR as SSRClient
from SSRSpeed.Shadowsocks.V2Ray import V2Ray as V2RayClient

from SSRSpeed.Utils.ConfigParser.ShadowsocksParser import ShadowsocksParser as SSParser
from SSRSpeed.Utils.ConfigParser.ShadowsocksRParser import ShadowsocksRParser as SSRParser
from SSRSpeed.Utils.ConfigParser.V2RayParser import V2RayParser

from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult

from SSRSpeed.SpeedTest.speedTest import SpeedTest
from SSRSpeed.Utils.checkRequirements import checkShadowsocks
from SSRSpeed.Utils.checkPlatform import checkPlatform
from SSRSpeed.Utils.sorter import Sorter

from config import config

class SSRSpeedCore(object):
	def __init__(self):
		
		self.testMethod = "SOCKET"
		self.proxyType = "SSR"
		self.webMode = False
		self.colors = "origin"
		self.sortMethod = ""
		self.subscriptionUrl = ""
		self.configFile = ""
		
		self.__client = None
		self.__parser = None
		self.__platformInfo = checkPlatform()
		self.__results = []
		self.__status = "stopped"

	def setup(self):
	#	self.__setProxyType()
		if (self.proxyType == "SSR"):
			self.__client = SSRClient()
			self.__parser = SSRParser()
		elif (self.proxyType == "SSR-C#"):
			self.__client = SSRClient()
			self.__client.useSsrCSharp = True
			self.__parser = SSRParser()
		elif(self.proxyType == "SS"):
			self.__client= SSClient()
			self.__parser = SSParser()
		elif(self.proxyType == "V2RAY"):
			self.__client = V2RayClient()
			self.__parser = V2RayParser()
		self.__readNodes()

	def clean(self):
		self.__results = []

	def getResults(self):
		return self.__results

	def getWebResults(self):
		r = {
			"status":"running" if (self.__status == "running") else "stopped",
			"results":self.__results
		}
		return json.dumps(r)
	
	def __readNodes(self):
		if (self.configFile):
			self.__parser.readGuiConfig(self.configFile)
		elif(self.subscriptionUrl):
			self.__parser.readSubscriptionConfig(self.subscriptionUrl)
		else:
			logger.critical("No config.")
			sys.exit(1)
	
	def filterNodes(self,fk=[],fgk=[],frk=[],ek=[],egk=[],erk=[]):
		self.__parser.excludeNode([],[],config["excludeRemarks"])
		self.__parser.filterNode(fk,fgk,frk)
		self.__parser.excludeNode(ek,egk,erk)
		print(len(self.__parser.getAllConfig()))
		self.__parser.printNode()
		logger.info("{} node(s) will be test.".format(len(self.__parser.getAllConfig())))

	def importAndExport(self,filename,split=0):
		self.__results = importResult.importResult(filename)
		self.__exportResult(split,2)
		self.__results = []

	def __exportResult(self,split = 0,exportType= 0):
		er = ExportResult()
		er.setColors(self.colors)
		if (not exportType):
			er.exportAsJson(self.__results)
		sorter = Sorter()
		result = sorter.sortResult(self.__results,self.sortMethod)
		if (split > 0):
			i = 0
			id = 1
			while (i < len(result)):
				_list = []
				for j in range(0,split):
					_list.append(result[i])
					i += 1
					if (i >= len(result)):
						break
				er.exportAsPng(_list,id)
				id += 1
		else:
			er.exportAsPng(result)

	def startTcpingOnlyTest(self):
		logger.info("Test mode : tcp ping only.")
		config = self.__parser.getNextConfig()
		st = SpeedTest()
		self.__status = "running"
		while (True):
			if(not config):
				break
			_item = {}
			_item["group"] = config["group"]
			_item["remarks"] = config["remarks"]
			config["server_port"] = int(config["server_port"])
			st = SpeedTest()
			latencyTest = st.tcpPing(config["server"],config["server_port"])
			_item["loss"] = 1 - latencyTest[1]
			_item["ping"] = latencyTest[0]
			_item["dspeed"] = -1
			_item["maxDSpeed"] = -1
			self.__results.append(_item)
			logger.info("%s - %s - Loss:%s%% - TCP_Ping:%d" % (_item["group"],_item["remarks"],_item["loss"] * 100,int(_item["ping"] * 1000)))
			config = self.__parser.getNextConfig()
			if (config == None):break
		self.__status = "stopped"
		self.__exportResult()

	def startFullTest(self):
		logger.info("Test mode : speed and tcp ping.Test method : %s." % self.testMethod)
		configs = self.__parser.getAllConfig()
		totalConfCount = len(configs)
		config = self.__parser.getNextConfig()
		time.sleep(2)
		curConfCount = 0
		self.__status = "running"
		while(True):
			if(not config):
				break
			_item = {}
			_item["group"] = config.get("group","N/A")
			_item["remarks"] = config.get("remarks",config["server"])
			config["server_port"] = int(config["server_port"])
			self.__client.startClient(config)
			curConfCount += 1
			logger.info("Starting test for %s - %s [%d/%d]" % (_item["group"],_item["remarks"],curConfCount,totalConfCount))
			time.sleep(1)
			try:
				st = SpeedTest()
				latencyTest = st.tcpPing(config["server"],config["server_port"])
				if (int(latencyTest[0] * 1000) != 0):
					time.sleep(1)
					testRes = st.startTest(self.testMethod)
					if (int(testRes[0]) == 0):
						logger.warn("Re-testing node.")
						testRes = st.startTest(self.testMethod)
					_item["dspeed"] = testRes[0]
					_item["maxDSpeed"] = testRes[1]
					_item["rawSocketSpeed"] = []
					try:
						_item["rawSocketSpeed"] = testRes[2]
					except:
						pass
					time.sleep(1)
				else:
					_item["dspeed"] = 0
					_item["maxDSpeed"] = 0
					_item["rawSocketSpeed"] = []
				self.__client.stopClient()
				time.sleep(1)
				_item["loss"] = 1 - latencyTest[1]
				_item["ping"] = latencyTest[0]
			#	_item["gping"] = st.googlePing()
				_item["gping"] = 0
				self.__results.append(_item)
				logger.info(
					"%s - %s - Loss:%s%% - TCP_Ping:%d - AvgSpeed:%.2fMB/s - MaxSpeed:%.2fMB/s" % (
						_item["group"],
						_item["remarks"],
						_item["loss"] * 100,
						int(_item["ping"] * 1000),
						_item["dspeed"] / 1024 / 1024,
						_item["maxDSpeed"] / 1024 / 1024
						)
					)
			except Exception:
				self.__client.stopClient()
				logger.exception("")
			config = self.__parser.getNextConfig()
			if (config == None):
				break
		self.__status = "stopped"
		self.__exportResult()


