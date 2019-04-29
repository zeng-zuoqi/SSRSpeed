

  
<h1 align="center">
    <br>SSRSpeed
</h1>
<p align="center">
基于Shadowsocks(R)的批量测速工具
</p>
<p align="center">
   <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/NyanChanMeow/SSRSpeed.svg">
    <img alt="GitHub release" src="https://img.shields.io/github/release/NyanChanMeow/SSRSpeed.svg">
    <img src="https://img.shields.io/github/license/NyanChanMeow/SSRSpeed.svg">
</p>

<p></p>


## 重要提示

<font size=5 color=#FF0033>在您公开发布测速结果之前请务必征得节点拥有者的同意以避免一些令人烦恼的事情</font>

 - SpeedTestNet方式已停止支持


## 特点
- 支持 Speedtestnet，Fast.com，Socket下载测速
- 支持导出结果为 json 和 png
- 支持从GUI的配置文件（gui-config.json）导入或者从订阅链接导入（确认支持SSPanelv2,v3）
- 支持从导出的json文件再次导入并导出为指定格式
- 支持WebUI

## 依赖

通用依赖
- Python >= 3.6
- pillow
- requests
- pysocks
- flask
- flask-cors

Linux 依赖
 - [libsodium](https://github.com/jedisct1/libsodium)
 - [Shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev)
 - [Simple-Obfs](https://github.com/shadowsocks/simple-obfs)

## 已支持平台
1. Windows 10 x64
2. Ubuntu 18.04 LTS

## 快速上手
### 命令行用法
pip install -r requirements.txt
or
pip3 install -r requirements.txt

    python .\main.py
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
      -t PROXY_TYPE, --type=PROXY_TYPE
                            选择代理类型[ssr,ss]，默认为ssr
      -y, --yes             跳过节点信息确认直接进行测试
      -C RESULT_COLOR, --color=RESULT_COLOR
                            选择导出图片的配色方案
      -s SPLIT_COUNT, --split=SPLIT_COUNT
                            设置单张结果图片显示的节点数量，会自动导出多张图片
      -S SORT_METHOD, --sort=SORT_METHOD
                            选择排序方式 [speed,rspeed,ping,rping],默认不排序
      -i IMPORT_FILE, --import=IMPORT_FILE
                            从导出文件中导入结果，仅支持json
      --debug               以调试模式运行程序


使用示例:
- python main.py -c gui-config.json --include 韩国 --include-remark Azure --include-group MoCloudPlus
- python main.py -u https://mocloudplus.com/link/ABCDEFG123456?mu=0 --include 香港 Azure --include-group MoCloudPlus --exclude HKT HKBN
- python main.py -u https://mocloudplus.com/link/ABCDEFG123456?mu=0 -t ss


关键字优先级如下

> -i > -c > -u
> 当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，三个参数中优先级最大的被采用，其余将会被忽略
> --include > --include-group > --include-remark
> --exclude > --exclude-group > --exclude-remark
> 当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，将从优先级最大的参数开始过滤。

### Web UI（测试中）

    python web.py
    此时访问 http://127.0.0.1:10870/ 可以进入Web UI

## 高级用法
 - **规则**
   - 程序拥有内置的规则匹配模式通过自定义规则匹配特定ISP或者特定地区的节点使用特定的下载测速源，规则已内置于config.py文件中，查看它以获得更多的信息。
  
 - **自定义配色**
   - 用户可以通过修改 config.py 中的配色部分和 -C 参数来自定义导出图片的配色方案，请查看 config.py 文件获得更多细节。

## 开发者
- [@ranwen](https://github.com/ranwen)

## 感谢
- 新配色方案
   - Chunxiaoyi 纯小亦
- Bug 反馈
   -  [Professional-V1](https://t.me/V1_BLOG)
   -  [Julydate 七夏浅笑](https://www.julydate.com/)
- 此项目还使用了这些开源项目
   -  [speedtest-cli](https://github.com/sivel/speedtest-cli)
   -  [Fast.com-cli](https://github.com/nkgilley/fast.com)