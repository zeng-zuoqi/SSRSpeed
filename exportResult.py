#coding:utf-8

from PIL import Image,ImageDraw,ImageFont
import json
import os
import sys
import time
import logging
logger = logging.getLogger("Sub")

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

	def __getMaxWeight(self,result,font):
		draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
		maxGroupWeight = 0
		maxRemarkWeight = 0
		for item in result:
			group = item["group"]
			remark = item["remarks"]
			maxGroupWeight = max(maxGroupWeight,draw.textsize(group,font=font)[0])
			maxRemarkWeight = max(maxRemarkWeight,draw.textsize(remark,font=font)[0])
		return (maxGroupWeight + 10,maxRemarkWeight + 10)

	def exportAsPng(self,result,id=0):
		resultFont = ImageFont.truetype("msyh.ttc",18)

		generatedTime = time.localtime()

		imageHeight = len(result) * 30 + 30
		weight = self.__getMaxWeight(result,resultFont)
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

		newImageHeight = imageHeight + 30
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

		for i in range(0,len(result)):
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

		if (id > 0):
			draw.text((5,imageHeight + 4),"Generated at " + time.strftime("%Y-%m-%d %H:%M:%S", generatedTime) + ("-%d" % id),font=resultFont,fill=(0,0,0))
			draw.line((0,newImageHeight - 1,imageRightPosition,newImageHeight - 1),fill=(127,127,127),width=1)
			filename = time.strftime("%Y-%m-%d-%H-%M-%S", generatedTime) + "-%d.png" % id
			resultImg.save(filename)
			logger.info("Result image saved as %s" % filename)
		else:
			draw.text((5,imageHeight + 4),"Generated at " + time.strftime("%Y-%m-%d %H:%M:%S", generatedTime),font=resultFont,fill=(0,0,0))
			draw.line((0,newImageHeight - 1,imageRightPosition,newImageHeight - 1),fill=(127,127,127),width=1)
			filename = time.strftime("%Y-%m-%d-%H-%M-%S", generatedTime) + ".png"
			resultImg.save(filename)
			logger.info("Result image saved as %s" % filename)

	def __parseSpeed(self,speed):
		speed = speed / 1024 / 1024
		if (speed < 1):
			return("%.2fKB" % (speed * 1024))
		else:
			return("%.2fMB" % speed)

	def __mixColor(self,lc,rc,rt):
		return (int(lc[0]*(1-rt)+rc[0]*rt),int(lc[1]*(1-rt)+rc[1]*rt),int(lc[2]*(1-rt)+rc[2]*rt))

	def __getColor(self,data):
		if (data > 16 * 1024 * 1024):
			return (255,0,0)
		elif (data < 64 * 1024):
			return self.__mixColor((255,255,255),(128,255,0),data/64/1024)
		elif (data < 512 * 1024):
			return self.__mixColor((128,255,0),(255,255,0),(data-64*1024)/(512*1024-64*1024))
		elif (data < 4*1024*1024):
			return self.__mixColor((255,255,0),(255,128,192),(data-512*1024)/(4*1024*1024-512*1024))
		else:
			return self.__mixColor((255,128,192),(255,0,0),(data-4*1024*1024)/((16-4)*1024*1024))

	def exportAsJson(self,result):
		filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json"
		with open(filename,"w+",encoding="utf-8") as f:
			f.writelines(json.dumps(result,sort_keys=True,indent=4,separators=(',',':')))
			f.close()
		logger.info("Result exported as %s" % filename)


