# -*- coding: utf-8-*-  

import sys,os
import codecs

from readdoc import *  

from flask import Flask,request       # pip install flask      注意脚本尽量不在中文目录运行,  可能会说找不到；遇到异常时, 删除 .pyc文件
app = Flask(__name__)


############## 一些配置文件的载入

configfile="config.py"
paths=os.getcwd()    #绝对路径  , os.getcwd()  代替  sys.path[0]
config = codecs.open(paths + "/"+ configfile,'r','utf-8').read( )
exec(config)


idcol=0     # ID 的列
urlcol=1   # 被请求URL地址 的列
reqkeycol=2     # 被请求的 KEY PATH 列
reqkeyvaluecol=3    # 被请求的 KEY 值预期列
realkeycol=4     # 被请求的 KEY 实际值
lastverifycol=5   # 判断
postmodfilecol=6   # 请求端的return模板名的列
retkeycol=7     # 返回的KEY APTH的列
retkeyvaluecol=8    # 返回的KEY值的列
explain=9   # 备注列

allcon=9   # 总列数(排除备注)

startrow=1   # 起始的行


#### 公共变量

xlsx=None
retxlsx=None
retfile=None

############# 执行用例

def runcase(request,header,row,sheet, retkeylist,reqkeylist):

	### 不同的请求类型
	if request.method == 'GET':

		fullurl=request.full_path
		hosturl=request.host_url
		baseurl=request.base_url

		requrl="/" + baseurl.replace(hosturl,"")

		rets=fullurl.replace(requrl+"?","")

	if request.method == 'POST':     #  支持方法 http://blog.csdn.net/wangqing008/article/details/39183153

		## 得到的数据
		ret=request.get_data()
		if sys.version_info.major==2:   #python2
			rets=unicode(ret, "utf-8")
		if sys.version_info.major==3:   #python3
			rets=ret.decode('utf8')

	##############  判断请求

	if isDebug==1:
		if rets==None:
			rets=""
		hues.info(u"被请求信息: \n" + rets)   

	
	for i in range(len(reqkeylist)):

		#print("verify:"+str(i)+": " + reqkeylist[i][0] + "	"  +  reqkeylist[i][1])
		
		wantkey=reqkeylist[i][0]

		####  验证条目注释掉了
		if wantkey[:1]=="#":
			hues.warn(u"预期验证被忽略: " + wantkey[1:])
			continue

		#######  一些转义参数	验证KEY

		getagrspath(rets,wantkey,reqkeylist, row,i, sheet, isSave, retxlsx, realkeycol,lastverifycol)




	###############  进行返回

	postfile=xlsx.get(postmodfilecol,row,sheet)

	try:
		if postfile!="" and postfile!=None:   # UNO 为"", VBA 为 None
			#print(templetpath+postfile)
			data=codecs.open(templetpath+postfile,'r','utf-8').read() 
		else:
			hues.error(u"ERROR:模板文件未填写,请检查 " + templetpath+postfile )
			sys.exit()   ## 强行退出
	except:
		hues.error(u"ERROR:模板文件路径不正确, 请检查 " + templetpath+postfile )
		sys.exit()   ## 强行退出


	if len(retkeylist)>0:  ## 有可能没有修改

		for i in range(len(retkeylist)):
			#print("modify:"+str(i)+": " + retkeylist[i][0] + "	"  +  retkeylist[i][1])

			retkey=retkeylist[i][0]
			if retkey==None:  ## VBA 返回为 None
		                continue

			#   修改条目注释掉了
			if retkey[:1]=="#":
				continue

			#######  一些转义参数	返回KEY

			key=retkey
			keylist=retkeylist
			(data,header)=sendagrspath(data,header,key,keylist,i)


	if isDebug==1:
		hues.info(u"返回信息: \n" + data)         
	
	

	#### 返回需要返回给客户端的内容

	return data,header

##############  请求处理

def webserver():

	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')

	### 请求的地址
	#print(dir(request))
	hosturl=request.host_url
	baseurl=request.base_url
	
	requrl="/" + baseurl.replace(hosturl,"")
	#print(requrl)


	###### 遍历匹配对应的路径位置

	row=startrow  ### 用例起始位置
	sheet=0    #server 模式只使用第一个sheet 页
	while isNullline(xlsx,row,sheet,allcon)==False:  ## 文件未结束

		## server 模式没有忽略执行ID模式

		caselineCount=caselineCounts(xlsx,row,idcol,sheet,allcon)  ## ID所占的行数 
		#print(caselineCount)

		caseurl=xlsx.get(urlcol,row,sheet)
		if caseurl==requrl:    ### 匹配到路径
			
			############## 取出"被请求"数据中需要验证KEY 数据

			column1=reqkeycol
			column2=reqkeyvaluecol			
			reqkeylist=getkeylisy(xlsx,row,caselineCount,column1,column2,sheet)

			### 将每一行的结果部分, 置为未执行   server模式只记录最后一次
			if isSave==1:
				strings=u"非校验"
				colors="yellow"
				basecolumn=reqkeycol
				setcolumn=lastverifycol
				
				setvalues(retxlsx,row,caselineCount,basecolumn,setcolumn,sheet,strings,colors)

			#print(reqkeylist)
			#print(len(reqkeylist))

			############## 取出"返回" 需要修改的数据

			column1=retkeycol
			column2=retkeyvaluecol			
			retkeylist=getkeylisy(xlsx,row,caselineCount,column1,column2,sheet)

			header=[]

			#print(retkeylist)
			#print(len(retkeylist))

			##############  执行用例

			(data,header)=runcase(request,header,row,sheet, retkeylist,reqkeylist)
			return data
			
		row=row+caselineCount     ### 对应用例文件中的下一行用例


	



################################

if __name__ == "__main__":


	################ 一些初始化设置

	# 邮件附件清单
	if os.path.exists('attachlist'):
		os.remove('attachlist')


	#############  用例初步处理

	casefile=casepath + server_case  +".xlsx"   ## 实际文件

	if os.path.exists(casefile)==False:
		hues.error(u"用例文件未找到:" + casefile)
		sys.exit()   ## 强行退出

	
	# 返回对应的句柄
	(xlsx,retxlsx,retfile)=getxlsx(casefile,temppath,isSave,resultpath,server_case)

	
	row=startrow  ### 用例起始位置
	sheet=0    #server 模式只使用第一个sheet 页
	while isNullline(xlsx,row,sheet,allcon)==False:  ## 文件未结束

		caselineCount=caselineCounts(xlsx,row,idcol,sheet,allcon)  ## ID所占的行数   
		#print(caselineCount)

		ids=xlsx.get(idcol,row,sheet)
		caseurl=xlsx.get(urlcol,row,sheet)
		app.add_url_rule(caseurl, '', webserver,methods=['GET', 'POST'])       
		hues.info(u"监听位置: "+  host+":"+ str(server_port) + caseurl)

		row=row+caselineCount     ### 对应用例文件中的下一行用例

	############ 启动监听

	try:
		app.run(host=host, port=server_port)
	except:   # ctrl+c
		print(u"服务监听停止")

	########### 收尾与日志优化输出

	if sysstr == "Linux" or (sysstr == "Windows" and isSave!=1):    #  windows 模式退出，会导致所有 EXCEL 退出
		xlsx.quit()

	print("==========================")

	if isSave==1:

		retxlsx.setcolwidth(idcol,6,sheet)
		retxlsx.setcolwidth(urlcol,13.5,sheet)
		retxlsx.setcolwidth(reqkeycol,18,sheet)
		retxlsx.setcolwidth(reqkeyvaluecol,18,sheet)
		retxlsx.setcolwidth(realkeycol,18,sheet)
		retxlsx.setcolwidth(lastverifycol,18,sheet)
		retxlsx.setcolwidth(postmodfilecol,18,sheet)
		retxlsx.setcolwidth(retkeycol,18,sheet)  
		retxlsx.setcolwidth(retkeyvaluecol,18,sheet)
		retxlsx.setcolwidth(explain,18,sheet)

		retxlsx.quit()


	##### 发送邮件

	
	if sendmail==1 and isSave==1:

		if sys.version_info.major==2: 
			reload(sys)
			sys.setdefaultencoding( "utf-8" )

		####  邮件的正文
		attachlist=open('mailcontent','w')   ## 邮件附件清单文件
		attachlist.write(u"接口测试报告, 测试时间: "+str(datetime.datetime.now())  + "\n")
		attachlist.close()	

		sendmaillist(mail_host,mail_user,mail_pass,mail_postfix, u"接口测试报告, 请查收")	









