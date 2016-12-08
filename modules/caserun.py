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
from dodata import *
from postget import *
from randomid import *
from sendmail import *

caselistfile="caselist"  ####  用例文件列表清单文件
casepath="case/case_xlsx/"		####   用例文件保存相对路径, 这里根据实际框架目录结构情况进行调整
templetpath="case/service_templet/"    ####   POST 模板保存相对路径, 这里根据实际框架目录结构情况进行调整
resultpath="result/"     	####   记录文件保存相对路径, 这里根据实际框架目录结构情况进行调整
temppath="case/temporary/"   ####  临时文件目录


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
mdfkeycol=3       # 修改KEY名的列
mdfkeyvaluecol=4  # 修改KEY的VLAUE列
retkeycol=5     # 返回验证的KEY名的列
retkeyvaluecol=6    # 返回验证的KEY值的列

realkeycol=7   # 实际返回的对应KEY的列
lastverifycol=8   # 判断

explain=9   # 备注

startrow=1   # 起始的行



#### 对应case条目行是否在对应行结束(空行判断）

def isNullline(xlsx,row,sheet):

	Nullline=True  ## 空行
	
	for i in range(allcon):
		#print(xlsx.get(i,row,sheet))

		getvalue=xlsx.get(i,row,sheet)
		if getvalue!="" and getvalue!=None:   
			Nullline=False  
			break
			
	return Nullline
	
	
##### 判断用例所占的行数

def caselineCounts(xlsx,row,sheet):

	if xlsx.getmerge(idcol,row,sheet)==False:   ##非合并行
		return 1
	
	therow=row+1
	while (xlsx.get(idcol,therow,sheet)=="" or xlsx.get(idcol,therow,sheet)==None) and isNullline(xlsx,therow,sheet)==False:    ## 新ID未出现， 并且非空行 
		therow=therow+1		
	
	return therow-row
	

##### 判断修改 KEY 的行数

def mdfkeyCounts(xlsx,fromrow,caselineCount,sheet):

	getvalue=xlsx.get(mdfkeycol,fromrow,sheet)
	if getvalue=="" or getvalue==None:
		return 0  # 没有修改

	for mdfkeyline in range(fromrow,fromrow+caselineCount+1):

		getvalue=xlsx.get(mdfkeycol,mdfkeyline,sheet)
		if getvalue=="" or getvalue==None:
			break

	return mdfkeyline-fromrow 


##### 判断验证 KEY 的行数

def retkeyCounts(xlsx,fromrow,caselineCount,sheet):

	for retkeyline in range(fromrow,fromrow+caselineCount+1):

		getvalue=xlsx.get(retkeycol,retkeyline,sheet)                
		if getvalue=="" or getvalue==None:
			break

	return retkeyline-fromrow



#####　对应用例条目调用

def runcase(idsinput,caseurl,postfile,mdfkeylist,retkeylist,row,retfile,sheet, retxlsx):


	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')


	if idsinput==None:
		hues.warn(u"用例格式错误")
		return


	ids=str(idsinput)


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

	########################### 这里进行修改KEY

	if len(mdfkeylist)>0:  ## 有可能没有修改
		for i in range(len(mdfkeylist)):
			#print("modify:"+str(i)+": " + mdfkeylist[i][0] + "	"  +  mdfkeylist[i][1])

			mdkey=mdfkeylist[i][0]
			if mdkey==None:  ## VBA 返回为 None
                                continue

			#   修改条目注释掉了
			if mdkey[:1]=="#":
				continue

			#  一些转义参数
			
			if mdkey=="$cookie()":    # cookie	cookie 添加
				addcookie=mdfkeylist[i][1]

			elif re.search("(\$addheader\(.*\))",mdkey) != None:    # header 添加
					pos1=mdkey.find("(")
					pos2=mdkey.find(")")

					if pos2!=pos1+1:
						tagvalues=mdkey[pos1+1:pos2]
						#print(tagvalues)
						header.append([tagvalues,mdfkeylist[i][1]])				   
					else:
						hues.warn(u"$addheader(headername) 中没设定 headername 标记值")

			else:		#  常规KEY值设置
				values=mdfkeylist[i][1]
				realvalue=readnode(data, mdfkeylist[i][0])
				values=vars(values,realvalue)     #### 请求内容  替换到参数变量化,  第二个值是给 $set 类参数存储使用的

				## 如果不是取值模式:
				if values!="$it's a tag for get somthing":
					data=writenode(data, mdkey, values)

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

		realvalue=readnode(returns, wantkey)     ### 读 KEY 位置的 实际返回值

		if isSave==1:
			if sysstr == "Windows":
				realvalue=realvalue.encode('gbk','ignore')  ## 转为特定编码
			retxlsx.set(realkeycol,row+i,realvalue,sheet)     ## 记录输出实际返回结果
		
		wantvalue=  retkeylist[i][1]

		if wantvalue==None:   ## VBA 返回为 None
                        wantvalue=""

                
		wantvalue=vars(wantvalue,realvalue)     #### 返回内容  替换到参数变量化,  第二个值是给 $set 类参数存储使用的

		if sysstr == "Windows":
			wantvalue=wantvalue.encode('gbk','ignore')  ## 转为特定编码
		
		## 如果不是取值模式:
		if wantvalue !="$it's a tag for get somthing":

			if sysstr == "Windows":
				wantvalue=wantvalue.decode('gbk','ignore')
				realvalue=realvalue.decode('gbk','ignore')
			
			hues.info(u"预期结果: "  + wantkey + "	"  + wantvalue)

			if realvalue!=wantvalue:

				hues.error(u"实际结果: "  + realvalue)

				if isSave==1:
					retxlsx.setbgcolor(lastverifycol,row+i,"red",sheet)
					retxlsx.set(lastverifycol,row+i,u"错误",sheet)
			else:
				hues.success(u"实际结果: "  + realvalue)

				if isSave==1:
					retxlsx.setbgcolor(lastverifycol,row+i,"green",sheet)
					retxlsx.set(lastverifycol,row+i,u"正确",sheet)		



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

			tempcasefile=temppath + "temporary.xlsx"   ## 临时文件

			#  拷贝生成临时文件,避免当前文件正被编辑


                        ### 如果是 windows , 临时文件也可能被占用，因此需要打开，并关闭
			if sysstr == "Windows":
                                try:
                                        xlsx=openexcel(tempcasefile)
                                        xlsx.quit()
                                except:
                                        pass
			
			
			shutil.copyfile(casefile,tempcasefile)
			xlsx=openexcel(tempcasefile)
			
			
			####### 复制用例,以便输出测试用例

			retxlsx=None
			retfile=None
			if isSave==1:
				now = int(time.time()) 
				timeArray = time.localtime(now)
				times = time.strftime("%Y%m%d%H%M%S", timeArray)
			
				retfile=str(resultpath + line + "_result_"+ times + ".xlsx")
				#print(retfile)                
				
				### 加入附件清单
				if os.path.exists('attachlist')==False:
					temp=open("attachlist",'w')
					temp.close()

				attachlist=open("attachlist",'a')
				attachlist.write(retfile+"\n")
				
				attachlist.close()				
				
							
				### 复制并打开记录文件
				shutil.copyfile(casefile,retfile)
				retxlsx=openexcel(retfile)    ### 结果文件, 不是临时文件


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
			
				while isNullline(xlsx,row,sheet)==False:  ## 文件未结束
			
					caselineCount=caselineCounts(xlsx,row,sheet)  ## 用例所占的行数
					#print(caselineCount)
				
					############## 取出需要修改KEY 数据
				
					mdfkeyCount=mdfkeyCounts(xlsx,row,caselineCount,sheet)  ## 其中修改KEY所占的行数
					#print(mdfkeyCount)
					mdfkeylist=[]
				
					for mdf in range(row,row+mdfkeyCount):   ## 对应的行
						mdfkey=xlsx.get(mdfkeycol,mdf,sheet)
						#print(mdfkey)
						mdfkeyvalue=xlsx.get(mdfkeyvaluecol,mdf,sheet)
						#print(mdfkeyvalue)
						mdfkeylist.append([mdfkey,mdfkeyvalue])
					
					#print(len(mdfkeylist))

					############## 取出需要验证KEY 数据

					retkeyCount=retkeyCounts(xlsx,row,caselineCount,sheet)   ## 其中验证KEY所占的行数
					#print(retkeyCount)
					retkeylist=[]


					for ret in range(row,row+retkeyCount):  ## 对应的行
						retkey=xlsx.get(retkeycol,ret,sheet)
						#print(retkey)					
						retkeyvalue=xlsx.get(retkeyvaluecol,ret,sheet)
						#print(retkeyvalue)
						retkeylist.append([retkey,retkeyvalue])

						### 将每一行的结果部分, 置为未执行
						if isSave==1:
							retxlsx.set(lastverifycol,ret,u"未执行",sheet)
							retxlsx.setbgcolor(lastverifycol,ret,"yellow",sheet)
					
					#print(len(retkeylist))

					############# 执行对应条目
					#print(idcol)
					#print(row)
					#print(sheet)
					
					ids=xlsx.get(idcol,row,sheet)
					caseurl=xlsx.get(urlcol,row,sheet)
					postfile=xlsx.get(postmodfilecol,row,sheet)
				
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

	
	







