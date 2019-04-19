#coding:utf-8

import logging
import os

logger = logging.getLogger("Sub")

def checkShadowsocks():
	sslibev = False
	simpleobfs = False
	for cmdpath in os.environ["PATH"].split(":"):
		if (not os.path.isdir(cmdpath)):
			continue
		for filename in os.listdir(cmdpath):
			if (filename == "obfs-local"):
				logger.info("Obfs-Local found {}".format(os.path.join(cmdpath,"obfs-local")))
				simpleobfs = True
			elif(filename == "ss-local"):
				logger.info("Shadowsocks-libev found {}".format(os.path.join(cmdpath,"ss-local")))
				sslibev = True
			if (simpleobfs and sslibev):
				break
		if (simpleobfs and sslibev):
			break
	if (not simpleobfs):
		logger.critical("Simple Obfs not found.")
		return False
	if (not sslibev):
		logger.critical("Shadowsocks-libev not found.")
		return False
	return True


