#coding:utf-8

config = {
	"excludeRemarks":[
		"剩余流量",
		"到期时间",
		"过期时间"
	],
	"exportResult":{
		"hideMaxSpeed":True,
		"uploadResult":False
	},
	"uploadResult":{
		"apiToken":"",
		"server":"",
		"remark":"Example Remark."
	},
	"speedtestsocket":{
		"maxThread":8,	#Thread count
		"buffer":4096,	#Buffer size,bytes
		"skipRuleMatch":False,
		"rules":[
			{
				"mode":"match_isp", #match_isp or match_location
				"ISP":"Microsoft Corporation",
				"tag":"Cachefly"
			},
			{
				"mode":"match_isp",
				"ISP":"Google LLC",
				"tag":"Default"
			}
	#		{
	#			"mode":"match_location",
	#			"countries":[	#Country Code,for example: HK, US, JP etc.
	#			],
	#			"continent":"Europe",
	#			"tag":"Hetzner_DE"
	#		},
	#		{
	#			"mode":"match_location",
	#			"countries":[	#Country Code,for example: HK, US, JP etc.
	#				"HK","SG"
	#			],
	#			"continent":"",
	#			"tag":"Linode_SG"
	#		}
		],
		"downloadLinks":[
			{
				"link":"https://download.microsoft.com/download/2/2/A/22AA9422-C45D-46FA-808F-179A1BEBB2A7/office2007sp3-kb2526086-fullfile-en-us.exe",
				"fileSize":350,	#File size,MBytes
				"tag":"Default"
			},
			{
				"link":"https://cachefly.cachefly.net/100mb.test",
				"fileSize":100,	#File size,MBytes
				"tag":"Cachefly"
			},
			{
				"tag":"Hetzner_DE",
				"link":"https://speed.hetzner.de/1GB.bin",
				"fileSize":1000	#File size,MBytes
			},
			{
				"tag":"Linode_SG",
				"link":"http://speedtest.singapore.linode.com/100MB-singapore.bin",
				"fileSize":100	#File size,MBytes
			}
			
		]
	}
}

