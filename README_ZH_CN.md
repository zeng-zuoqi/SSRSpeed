
  
  

# SSRSpeed

ShadowsocksR 批量测速工具


## 重要提示
出于版权问题“msyh.ttc”字体不会在该仓库提供，在使用Linux操作系统时请您自行提取该字体至程序根目录下以正常导出结果图片


## 特点

  

- 支持 Speedtestnet，Fast.com，Socket下载测速

- 支持导出结果为 json 和 png

- 支持从ShadowsocksR-CSharp的配置文件（gui-config.json）导入或者从订阅链接导入（确认支持SSPanelv2,v3）

- 支持从导出的json文件再次导入并导出为指定格式

  

## 依赖

  

- Python >= 3.6

- pillow

- requests

- pysocks

  
## 操作系统支持

 1. Windows 10 x64
 2. Ubuntu 18.04 LTS

## 快速上手

  

pip install -r requirements.txt
or
pip3 install -r requirements.txt

  

python .\main.py

Usage: main.py [options] arg1 arg2...

Options:

--version 显示版本号然后退出程序

-h, --help 显示该帮助并退出

--cli 以内置命令行形式运行程序

-c GUICONFIG, --config=GUICONFIG

从ShadowsocksR的配置文件中导入节点

-u URL, --url=URL 从订阅链接中导入节点

-m TEST_METHOD, --method=TEST_METHOD

从以下四种测速方式中选择一种方式测速

[speedtestnet,fast,cachefly,socket]

--include=FILTER 仅选中组名或者备注中包含该关键字的节点

--include-remark=REMARKS

仅选中备注中包含该关键字的节点

--include-group=GROUP

仅选中组名中包含该关键字的节点

--exclude=EFLITER 排除组名或者备注中包含该关键字的节点

--exclude-group=EGFILTER

排除组名中包含该关键字的节点

--exclude-remark=ERFILTER

排除备注中包含该关键字的节点

-y, --yes 跳过节点信息确认直接进行测试

-e EXPORT_FILE_TYPE, --export=EXPORT_FILE_TYPE

设置导出文件格式，当前支持json和png

-i IMPORT_FILE, --import=IMPORT_FILE

从导出文件中导入结果，仅支持json

--debug 以调试模式运行程序

  

Example usage :

- python main.py -c gui-config.json --include 韩国 --include-remark Azure --include-group MoCloudPlus -e json -m fast

- python main.py -u https://mocloudplus.com/link/ABCDEFG123456?mu=0 --include 香港 --include-remark Azure --include-group MoCloudPlus --exclude HKT -e png -m fast

  

关键字优先级如下

> -i > -c > -u

> 当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，三个参数中优先级最大的被采用，其余将会被忽略

>

> --include > --include-group > --include-remark

> --exclude > --exclude-group > --exclude-remark

> 当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，将从优先级最大的参数开始过滤。

  
  

## 开发者

  

- 初始版本 [@ranwen](https://github.com/ranwen)

  

## 感谢

-  [speedtest-cli](https://github.com/sivel/speedtest-cli)

-  [Fast.com-cli](https://github.com/nkgilley/fast.com)
