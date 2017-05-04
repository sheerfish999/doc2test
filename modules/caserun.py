# -*- coding: utf-8 -*-

#########################  本文件用于封装读取测试用例，  依赖于自封装 unoclass  （底层  openoffice uno)

#########  版本  2016-11-19

import sys,os
import codecs

import time
import shutil 


import platform
sysstr = platform.system()   ### 判断操作系统类型   Windows   Linux    .   本脚本函数入口, 统一以 LINUX 为准, 其后在函数内进行转换

if sysstr == "Linux":
        import hues   ## pip install hues

if sysstr == "Windows":
        import winhues as hues

from unoclass import *
from readdoc import *  
from dodata import *
from postget import *
from randomid import *
from sendmail import *

try:   ### 不一定需要数据库支持
	from dbrun import *   
except:
	pass


############## 一些配置文件的载入

configfile="config.py"
paths=os.getcwd()    #绝对路径  , os.getcwd()  代替  sys.path[0]
config = codecs.open(paths + "/"+ configfile,'r','utf-8').read( )
exec(config)



#### 模板性质定义

"""
列  0-6 
0  ID    （合并）
1  URL   （合并）
2  post 模板  （合并）
3  自定义修改的KEY
4  自定义修改的KEY 的 VALUE
5  判断返回的KEY
6  判断返回的KEY 的 VALUE

行 从 1 开始



"""

allcon=7  # 用例总共几列  (判断部分的列数,非总体)

idcol=0     # ID 的列
urlcol=1    # URL 的列
postmodfilecol=2   # post模板名的列
mdfkeycol=3       # 修改KEY PATH的列
mdfkeyvaluecol=4  # 修改KEY的VLAUE列
retkeycol=5     # 返回验证的KEY PATH的列
retkeyvaluecol=6    # 返回验证的KEY 预期值的列

realkeycol=7   # 实际返回的对应KEY的列
lastverifycol=8   # 判断

explain=9   # 备注

startrow=1   # 起始的行



#####　对应用例条目调用

def runcase(idsinput,caseurl,postfile,mdfkeylist,retkeylist,row,retfile,sheet, retxlsx):


	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')


	if idsinput==None:
		hues.warn(u"用例格式错误")
		return


	ids=str(idsinput)
	ids=ids.replace("\n","")
	ids=ids.replace("\r","")

	if ids[:1]=="#":    ### 该条接口用例被忽略执行
		hues.warn(u"用例 id:" +ids + u"被忽略执行")
		return


	########################

	hues.log(u"用例 id:" +ids)
	caseurl=vars(caseurl)			###### 请求的地址进行参数化
	hues.log(u"用例 URL:" +caseurl)
	if postfile!="" and postfile!=None:
		hues.log(u"POST模板:" +postfile)
	else:
		hues.log(u"GET模式")
	
	#print("row:" + str(row))
	#print("result file:" + retfile)
	
	try:
		if postfile=="" or postfile==None:   # UNO 为"", VBA 为 None
			data=""  #GET模式
		else:
                        #print(templetpath+postfile)
			data=codecs.open(templetpath+postfile,'r','utf-8').read() 
	except:
		hues.error(u"ERROR:模板文件路径不正确, 请检查 " + templetpath+postfile )
		return

	#######################

	# 参数初始化

	addcookie=""
	header=[]

	########################### 这里进行修改

	if len(mdfkeylist)>0:  ## 有可能没有修改

		for i in range(len(mdfkeylist)):
			#print("modify:"+str(i)+": " + mdfkeylist[i][0] + "	"  +  mdfkeylist[i][1])

			mdkey=mdfkeylist[i][0]
			if mdkey==None:  ## VBA 返回为 None
                                continue

			#   修改条目注释掉了
			if mdkey[:1]=="#":
				continue

			#######  一些转义参数	请求KEY

			key=mdkey
			keylist=mdfkeylist
			(data,header)=sendagrspath(data,header,key,keylist,i)


	#print(data)		

	#### 这里进行执行并得到返回

	if isDebug==1:
		hues.info(u"请求信息: \n" + data)        

	returns=posts(caseurl,data,addcookie,timeouts,header)         ######  进行请求

	if isDebug==1:
		if returns==None:
			returns=""
		hues.info(u"返回信息: \n" + returns)        

	
	########################## 这里进行验证
	
	for i in range(len(retkeylist)):

		#### 没有请求成功
		
		if returns==None:

			if isSave==1:
				retxlsx.set(realkeycol,row+i,"",sheet)     ## 记录输出实际返回结果
				retxlsx.setbgcolor(lastverifycol,row+i,"red",sheet)
				retxlsx.set(lastverifycol,row+i,u"请求失败",sheet)
			
			continue 		


		####  请求成功

		#print("verify:"+str(i)+": " + retkeylist[i][0] + "	"  +  retkeylist[i][1])
		
		wantkey=retkeylist[i][0]

		####  验证条目注释掉了
		if wantkey[:1]=="#":
			hues.warn(u"预期验证被忽略: " + wantkey[1:])
			continue

		#######  一些转义参数	验证KEY

		getagrspath(returns,wantkey,retkeylist, row,i, sheet, isSave,retxlsx, realkeycol,lastverifycol)


###################### 全部用例的读取函数

def readcase():
	
	############## 逐行读取测试用例清单，按照清单查找对应的测试用例 EXCEL 文件（xlsx 格式）
	
	for line in open(caselistfile):     ####  从清单中逐个取用例文件

		line=line.replace("\n","")
		line=line.replace("\r","")	

		if line[:1]!="#" and line!="":
						
			print("==================================================")
			hues.info(u"执行接口用例:" + line)
			print("==================================================")

			casefile=casepath + line +".xlsx"   ## 实际文件
			if os.path.exists(casefile)==False:
				hues.error(u"用例文件未找到:" + casefile)
				continue

			# 返回对应句柄
			casename=line
			(xlsx,retxlsx,retfile)=getxlsx(casefile,temppath,isSave,resultpath,casename)


			#######################  读取对应用例文件的内容
			sheetcount=xlsx.getsheetcount()

			for sheet in range(sheetcount):  # 读对应 sheet


				sheetname=xlsx.getsheetname(sheet)
				hues.info(u"测试页: " + sheetname)
				if sheetname[:1]=="#":
					hues.warn(u"测试页: " + sheetname + u" 被忽略执行")
					print("==========================")
					continue

				### 用例起始位置
				row=startrow
			
				while isNullline(xlsx,row,sheet,allcon)==False:  ## 文件未结束
			
					caselineCount=caselineCounts(xlsx,row,idcol,sheet,allcon)  ## 用例所占的行数
					#print(caselineCount)
				
					############## 取出"请求"需要修改KEY 数据

					column1=mdfkeycol
					column2=mdfkeyvaluecol			
					mdfkeylist=getkeylisy(xlsx,row,caselineCount,column1,column2,sheet)
					
					#print(len(mdfkeylist))

					############## 取出"返回"需要验证KEY 数据

					column1=retkeycol
					column2=retkeyvaluecol			
					retkeylist=getkeylisy(xlsx,row,caselineCount,column1,column2,sheet)

					### 将每一行的结果部分, 置为未执行
					if isSave==1:
						strings=u"未执行/非校验"
						colors="yellow"
						basecolumn=retkeycol
						setcolumn=lastverifycol
						setvalues(retxlsx,row,caselineCount,basecolumn,setcolumn,sheet,strings,colors)

					#print(len(retkeylist))

					############# 执行对应条目
					#print(idcol)
					#print(row)
					#print(sheet)
					
					ids=xlsx.get(idcol,row,sheet)
					caseurl=xlsx.get(urlcol,row,sheet)
					postfile=xlsx.get(postmodfilecol,row,sheet)
				
					### 执行
					runcase(ids,caseurl,postfile,mdfkeylist,retkeylist,row,retfile,sheet, retxlsx)
										
				
					#############
				
					row=row+caselineCount     ### 对应用例文件中的下一行用例

					print("==========================")



			if sysstr == "Linux" or (sysstr == "Windows" and isSave!=1):    #  windows 模式退出，会导致所有 EXCEL 退出
				xlsx.quit()



			if isSave==1:

				#### 优化输出格式 (列宽)
				for sheet in range(retxlsx.getsheetcount()):
					retxlsx.setcolwidth(idcol,6,sheet)
					retxlsx.setcolwidth(urlcol,13.5,sheet)
					retxlsx.setcolwidth(postmodfilecol,11.5,sheet)
					retxlsx.setcolwidth(mdfkeycol,18,sheet)
					retxlsx.setcolwidth(mdfkeyvaluecol,18,sheet)
					retxlsx.setcolwidth(retkeycol,18,sheet)
					retxlsx.setcolwidth(retkeyvaluecol,18,sheet)
					retxlsx.setcolwidth(realkeycol,18,sheet)  
					retxlsx.setcolwidth(lastverifycol,10,sheet)
					retxlsx.setcolwidth(explain,18,sheet)

				#### 转到第一个 sheet 上
				retxlsx.activesheet()

				retxlsx.quit()
			


################################################  执行

if __name__ == '__main__':  


	###### 一些初始化设置

	# 邮件附件清单
	if os.path.exists('attachlist'):
		os.remove('attachlist')

	###### 执行

	readcase()


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

	
	







