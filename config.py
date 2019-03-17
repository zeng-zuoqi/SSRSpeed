#coding:utf-8

config = {
	"speedtestsocket":{
		"maxThread":4,	#Thread count
		"buffer":4094,	#Buffer size,bytes
		"downloadLinks":[
			{
				"area":[
					"ALL"
				],
				"link":"https://cachefly.cachefly.net/100mb.test",
				"fileSize":100	#File size,MBytes
			}
		]
	}
}

