#coding:utf-8

import time
import sys
import os
import json
import threading
import urllib.parse
import platform
from optparse import OptionParser
import logging

from flask import Flask,request

from SSRSpeed.Utils.checkRequirements import checkShadowsocks
from SSRSpeed.Utils.checkPlatform import checkPlatform
from SSRSpeed.Utils.Web.parseqsplus import parse_qs_plus
from SSRSpeed.Core.SSRSpeedCore import SSRSpeedCore

from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult

from config import config

WEB_API_VERSION = "0.0.2-alpha"

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

def setOpts(parser):
	parser.add_option(
		"-l","--listen",
		action="store",
		dest="listen",
		default=config["web"]["listen"],
		help="Set listen address for web server."
		)
	parser.add_option(
		"-p","--port",
		action="store",
		dest="port",
		default=config["web"]["port"],
		help="Set listen port for web server."
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

app = Flask(__name__)
sc = None

def getPostData():
	#print(request.content_type)
	data = {}
	if (request.content_type.startswith('application/json')):
		data = request.get_data()
		return json.loads(data)
	elif(request.content_type.startswith("application/x-www-form-urlencoded")):
		#print(1)
		#print(urllib.parse.parse_qs(request.get_data().decode("utf-8")))
		return parse_qs_plus(urllib.parse.parse_qs(request.get_data().decode("utf-8")))
	else:
		for key, value in request.form.items():
			if key.endswith('[]'):
				data[key[:-2]] = request.form.getlist(key)
			else:
				data[key] = value
		return data
@app.route("/",methods=["POST"])
def index():
	print(getPostData())
	return "SUCCESS"

'''
	{
		"proxyType":"SSR", //[SSR,SSR-C#,SS,V2RAY]
		"testMethod":"SOCKET", //[SOCKET,SPEED_TEST_NET,FAST]
		"testMode":"",//[ALL,TCP_PING]
		"subscriptionUrl":"",
		"colors":"origin",
		"sortMethod":"",//[SPEED,REVERSE_SPEED,PING,REVERSE_PING]
		"include":[],
		"includeGroup":[],
		"includeRemark":[],
		"exclude":[],
		"excludeGroup":[],
		"excludeRemark":[]
	}
'''

@app.route('/start',methods=["POST"])
def startTest():
	if (request.method == "POST"):
		data = getPostData()
	#	return "SUCCESS"
		if (json.loads(sc.getWebResults()).get("status","stopped") == "running"):
			return 'running'
		sc.clean()
		sc.proxyType =data.get("proxyType","SSR")
		sc.testMethod =data.get("testMethod","SOCKET")
		sc.subscriptionUrl =data.get("subscriptionUrl","")
		if (sc.subscriptionUrl == ""):
			return 'invalid subscription url.'
		sc.colors =data.get("colors","origin")
		sc.sortMethod =data.get("sortMethod",""),
		sc.setup()
		sc.filterNodes(
			data.get("include",[]),
			data.get("includeGroup",[]),
			data.get("includeRemark",[]),
			data.get("exclude",[]),
			data.get("excludeGroup",[]),
			data.get("excludeRemark",[])
		)
		if (data.get("testMode","") == "TCP_PING"):
			sc.startTcpingOnlyTest()
		else:
			sc.startFullTest()
		return 'done'
	return 'invalid method'

@app.route('/getresults')
def sleepp():
	return sc.getWebResults()

if (__name__ == "__main__"):
	pfInfo = checkPlatform()
	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	DEBUG = False

	parser = OptionParser(usage="Usage: %prog [options] arg1 arg2...",version="SSR Speed Web Api " + WEB_API_VERSION)
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

	sc = SSRSpeedCore()
	sc.webMode = True
	app.run(host=options.listen,port=int(options.port),debug=DEBUG,threaded=True)

