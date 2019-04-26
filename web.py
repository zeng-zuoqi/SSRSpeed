#coding:utf-8

import time
import sys
import os
import json
import threading
import urllib.parse
import logging

from flask import Flask,request,render_template

from SSRSpeed.Utils.checkRequirements import checkShadowsocks
from SSRSpeed.Utils.checkPlatform import checkPlatform

from SSRSpeed.Utils.Web.getpostdata import getPostData

from SSRSpeed.Core.SSRSpeedCore import SSRSpeedCore
import SSRSpeed.Core.Shell.ConsoleWeb as ShellWebServer

from SSRSpeed.Result.exportResult import ExportResult
import SSRSpeed.Result.importResult as importResult

from config import config

WEB_API_VERSION = "0.1.1-alpha"

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

TEMPLATE_FOLDER = "./resources/webui/templates"
STATIC_FOLDER = "./resources/webui/static"

app = Flask(__name__,
	template_folder=TEMPLATE_FOLDER,
	static_folder=STATIC_FOLDER,
	static_url_path=""
	)
sc = None

@app.route("/",methods=["GET"])
def index():
	return render_template(
		"index.html"
		)

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

@app.route("/status",methods=["GET"])
def status():
	sc.getWebStatus()

@app.route('/start',methods=["POST"])
def startTest():
	if (request.method == "POST"):
		data = getPostData()
	#	return "SUCCESS"
		if (json.loads(sc.getWebStatus()).get("status","stopped") == "running"):
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
def getResults():
	return sc.getWebStatus()

if (__name__ == "__main__"):
	pfInfo = checkPlatform()
	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	DEBUG = False
	
	options,args = ShellWebServer.init(WEB_API_VERSION)

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

