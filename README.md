

# 本项目为了优化和解决以下问题:

1) webserivce接口集成测试的特点是: 围绕集成接口规格说明书建立工作过程, 不同的目标可能需要维护多套文档. 这样造成的问题是文档与测试执行的代码存在脱节的风险, 如果能直接实现从文档到测试的过程, 简化了工作步骤, 降低了这种风险.

2) 工具化的文档读取(如loadrunner,postman,jmeter)依赖于工具本身,存在一定的约束性,扩展性也较低, 工具本身就带来一定的门槛,常规的接口测试过程使用类似工具笨重不灵活.

3) excel 文档的表现方式丰富, 优于文本\配置文件, 其维护性和可读性又优于代码脚本, 如果能快速的可视化的编写测试过程, 将减少测试代码编写和维护量. 本框架兼容 Linux 和 Windows, 直接解决 跨平台的调用和调试的统一问题(如jenkins调用) 


# 语法支持及使用方法,  请参考本项目Wiki:
http://callisto.ngrok.cc/wiki/doku.php?id=doc2test


# 安装方法
## Linux (推荐)

1 需要 pyuno文档操作 及 openoffice/libreoffice 支持
1) 注意不要安装 pip install uno , 安装请 uninstall
2) 同一个发行版的系统, 一般只在 python2 或 python3 中某一个版本支持python-uno, 因此注意支持的版本并使用对应的python版本:

centos:

yum install python-openoffice  libreoffice

debian:

apt-get install libreoffice-script-provider-python libreoffice

2 根据实际使用的 python 版本选择 pip 安装支持包:

pip install hues
pip3 install request http  (如果使用 python3)
pip install jsonpath_rw

3 lxml的解析支持 (debian为例)
debian:

apt install python-libxml2 # 或python3-libxml2

pip install  lxml   #或 apt-get install python3-lxml #python3

## Windows

1) 需要 MS office EXCEL 支持

2) 安装pip包

pip install pywin32
pip install six
pip install ply
pip install jsonpath_rw  

3) 安装 libxml2

http://xmlsoft.org/sources/win32/python/libxml2-python-2.7.7.win32-py2.7.exe

3) 安装 lxml

http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml  下载对应的 whl,  如 lxml‑3.6.4‑cp27‑cp27m‑win32.whl
pip install lxml‑3.6.4‑cp27‑cp27m‑win32.whl

4) 若提示安装VC9.0 编译环境，可安装 Micorsoft Visual C++ Compiler for Python 2.7
(http://www.microsoft.com/en-us/download/details.aspx?id=44266）

