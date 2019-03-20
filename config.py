#coding:utf-8

config = {
	"speedtestsocket":{
		"maxThread":4,	#Thread count
		"buffer":4096,	#Buffer size,bytes
		"downloadLinks":[
			{
				"countries":[	#Country Code,for example: HK, US, JP etc.
					"ALL"
				],
				"link":"https://cachefly.cachefly.net/100mb.test",
				"fileSize":100	#File size,MBytes
			}
		]
	}
}

