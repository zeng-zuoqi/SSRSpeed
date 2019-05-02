#coding:utf-8

import logging
import time

logger = logging.getLogger("Sub")

from SSRSpeed.SpeedTest.speedTest import SpeedTest

class SpeedTestCore(object):
	def __init__(self,parser,client,method = "SOCKET"):
		self.__parser = parser
		self.__client = client
		self.__testMethod = method
		self.__results = []
		self.__current = {}

	def resetStatus(self):
		self.__results = []
		self.__current = {}

	def getResult(self):
		return self.__results
	
	def getCurrent(self):
		return self.__current
	
	def tcpingOnly(self):
		logger.info("Test mode : tcp ping only.")
		self.__results = []
		config = self.__parser.getNextConfig()
		st = SpeedTest()
		while (True):
			if (config == None):break
			_item = {}
			_item["group"] = config["group"]
			_item["remarks"] = config["remarks"]
			self.__current = _item
			config["server_port"] = int(config["server_port"])
			st = SpeedTest()
			latencyTest = st.tcpPing(config["server"],config["server_port"])
			_item["loss"] = 1 - latencyTest[1]
			_item["ping"] = latencyTest[0]
			_item["dspeed"] = -1
			_item["maxDSpeed"] = -1
			_item["trafficUsed"] = -1
			_item["rawSocketSpeed"] = []
			self.__results.append(_item)
			logger.info("%s - %s - Loss:%s%% - TCP_Ping:%d" % (_item["group"],_item["remarks"],_item["loss"] * 100,int(_item["ping"] * 1000)))
			config = self.__parser.getNextConfig()
		self.__current = {}

	def fullTest(self):
		logger.info("Test mode : speed and tcp ping.Test method : {}.".format(self.__testMethod))
		self.__results = []
		configs = self.__parser.getAllConfig()
		totalConfCount = len(configs)
		config = self.__parser.getNextConfig()
		time.sleep(2)
		curConfCount = 0
		while(True):
			if(not config):break
			_item = {}
			_item["group"] = config.get("group","N/A")
			_item["remarks"] = config.get("remarks",config["server"])
			config["server_port"] = int(config["server_port"])
			self.__client.startClient(config)
			curConfCount += 1
			logger.info("Starting test for {} - {} [{}/{}]".format(_item["group"],_item["remarks"],curConfCount,totalConfCount))
			self.__current = _item
			time.sleep(1)
			try:
				st = SpeedTest()
				latencyTest = st.tcpPing(config["server"],config["server_port"])
				if (int(latencyTest[0] * 1000) != 0):
					time.sleep(1)
					testRes = st.startTest(self.__testMethod)
					if (int(testRes[0]) == 0):
						logger.warn("Re-testing node.")
						testRes = st.startTest(self.__testMethod)
					_item["dspeed"] = testRes[0]
					_item["maxDSpeed"] = testRes[1]
					_item["trafficUsed"] = -1
					_item["rawSocketSpeed"] = []
					try:
						_item["trafficUsed"] = testRes[3]
						_item["rawSocketSpeed"] = testRes[2]
					except:
						pass
					time.sleep(1)
				else:
					_item["dspeed"] = 0
					_item["maxDSpeed"] = 0
					_item["trafficUsed"] = -1
					_item["rawSocketSpeed"] = []
				self.__client.stopClient()
				time.sleep(1)
				_item["loss"] = 1 - latencyTest[1]
				_item["ping"] = latencyTest[0]
			#	_item["gping"] = st.googlePing()
				_item["gping"] = 0
				self.__results.append(_item)
				logger.info(
					"{} - {} - Loss:{}%% - TCP_Ping:{} - AvgSpeed:{:.2f}MB/s - MaxSpeed:{:.2f}MB/s".format(
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
		self.__current = {}

