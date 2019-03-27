
# SSRSpeed

ShadowsocksR 批量测速工具

## 重要提示

出于版权问题“msyh.ttc”字体不会在该仓库提供，在使用Linux操作系统时请您自行提取该字体至程序根目录下以正常导出结果图片

SpeedTestNet方式已停止支持，将在不久之后移除！

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

python main.py

    Usage: main.py [options] arg1 arg2...
    
    Options:
      --version             显示版本信息
      -h, --help            显示帮助信息
      -c GUICONFIG, --config=GUICONFIG
                            从ssr-win客户端加载配置文件
      -u URL, --url=URL     从ssr订阅链接中加载节点信息
      -m TEST_METHOD, --method=TEST_METHOD
                            从 [speedtestnet,fast,socket] 中选择测速方式
      -M TEST_MODE, --mode=TEST_MODE
                            选择测试模式 [all,pingonly]，pingonly方式仅进行TCP Ping
      --include             仅选中组名或者备注中包含该关键字的节点
      --include-remark      仅选中备注中包含该关键字的节点
      --include-group       仅选中组名中包含该关键字的节点
      --exclude             排除组名或者备注中包含该关键字的节点
      --exclude-group       排除组名中包含该关键字的节点
      --exclude-remark      排除备注中包含该关键字的节点
      -y, --yes             跳过节点信息确认直接进行测试
      -s SPLIT_COUNT, --split=SPLIT_COUNT
                            设置单张结果图片显示的节点数量，会自动导出多张图片
      -i IMPORT_FILE, --import=IMPORT_FILE
                            从导出文件中导入结果，仅支持json
      --debug               以调试模式运行程序

用法示例 :
- python main.py -c gui-config.json --include 韩国 --include-remark Azure --include-group MoCloudPlus
- python main.py -u https://mocloudplus.com/link/ABCDEFG123456?mu=0 --include 香港 Azure --include-group MoCloudPlus --exclude HKT HKBN

关键字优先级如下

> -i > -c > -u
> 当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，三个参数中优先级最大的被采用，其余将会被忽略
> --include > --include-group > --include-remark
> --exclude > --exclude-group > --exclude-remark  
> 当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，将从优先级最大的参数开始过滤。

## 开发者
- 初始版本 [@ranwen](https://github.com/ranwen)

## 感谢
-  [speedtest-cli](https://github.com/sivel/speedtest-cli)
-  [Fast.com-cli](https://github.com/nkgilley/fast.com)