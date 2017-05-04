# -*- coding: utf-8 -*-

import shutil
import time

import platform
sysstr = platform.system()   ### 判断操作系统类型   Windows   Linux    .   本脚本函数入口, 统一以 LINUX 为准, 其后在函数内进行转换


from unoclass import *
from dodata import *
from postget import *
from randomid import *

try:   ### 不一定需要数据库支持
	from dbrun import *   
except:
	pass

#########################  本文件用于封装框架层次的文件操作


########## 返回excel文件操作句柄

def getxlsx(casefile,temppath,isSave,resultpath,casename):

	#######  用例基本处理

	tempcasefile=temppath + "temporary.xlsx"   ## 临时文件	

	#  拷贝生成临时文件,避免当前文件正被编辑

        ### 如果是 windows , 临时文件也可能被占用，因此需要打开，并关闭
	if sysstr == "Windows":
                try:
                        xlsx=openexcel(tempcasefile)
                        xlsx.quit()
                except:
                        pass
	
	####### 复制用例,以便输出测试用例

	retxlsx=None
	retfile=None

	if isSave==1:

		now = int(time.time()) 
		timeArray = time.localtime(now)
		times = time.strftime("%Y%m%d%H%M%S", timeArray)
	
		retfile=str(resultpath + casename + "_result_"+ times + ".xlsx")
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

	# 打开文件
	shutil.copyfile(casefile,tempcasefile)
	xlsx=openexcel(tempcasefile)

	return (xlsx,retxlsx,retfile)


#### 对应case条目行是否在对应行结束(空行判断）

def isNullline(xlsx,row,sheet,allcon):

	Nullline=True  ## 空行
	
	for i in range(allcon):
		#print(xlsx.get(i,row,sheet))

		getvalue=xlsx.get(i,row,sheet)
		if getvalue!="" and getvalue!=None:   
			Nullline=False  
			break
			
	return Nullline


##### 判断用例所占的行数

def caselineCounts(xlsx,row,column,sheet,allcon):

	idcol=column   #id 的列位置
	
	if xlsx.getmerge(idcol,row,sheet)==False:   ##非合并行
		return 1
	
	therow=row+1
	while (xlsx.get(idcol,therow,sheet)=="" or xlsx.get(idcol,therow,sheet)==None) and isNullline(xlsx,therow,sheet,allcon)==False:    ## 新ID未出现， 并且非空行 
		therow=therow+1		
	
	return therow-row



#####  该id 对应某个列的行数

def keyCounts(xlsx,fromrow,caselineCount,column,sheet):

	getvalue=xlsx.get(column,fromrow,sheet)
	if getvalue=="" or getvalue==None:
		return 0  # 没有

	for keyline in range(fromrow,fromrow+caselineCount+1):

		getvalue=xlsx.get(column,keyline,sheet)
		if getvalue=="" or getvalue==None:
			break

	return keyline-fromrow


#####  获得两个对应列的成员信息 (对应fromrow, caselineCount)

def getkeylisy(xlsx,fromrow,caselineCount,column1,column2,sheet):

	keyCount=keyCounts(xlsx,fromrow,caselineCount,column1,sheet)   # 行数
	keylist=[]

	for ret in range(fromrow,fromrow+keyCount):   ## 对应的行
		key=xlsx.get(column1,ret,sheet)
		#print(retkey)
		keyvalue=xlsx.get(column2,ret,sheet)
		#print(retkeyvalue)
		keylist.append([key,keyvalue])

	return keylist

#####  批量设置对应列属性 (对应 fromrow, caselineCount, basecolumn)

def setvalues(retxlsx,row,caselineCount, basecolumn,setcolumn,sheet,strings,colors):

	keyCount=keyCounts(retxlsx,row,caselineCount,basecolumn,sheet)   # 行数
	#print(keyCount)

	for ret in range(row,row+keyCount):  ## 对应的行
		
		retxlsx.set(setcolumn,ret,strings,sheet)
		retxlsx.setbgcolor(setcolumn,ret,colors,sheet)


#####  "得到返回" 及 "被请求"  KEY PATH 部分参数化的处理  (测试端得到, 并进行验证)

def getagrspath(returns,wantkey,retkeylist, row,i, sheet, isSave,retxlsx, realkeycol,lastverifycol):
	
	##### oracle
	restr="$oracle"
	(findstr,tagvalues)=midstr(restr,wantkey)

	if tagvalues!=""  and tagvalues!=None :

		Connectstr=tagvalues
		values=retkeylist[i][1]
		sqlstr=vars(values)    # SQL语句先进行参数化

		#print(Connectstr)
		#print(sqlstr)
		rs=oraclesql(Connectstr,sqlstr)

		if rs!="":    ## 返回值存储到  oracle 变量中
			addvaluelist(["oracle",rs])
		
		return
			
	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$oracle(ConnectionString) 中没设定 ConnectionString 标记值")

		return

	
	##### mysql
	restr="$mysql"
	(findstr,tagvalues)=midstr(restr,wantkey)

	if tagvalues!=""  and tagvalues!=None :

		Connectstr=tagvalues
		values=retkeylist[i][1]
		sqlstr=vars(values)    # SQL语句先进行参数化

		#print(Connectstr)
		#print(sqlstr)
		rs=mysqls(Connectstr,sqlstr)

		if rs!="":    ## 返回值存储到  mysql 变量中
			addvaluelist(["mysql",rs])
		
		return
			
	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$mysql(ConnectionString) 中没设定 ConnectionString 标记值")

		return


	 ##### 读 KEY 位置的 实际返回值

	realvalue=readnode(returns, wantkey)    

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





#####  "请求" 及 "返回给客户端"  KEY PATH 部分参数化的处理   (测试端发送, 没有验证部分)


def sendagrspath(data,header,key,keylist,i):

	#### cookie
	if key=="$cookie()":    # cookie	cookie 添加
		values=keylist[i][1]
		addcookie=vars(values)    # cookie先进行参数化

		return data,header

	#### header
	restr="$addheader"
	(findstr,tagvalues)=midstr(restr,key)

	if tagvalues!=""  and tagvalues!=None :
			values=keylist[i][1]
			headerlist=vars(values)    # header先进行参数化	
			header.append([tagvalues,headerlist])
			return data,header
	elif tagvalues=="":    #还有可能是 None
			return data,header

	##### oracle
	restr="$oracle"
	(findstr,tagvalues)=midstr(restr,key)

	if tagvalues!=""  and tagvalues!=None :
		Connectstr=tagvalues
		values=keylist[i][1]
		sqlstr=vars(values)    # SQL语句先进行参数化

		#print(Connectstr)
		#print(sqlstr)
		rs=oraclesql(Connectstr,sqlstr)

		if rs!="":    ## 返回值存储到  oracle 变量中
			addvaluelist(["oracle",rs])
		
		return data,header
			
	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$oracle(ConnectionString) 中没设定 ConnectionString 标记值")

		return data,header


	##### mysql
	restr="$mysql"
	(findstr,tagvalues)=midstr(restr,key)

	if tagvalues!=""  and tagvalues!=None :
		Connectstr=tagvalues
		values=keylist[i][1]
		sqlstr=vars(values)    # SQL语句先进行参数化

		#print(Connectstr)
		#print(sqlstr)
		rs=mysqls(Connectstr,sqlstr)

		if rs!="":    ## 返回值存储到  mysql 变量中
			addvaluelist(["mysql",rs])
		
		return data,header
			
	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$mysql(ConnectionString) 中没设定 ConnectionString 标记值")

		return data,header
	

	######  常规的KEY值变量化设置

	values=keylist[i][1]
	realvalue=readnode(data, keylist[i][0])
	values=vars(values,realvalue)     #### 请求内容  替换到参数变量化,  第二个值是给 $set 类参数存储使用的

	## 如果不是取值模式:
	if values!="$it's a tag for get somthing":
		data=writenode(data, key, values)


	return data,header












