#coding:utf-8

from PIL import Image,ImageDraw,ImageFont
import json
import os
import sys
import time
import logging
logger = logging.getLogger("Sub")

from SSRSpeed.Result.uploadResult import pushToServer
from SSRSpeed.Utils.sorter import Sorter

from config import config

'''
	resultJson
		{
			"group":"GroupName",
			"remarks":"Remarks",
			"loss":0,#Data loss (0-1)
			"ping":0.014,
			"gping":0.011,
			"dspeed":12435646 #Bytes
			"maxDSpeed":12435646 #Bytes
		}
'''

class ExportResult(object):
	def __init__(self):
		self.__config = config["exportResult"]
		self.hideMaxSpeed = self.__config["hideMaxSpeed"]
		self.__colors = {}
		self.__colorSpeedList = []
		self.__font = ImageFont.truetype(self.__config["font"],18)
	#	self.setColors()

	def setColors(self,name = "origin"):
		for color in self.__config["colors"]:
			if (color["name"] == name):
				logger.info("Set colors as {}.".format(name))
				self.__colors = color["colors"]
				self.__colorSpeedList.append(0)
				for speed in self.__colors.keys():
					try:
						self.__colorSpeedList.append(float(speed))
					except:
						continue
				self.__colorSpeedList.sort()
				return
		logger.warn("Color {} not found in config.".format(name))

	def export(self,result,split = 0,exportType = 0,sortMethod = ""):
		if (not exportType):
			self.__exportAsJson(result)
		sorter = Sorter()
		result = sorter.sortResult(result,sortMethod)
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
				self.__exportAsPng(_list,id)
				id += 1
		else:
			self.__exportAsPng(result)

	def __getMaxWeight(self,result):
		font = self.__font
		draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
		maxGroupWeight = 0
		maxRemarkWeight = 0
		for item in result:
			group = item["group"]
			remark = item["remarks"]
			maxGroupWeight = max(maxGroupWeight,draw.textsize(group,font=font)[0])
			maxRemarkWeight = max(maxRemarkWeight,draw.textsize(remark,font=font)[0])
		return (maxGroupWeight + 10,maxRemarkWeight + 10)

	def __deweighting(self,result):
		_result = []
		for r in result:
			isFound = False
			for i in range(0,len(_result)):
				_r = _result[i]
				if (_r["group"] == r["group"] and _r["remarks"] == r["remarks"]):
					isFound = True
					if (r["dspeed"] > _r["dspeed"]):
						_result[i] = r
					elif(r["ping"] < _r["ping"]):
						_result[i] = r
					break
			if (not isFound):
				_result.append(r)
		return _result

	def __exportAsPng(self,result,id=0):
		if (self.__colorSpeedList == []):
			self.setColors()
		# result = self.__deweighting(result)
		resultFont = self.__font
		generatedTime = time.localtime()
		imageHeight = len(result) * 30 + 30 
		weight = self.__getMaxWeight(result)
		groupWeight = weight[0]
		remarkWeight = weight[1]
		if (groupWeight < 60):
			groupWeight = 60
		if (remarkWeight < 60):
			remarkWeight = 90
		otherWeight = 100
	
		groupRightPosition = groupWeight
		remarkRightPosition = groupRightPosition + remarkWeight
		lossRightPosition = remarkRightPosition + otherWeight
		tcpPingRightPosition = lossRightPosition + otherWeight
		dspeedRightPosition = tcpPingRightPosition + otherWeight
		maxDSpeedRightPosition = dspeedRightPosition + otherWeight

		if (not self.hideMaxSpeed):
			imageRightPosition = maxDSpeedRightPosition
		else:
			imageRightPosition = dspeedRightPosition

		newImageHeight = imageHeight + 30 * 2
		resultImg = Image.new("RGB",(imageRightPosition,newImageHeight),(255,255,255))
		draw = ImageDraw.Draw(resultImg)

		draw.line((0,0,0,newImageHeight - 1),fill=(127,127,127),width=1)
		draw.line((groupRightPosition,0,groupRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
		draw.line((remarkRightPosition,0,remarkRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
		draw.line((lossRightPosition,0,lossRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
		draw.line((tcpPingRightPosition,0,tcpPingRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
		draw.line((dspeedRightPosition,0,dspeedRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
		draw.line((imageRightPosition,0,imageRightPosition,newImageHeight - 1),fill=(127,127,127),width=1)
	
		draw.line((0,0,imageRightPosition - 1,0),fill=(127,127,127),width=1)

		draw.text((5,4),"Group",font=resultFont,fill=(0,0,0))
		draw.text((groupRightPosition + 5,4),"Remarks",font=resultFont,fill=(0,0,0))
		draw.text((remarkRightPosition + 5,4),"Loss",font=resultFont,fill=(0,0,0))
		draw.text((lossRightPosition + 5,4),"Ping",font=resultFont,fill=(0,0,0))
		draw.text((tcpPingRightPosition + 5,4),"AvgSpeed",font=resultFont,fill=(0,0,0))

		if (not self.hideMaxSpeed):
			draw.text((dspeedRightPosition + 5,4),"MaxSpeed",font=resultFont,fill=(0,0,0))
	
		draw.line((0,30,imageRightPosition - 1,30),fill=(127,127,127),width=1)

		totalTraffic = 0
		for i in range(0,len(result)):
			totalTraffic += result[i]["trafficUsed"] if (result[i]["trafficUsed"] > 0) else 0
			draw.line((0,30 * i + 60,imageRightPosition,30 * i + 60),fill=(127,127,127),width=1)
			item = result[i]

			group = item["group"]
			draw.text((5,30 * i + 30 + 4),group,font=resultFont,fill=(0,0,0))

			remarks = item["remarks"]
			draw.text((groupRightPosition + 5,30 * i + 30 + 4),remarks,font=resultFont,fill=(0,0,0,0))

			loss = "%.2f" % (item["loss"] * 100) + "%"
			draw.text((remarkRightPosition + 5,30 * i + 30 + 4),loss,font=resultFont,fill=(0,0,0))

			ping = "%.2f" % (item["ping"] * 1000)
			draw.text((lossRightPosition + 5,30 * i + 30 + 4),ping,font=resultFont,fill=(0,0,0))

			speed = item["dspeed"]
			if (speed == -1):
				draw.text((tcpPingRightPosition + 5,30 * i + 30 + 1),"N/A",font=resultFont,fill=(0,0,0))
			else:
				draw.rectangle((tcpPingRightPosition + 1,30 * i + 30 + 1,dspeedRightPosition - 1,30 * i + 60 -1),self.__getColor(speed))
				draw.text((tcpPingRightPosition + 5,30 * i + 30 + 1),self.__parseSpeed(speed),font=resultFont,fill=(0,0,0))

			if (not self.hideMaxSpeed):
				maxSpeed = item["maxDSpeed"]
				if (maxSpeed == -1):
					draw.text((dspeedRightPosition + 5,30 * i + 30 + 1),"N/A",font=resultFont,fill=(0,0,0))
				else:
					draw.rectangle((dspeedRightPosition + 1,30 * i + 30 + 1,maxDSpeedRightPosition - 1,30 * i + 60 -1),self.__getColor(maxSpeed))
					draw.text((dspeedRightPosition + 5,30 * i + 30 + 1),self.__parseSpeed(maxSpeed),font=resultFont,fill=(0,0,0))
		files = []
		if (totalTraffic < 0):
			trafficUsed = "N/A"
		else:
			trafficUsed = self.__parseTraffic(totalTraffic)
		if (id > 0):
			draw.text((5,imageHeight + 4),
				"Traffic used : {}. Generated at {} - {} By SSRSpeed {}.".format(
					trafficUsed,
					time.strftime("%Y-%m-%d %H:%M:%S", generatedTime),
					id,
					config["VERSION"]
				),
				font=resultFont,
				fill=(0,0,0)
			)
			draw.line((0,newImageHeight - 1,imageRightPosition,newImageHeight - 1),fill=(127,127,127),width=1)
			filename = "./results/" + time.strftime("%Y-%m-%d-%H-%M-%S", generatedTime) + "-%d.png" % id
			resultImg.save(filename)
			files.append(filename)
			logger.info("Result image saved as %s" % filename)
		else:
			draw.text((5,imageHeight + 4),
				"Generated at {}".format(
					time.strftime("%Y-%m-%d %H:%M:%S", generatedTime),
				),
				font=resultFont,
				fill=(0,0,0)
			)
			draw.line((0,newImageHeight - 30 - 1,imageRightPosition,newImageHeight - 30 - 1),fill=(127,127,127),width=1)
			draw.text((5,imageHeight + 30 + 4),
				"Traffic used : {}. By SSRSpeed {}.".format(
					trafficUsed,
					config["VERSION"]
				),
				font=resultFont,
				fill=(0,0,0)
			)
			draw.line((0,newImageHeight - 1,imageRightPosition,newImageHeight - 1),fill=(127,127,127),width=1)
			filename = "./results/" + time.strftime("%Y-%m-%d-%H-%M-%S", generatedTime) + ".png"
			resultImg.save(filename)
			files.append(filename)
			logger.info("Result image saved as %s" % filename)
		for _file in files:
			if (not self.__config["uploadResult"]):
				break
			pushToServer(_file)

	def __parseTraffic(self,traffic):
		traffic = traffic / 1024 / 1024
		if (traffic < 1):
			return("%.2f KB" % (traffic * 1024))
		gbTraffic = traffic / 1024
		if (gbTraffic < 1):
			return("%.2f MB" % traffic)
		return ("%.2f GB" % gbTraffic)

	def __parseSpeed(self,speed):
		speed = speed / 1024 / 1024
		if (speed < 1):
			return("%.2fKB" % (speed * 1024))
		else:
			return("%.2fMB" % speed)

	def __newMixColor(self,lc,rc,rt):
	#	print("RGB1 : {}, RGB2 : {}, RT : {}".format(lc,rc,rt))
		return (
			int(lc[0]*(1-rt)+rc[0]*rt),
			int(lc[1]*(1-rt)+rc[1]*rt),
			int(lc[2]*(1-rt)+rc[2]*rt)
		)

	def __getColor(self,data):
		if (self.__colorSpeedList == []):
			return (255,255,255)
		rt = 1
		curSpeed = self.__colorSpeedList[len(self.__colorSpeedList)-1]
		backSpeed = 0
		if (data >= curSpeed  * 1024 * 1024):
			return (self.__colors[str(curSpeed)][0],self.__colors[str(curSpeed)][1],self.__colors[str(curSpeed)][2])
		for i in range (0,len(self.__colorSpeedList)):
			curSpeed = self.__colorSpeedList[i] * 1024 * 1024
			if (i > 0):
				backSpeed = self.__colorSpeedList[i-1]
			backSpeedStr = str(backSpeed)
		#	print("{} {}".format(data/1024/1024,backSpeed))
			if (data < curSpeed):
				rgb1 = self.__colors[backSpeedStr] if backSpeed > 0 else (255,255,255)
				rgb2 = self.__colors[str(self.__colorSpeedList[i])]
				rt = (data - backSpeed * 1024 * 1024)/(curSpeed - backSpeed * 1024 * 1024)
				logger.debug("Speed : {}, RGB1 : {}, RGB2 : {}, RT : {}".format(data/1024/1024,rgb1,rgb2,rt))
				return self.__newMixColor(rgb1,rgb2,rt)
		return (255,255,255)


	def __exportAsJson(self,result):
		# result = self.__deweighting(result)
		filename = "./results/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json"
		with open(filename,"w+",encoding="utf-8") as f:
			f.writelines(json.dumps(result,sort_keys=True,indent=4,separators=(',',':')))
			f.close()
		logger.info("Result exported as %s" % filename)

