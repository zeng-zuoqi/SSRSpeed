#coding:utf-8

from PIL import Image,ImageDraw,ImageFont
import json
import os
import sys
import time
import logging
logger = logging.getLogger("Sub")

'''
	resultJson
		{
			"group":"GroupName",
			"remarks":"Remarks",
			"loss":0,#Data loss (0-1)
			"ping":0.014,
			"gping":0.011,
			"dspeed":12435646 #Bytes
		}
'''

def getMaxWeight(result,font):
	draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
	maxGroupWeight = 0
	maxRemarkWeight = 0
	for item in result:
		group = item["group"]
		remark = item["remarks"]
		maxGroupWeight = max(maxGroupWeight,draw.textsize(group,font=font)[0])
		maxRemarkWeight = max(maxRemarkWeight,draw.textsize(remark,font=font)[0])

	return (maxGroupWeight + 10,maxRemarkWeight + 10)

def generateWatermark(img,imgWeight,imgHeight):
	pass
#	watermark = Image.new("RBGA",(80,80))

def exportAsPng(result):
	resultFont = ImageFont.truetype("msyh.ttc",18)

	imageHeight = len(result) * 30 + 30
	weight = getMaxWeight(result,resultFont)
	groupWeight = weight[0]
	remarkWeight = weight[1]
	otherWeight = 60
	
	groupRightPosition = groupWeight
	remarkRightPosition = groupRightPosition + remarkWeight
	lossRightPosition = remarkRightPosition + otherWeight
	tcpPingRightPosition = lossRightPosition + otherWeight
	dspeedRightPosition = tcpPingRightPosition + otherWeight + 30

	resultImg = Image.new("RGB",(dspeedRightPosition,imageHeight + 30),(255,255,255))
	
	draw = ImageDraw.Draw(resultImg)

	draw.line((0,0,0,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((groupRightPosition,0,groupRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((remarkRightPosition,0,remarkRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((lossRightPosition,0,lossRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((tcpPingRightPosition,0,tcpPingRightPosition,imageHeight - 1),fill=(127,127,127),width=1)
	
	draw.text((5,4),"Group",font=resultFont,fill=(0,0,0))
	draw.text((groupRightPosition + 5,4),"Remarks",font=resultFont,fill=(0,0,0))
	draw.text((remarkRightPosition + 5,4),"Loss",font=resultFont,fill=(0,0,0))
	draw.text((lossRightPosition + 5,4),"Ping",font=resultFont,fill=(0,0,0))
	draw.text((tcpPingRightPosition + 5,4),"DSpeed",font=resultFont,fill=(0,0,0))
	
	draw.line((0,30,dspeedRightPosition - 1,30),fill=(127,127,127),width=1)

	for i in range(0,len(result)):
		draw.line((0,30 * i + 60,dspeedRightPosition,30 * i + 60),fill=(127,127,127),width=1)
		item = result[i]

		group = item["group"]
		draw.text((5,30 * i + 30 + 4),group,font=resultFont,fill=(0,0,0))

		remarks = item["remarks"]
		draw.text((groupRightPosition + 5,30 * i + 30 + 4),remarks,font=resultFont,fill=(0,0,0,0))

		loss = str(item["loss"] * 100) + "%%"
		while(draw.textsize(loss,font=resultFont)[0] > 50):
			loss = loss[:-1]
		draw.text((remarkRightPosition + 5,30 * i + 30 + 4),loss,font=resultFont,fill=(0,0,0))

		ping = str(item["ping"] * 1000)
		while(draw.textsize(ping,font=resultFont)[0] > 50):
			ping = ping[:-1]
		draw.text((lossRightPosition + 5,30 * i + 30 + 4),ping,font=resultFont,fill=(0,0,0))

		speed = item["dspeed"]
		draw.rectangle((tcpPingRightPosition + 1,30 * i + 30 + 1,dspeedRightPosition - 1,30 * i + 60 -1),getColor(speed))
		draw.text((tcpPingRightPosition + 5,30 * i + 30 + 1),parseSpeed(speed),font=resultFont,fill=(0,0,0))
	
	draw.text((5,imageHeight + 4),"Generated at " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),font=resultFont,fill=(0,0,0))
	filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".png"
	resultImg.save(filename)
	logger.info("Result image saved as %s" % filename)

def parseSpeed(speed):
	speed = speed / 1024 / 1024
	if (speed < 1):
		return("%.2fKB" % (speed * 1024))
	else:
		return("%.2fMB" % speed)

def mixColor(lc,rc,rt):
	return (int(lc[0]*(1-rt)+rc[0]*rt),int(lc[1]*(1-rt)+rc[1]*rt),int(lc[2]*(1-rt)+rc[2]*rt))

def getColor(data):
	if (data > 16 * 1024 * 1024):
		return (255,0,0)
	elif (data < 64 * 1024):
		return mixColor((255,255,255),(128,255,0),data/64/1024)
	elif (data < 512 * 1024):
		return mixColor((128,255,0),(255,255,0),(data-64*1024)/(512*1024-64*1024))
	elif (data < 4*1024*1024):
		return mixColor((255,255,0),(255,128,192),(data-512*1024)/(4*1024*1024-512*1024))
	else:
		return mixColor((255,128,192),(255,0,0),(data-4*1024*1024)/((16-4)*1024*1024))

def exportAsJson(result):
	filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json"
	with open(filename,"w+",encoding="utf-8") as f:
		f.writelines(json.dumps(result,sort_keys=True,indent=4,separators=(',',':')))
		f.close()
	logger.info("Result exported as %s" % filename)


