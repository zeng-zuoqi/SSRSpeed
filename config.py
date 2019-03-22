#coding:utf-8

config = {
	"speedtestsocket":{
		"maxThread":4,	#Thread count
		"buffer":4096,	#Buffer size,bytes
		"defaultDownloadLink":{
			"link":"https://cachefly.cachefly.net/100mb.test",
			"fileSize":100	#File size,MBytes
		},
		"downloadLinks":[
			{
				"countries":[	#Country Code,for example: HK, US, JP etc.
				],
				"Continent":"Europe",
				"link":"https://speed.hetzner.de/1GB.bin",
				"fileSize":1000	#File size,MBytes
			},
			{
				"countries":[	#Country Code,for example: HK, US, JP etc.
					"US"
				],
				"Continent":"",
				"link":"http://speedtest.dallas.linode.com/100MB-dallas.bin",
				"fileSize":100	#File size,MBytes
			},
			{
				"countries":[	#Country Code,for example: HK, US, JP etc.
					"JP"
				],
				"Continent":"",
				"link":"http://speedtest.tokyo2.linode.com/100MB-tokyo2.bin",
				"fileSize":100	#File size,MBytes
			},
			{
				"countries":[	#Country Code,for example: HK, US, JP etc.
					"HK","SG"
				],
				"Continent":"",
				"link":"http://speedtest.singapore.linode.com/100MB-singapore.bin",
				"fileSize":100	#File size,MBytes
			}
			
		]
	}
}

