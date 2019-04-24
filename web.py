#coding:utf-8

import time
import sys
import os
import json
import threading
import platform
from optparse import OptionParser
import logging

from SSRSpeed.Shadowsocks.Shadowsocks import Shadowsocks as SSClient
from SSRSpeed.Shadowsocks.ShadowsocksR import ShadowsocksR as SSRClient
from SSRSpeed.Shadowsocks.V2Ray import V2Ray as V2RayClient
from SSRSpeed.SpeedTest.speedTest import SpeedTest
from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult
from SSRSpeed.Utils.checkPlatform import checkPlatform
from SSRSpeed.Utils.ConfigParser.ShadowsocksParser import ShadowsocksParser as SSParser
from SSRSpeed.Utils.ConfigParser.ShadowsocksRParser import ShadowsocksRParser as SSRParser
from SSRSpeed.Utils.ConfigParser.V2RayParser import V2RayParser
from SSRSpeed.Utils.checkRequirements import checkShadowsocks

from config import config

if (not os.path.exists("./logs/")):
	os.mkdir("./logs/")
if (not os.path.exists("./results/")):
	os.mkdir("./results/")

loggerList = []
loggerSub = logging.getLogger("Sub")
logger = logging.getLogger(__name__)
loggerList.append(loggerSub)
loggerList.append(logger)

formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s")
fileHandler = logging.FileHandler("./logs/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log",encoding="utf-8")
fileHandler.setFormatter(formatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)

VERSION = "2.3.0-alpha"

def setOpts(parser):
	parser.add_option(
		"-d","--daemon",
		action="store_true",
		dest="daemon_mode",
		default=False,
		help="Run web server in daemon mode."
		)
	
	parser.add_option(
		"-l","--listen",
		action="store",
		dest="local_address",
		default="127.0.0.1",
		help="Web server listen address."
		)
	
	parser.add_option(
		"-p","--port",
		action="store",
		dest="local_port",
		default="19198",
		help="Web server listen port."
		)
	
	parser.add_option(
		"--debug",
		action="store_true",
		dest="debug",
		default=False,
		help="Run program in debug mode."
		)
	parser.add_option(
		"--paolu",
		action="store_true",
		dest="paolu",
		default=False,
		help="如题"
		)

def export(Result,split = 0,exportType= 0,color="origin"):
	er = ExportResult()
	er.setColors(color)
	if (not exportType):
		er.exportAsJson(Result)
		return
	if (split > 0):
		i = 0
		id = 1
		while (i < len(Result)):
			_list = []
			for j in range(0,split):
				_list.append(Result[i])
				i += 1
				if (i >= len(Result)):
					break
			er.exportAsPng(_list,id)
			id += 1
	else:
		er.exportAsPng(Result)

if (__name__ == "__main__"):

	DEBUG = False
	CONFIG_LOAD_MODE = 0 #0 for import result,1 for guiconfig,2 for subscription url
	CONFIG_FILENAME = ""
	CONFIG_URL = ""
	IMPORT_FILENAME = ""
	FILTER_KEYWORD = []
	FILTER_GROUP_KRYWORD = []
	FILTER_REMARK_KEYWORD = []
	EXCLUDE_KEYWORD = []
	EXCLUDE_GROUP_KEYWORD = []
	EXCLUDE_REMARK_KEWORD = []
	TEST_METHOD = ""
	TEST_MODE = ""
	PROXY_TYPE = "SSR"
	SPLIT_CNT = 0
	SORT_METHOD = ""
	SKIP_COMFIRMATION = False
	RESULT_IMAGE_COLOR = "origin"

	parser = OptionParser(usage="Usage: %prog [options] arg1 arg2...",version="SSR Speed Tool " + VERSION)
	setOpts(parser)
	(options,args) = parser.parse_args()

	if (options.paolu):
		for root, dirs, files in os.walk(".", topdown=False):
			for name in files:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
			for name in dirs:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
		sys.exit(0)

	print("****** Import Hint 重要提示******")
	print("Before you publicly release your speed test results, be sure to ask the node owner if they agree to the release to avoid unnecessary disputes.")
	print("在您公开发布测速结果之前请务必征得节点拥有者的同意,以避免一些令人烦恼的事情")
	print("*********************************")
	input("Press ENTER to conitnue or Crtl+C to exit.")

	if (options.debug):
		DEBUG = options.debug
		for item in loggerList:
			item.setLevel(logging.DEBUG)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)
	else:
		for item in loggerList:
			item.setLevel(logging.INFO)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)

	if (logger.level == logging.DEBUG):
		logger.debug("Program running in debug mode")

	if (len(sys.argv) == 1):
		parser.print_help()
		exit(0)

	if (PROXY_TYPE == "SSR"):
		client = SSRClient()
		uConfigParser = SSRParser()
	elif(PROXY_TYPE == "SS"):
		client = SSClient()
		uConfigParser = SSParser()
	elif(PROXY_TYPE == "V2RAY"):
		client = V2RayClient()
		uConfigParser = V2RayParser()

	if (CONFIG_LOAD_MODE == 1):
		uConfigParser.readGuiConfig(CONFIG_FILENAME)
	else:
		uConfigParser.readSubscriptionConfig(CONFIG_URL)
	uConfigParser.excludeNode([],[],config["excludeRemarks"])
	uConfigParser.filterNode(FILTER_KEYWORD,FILTER_GROUP_KRYWORD,FILTER_REMARK_KEYWORD)
	uConfigParser.excludeNode(EXCLUDE_KEYWORD,EXCLUDE_GROUP_KEYWORD,EXCLUDE_REMARK_KEWORD)
	uConfigParser.printNode()
	logger.info("{} node(s) will be test.".format(len(uConfigParser.getAllConfig())))

	if (TEST_MODE == "TCP_PING"):
		logger.info("Test mode : tcp ping only.")
	#	print("Your test mode is tcp ping only.")
	else:
		logger.info("Test mode : speed and tcp ping.\nTest method : %s." % TEST_METHOD)
	#	print("Your test mode : speed and tcp ping.\nTest method : %s." % TEST_METHOD)

	if (not SKIP_COMFIRMATION):
		
		ans = input("Before the test please confirm the nodes,Ctrl-C to exit. (Y/N)")
		if (ans == "Y"):
			pass
		else:
			sys.exit(0)

	'''
		{
			"group":"",
			"remarks":"",
			"loss":0,
			"ping":0.01,
			"gping":0.01,
			"dspeed":10214441 #Bytes
		}
	'''
	Result = []
	retryList = []
	retryConfig = []
	retryMode = False
	totalConfCount = 0
	curConfCount = 0

	pfInfo = checkPlatform()

	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	if (TEST_MODE == "ALL"):
		configs = uConfigParser.getAllConfig()
		totalConfCount = len(configs)
		config = uConfigParser.getNextConfig()
		time.sleep(2)
		while(True):
			_item = {}
			_item["group"] = config.get("group","N/A")
			_item["remarks"] = config.get("remarks",config["server"])
			config["server_port"] = int(config["server_port"])
			client.startClient(config)
			curConfCount += 1
			logger.info("Starting test for %s - %s [%d/%d]" % (_item["group"],_item["remarks"],curConfCount,totalConfCount))
			time.sleep(1)
			try:
				st = SpeedTest()
				latencyTest = st.tcpPing(config["server"],config["server_port"])
				if (int(latencyTest[0] * 1000) != 0):
					time.sleep(1)
					testRes = st.startTest(TEST_METHOD)
					if (int(testRes[0]) == 0):
						logger.warn("Re-testing node.")
						testRes = st.startTest(TEST_METHOD)
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
				client.stopClient()
				time.sleep(1)
				_item["loss"] = 1 - latencyTest[1]
				_item["ping"] = latencyTest[0]
			#	_item["gping"] = st.googlePing()
				_item["gping"] = 0
				if ((int(_item["dspeed"]) == 0) and (int(latencyTest[0] * 1000) != 0) and (retryMode == False)):
					retryList.append(_item)
					retryConfig.append(config)
				Result.append(_item)
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
				client.stopClient()
				logger.exception("")

			if (True):
				client.stopClient()
				if (retryMode):
					if (retryConfig != []):
						config = retryConfig.pop(0)
					else:
						config = None
				else:
					config = uConfigParser.getNextConfig()

				if (config == None):
					if ((retryMode == True) or (retryList == [])):
						break
					ans = str(input("%d node(s) got 0kb/s,do you want to re-test these node? (Y/N)" % len(retryList))).lower()
					if (ans == "y"):
					#	logger.debug(retryConfig)
						curConfCount = 0
						totalConfCount = len(retryConfig)
						retryMode = True
						config = retryConfig.pop(0)
					#	logger.debug(config)
						continue
					else:
						for r in retryList:
							for s in range(0,len(Result)):
								if (r["remarks"] == Result[s]["remarks"]):
									Result[s]["dspeed"] = r["dspeed"]
									Result[s]["maxDSpeed"] = r["maxDSpeed"]
									Result[s]["ping"] = r["ping"]
									Result[s]["loss"] = r["loss"]
									break
						break
	
	if (TEST_MODE == "TCP_PING"):
		config = uConfigParser.getNextConfig()
		while (True):
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
			Result.append(_item)
			logger.info("%s - %s - Loss:%s%% - TCP_Ping:%d" % (_item["group"],_item["remarks"],_item["loss"] * 100,int(_item["ping"] * 1000)))
			config = uConfigParser.getNextConfig()
			if (config == None):break
	export(Result)
	export(Result,SPLIT_CNT,2,RESULT_IMAGE_COLOR)


