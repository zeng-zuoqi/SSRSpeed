#coding:utf-8

import copy

V2RayBaseConfig = {
	"remarks":"",
	"group":"N/A",
	"server":"",
	"server_port":"",
	"log": {
		"access": "",
		"error": "",
		"loglevel": "warning"
	},
	"inbounds": [
		{
			"port": 1087,
			"listen": "127.0.0.1",
			"protocol": "socks",
			"sniffing": {
				"enabled": True,
				"destOverride": [
					"http",
					"tls"
				]
			},
			"settings": {
				"auth": "noauth",
				"udp": True,
				"ip": None,
				"clients": None
			},
			"streamSettings": None
		}
	],
	"outbounds": [
		{
			"tag": "proxy",
			"protocol": "vmess",
			"settings": {
				"vnext": [
					{
						"address": "",
						"port": 1,
						"users": [
							{
								"id": "",
								"alterId": 0,
								"email": "",
								"security": "auto"
							}
						]
					}
				],
				"servers": None,
				"response": None
			},
			"streamSettings": {
				"network": "",
				"security": "",
				"tlsSettings": None,
				"tcpSettings": None,
				"kcpSettings": None,
				"wsSettings": None,
				"httpSettings": None,
				"quicSettings": None
			},
			"mux": {
				"enabled": True
			}
		},
		{
			"tag": "direct",
			"protocol": "freedom",
			"settings": {
				"vnext": None,
				"servers": None,
				"response": None
			},
			"streamSettings": None,
			"mux": None
		},
		{
			"tag": "block",
			"protocol": "blackhole",
			"settings": {
				"vnext": None,
				"servers": None,
				"response": {
					"type": "http"
				}
			},
			"streamSettings": None,
			"mux": None
		}
	],
	"dns": None,
	"routing": {
		"domainStrategy": "IPIfNonMatch",
		"rules": []
	}
}

def getConfig():
	return copy.deepcopy(V2RayBaseConfig)


