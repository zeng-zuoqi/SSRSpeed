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

from SSRSpeed.SpeedTest.SpeedTestCore import SpeedTestCore
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
		self.__stc = None
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
		if (self.__stc):
			self.__stc.resetStatus()

	def getResults(self):
		return self.__results

	def getWebStatus(self):
		if (self.__status == "running"):
			if (self.__stc):
				status = "running"
			else:
				status = "pending"
		else:
			status = self.__status
		r = {
			"status":status,
			"current":self.__stc.getCurrent() if (self.__stc) else {},
			"results":self.__stc.getResult() if (self.__stc) else []
		}
		return json.dumps(r)
	
	def __readNodes(self):
		self.__parser.cleanConfigs()
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
		er.export(self.__results,split,exportType,self.sortMethod)

	def startTcpingOnlyTest(self):
		self.__stc = SpeedTestCore(self.__parser,self.__client,self.testMethod)
		self.__status = "running"
		self.__stc.tcpingOnly()
		self.__results = self.__stc.getResult()
		self.__status = "stopped"
		self.__exportResult()

	def startFullTest(self):
		self.__stc = SpeedTestCore(self.__parser,self.__client,self.testMethod)
		self.__status = "running"
		self.__stc.fullTest()
		self.__results = self.__stc.getResult()
		self.__status = "stopped"
		self.__exportResult()


