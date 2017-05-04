# -*- coding: utf-8 -*-

import os,sys

import uuid
import random
import time
import datetime
import hashlib

import re


import platform
sysstr = platform.system()   ### 判断操作系统类型   Windows   Linux    .   本脚本函数入口, 统一以 LINUX 为准, 其后在函数内进行转换

if sysstr == "Linux":
        import hues   ## pip install hues

if sysstr == "Windows":
        import winhues as hues

#################################    本文件用于转义 KEY VALUE 部分的参数化

# 获得()中间的tagname字符串 

"""
入口:  
1)  restr 函数前缀如: #random
2)  strs 原始字符串

出口:
1) 查到的字符串
2) 内部的变量串

"""

def midstr(restr,strs):    

	restr="(\\" +  restr + "\(.*\))"   # 拼出正则表达式

	#print(restr)

	# 这里不能用 match.  match是从字符串的开始(即第一个)与表达式匹配，search是从所有字符串 与表达式匹配
	getstrs=re.search(restr,strs)

	if getstrs!= None: 

		strs=getstrs.groups()[0]   # 目前支持一个, 未来可以轮询支持多个

		pos1=strs.find("(")
		pos2=strs.find(")")

		if pos2!=pos1+1:
			tagvalues=strs[pos1+1:pos2]

			if sysstr == "Windows":
				tagvalues=tagvalues.encode('gbk','ignore')  ##  windows 转为 gbk 编码

			#print(tagvalues)
		
		else:
			tagvalues=""
	else:
		tagvalues=None			

	return strs,tagvalues





####################  本文件生成随机值


########  UUID

def uuids():

	res=uuid.uuid1()   # uuid1单一不能实现随机
	return(str(res))


########  随机值

def getnum(counts):

	res=""
	for nos in range(counts):
		here=random.randint(1, 9)
		res=res + str(here)		

	return res

########  身份证号

def getcardid():

	id = '110108' #地区项
	id = id + str(random.randint(1930,2016)) #年份项 
	da = datetime.date.today()+datetime.timedelta(days=random.randint(1,366)) #月份和日期项 
	id = id + da.strftime('%m%d') 
	id = id+ str(random.randint(100,300))#，顺序号简单处理 
	#     print '身份证前17位:',id
	count = 0
	weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2] #身份证前17数字的权重项 
	checkcode ={'0':'1','1':'0','2':'X','3':'9','4':'8','5':'7','6':'6','7':'5','8':'4','9':'3','10':'2'} #余数映射校验码字典
	n = len(id)
	for i in range(n): 
		count = count +int(id[i])*weight[i] #求出身份证号前17位数字，每一位数字与权重相乘后的总和
	#     print count    
	id = id + checkcode[str(count%11)] #总和对11取余数，根据余数映射的验证码字典，得出校验码 
	return id

#################  手机号

def getphone():

	phone=random.choice(['131','132','133','134','135','136','137','138','139','188','185','151','158'])+"".join(random.choice("0123456789") for i in range(8))

	#print("Phone: " + phone)

	return(phone)


################# 农行卡号

################## 农行卡卡号


def farmbankcardid():

	cardtag="622848"

	# 622848后   0987654320000, 共 13 位

	x ='%04d%04d%04d%d' %(random.randint(1,9999),
		random.randint(1,9999),
		random.randint(1,9999),
		random.randint(0,9))
	
	farmbankid=cardtag+x

	#print("FarmBank Cardid: " + farmbankid)

	return(farmbankid)


################# 用户名

def getname():

	uuids=uuid.uuid1()   # uuid1单一不能实现随机

	m = hashlib.md5()    #md5 非对称
	m.update(str(uuids).encode('utf-8'))
	names= m.hexdigest()   

	names=names[:8]    #截取
	names="t"+ names   #首字符为字母

	#print("Name: " + names)

	return(names)


####  使用生成器循环返回文件行

hasget=False
def readfilecycline(filename):

	global hasget
	hasget=True      ### 判断是否被引用过

	while True:
		files=open(filename)

		for line in files:
			line=line.replace("\n","")
			line=line.replace("\r","")
			yield line

		files.close()


################# 替换变量到对应的函数

##  最后随机化的参数值
lastuuid=""     ### 最后一个生成的uuid
lastrandom=""    ### 最后一个生成的随机值
lastphone=""	###  随后一个随机化的电话号码
lastcardid=""	### 最后一个随机化的身份证号
lastbankcardid=""   #### 最后一个随机化的银行卡号

valuelist=[]      ### 储存的 getvalue

filecyc=None


# 增加一个记忆值, 变量格式: [tagvalues,value]
def addvaluelist(lists):          

	valuelist.append(lists)



def  vars(strsinput,realvalue=""):   #  VALUE内容替换到参数变量化,   第二个值是给 $set 类参数存储使用的

	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')

	strs=str(strsinput)

	global valuelist
	global lastrandom
	global lastuuid
	global lastcardid
	global lastphone
	global lastbankcardid

	repstr=""

	###### UUID
	if "$uuid()" in strs:
		repstr=uuids()
		strs=strs.replace("$uuid()",repstr)
		lastuuid=repstr   ## 最后一个参数化的值,  供返回调用和判断等

	if "$lastuuid()" in strs:

		repstr=lastuuid
		strs=strs.replace("$lastuuid()",repstr)

	####### PHONE
	if "$phone()" in strs:
		repstr=getphone()
		strs=strs.replace("$phone()",repstr)
		lastphone=repstr   ## 最后一个参数化的值,  供返回调用和判断等

	if "$lastphone()" in strs:

		repstr=lastphone
		strs=strs.replace("$lastphone()",repstr)


	####### CARDID  身份证号
	if "$cardid()" in strs:
		repstr=getcardid()
		strs=strs.replace("$cardid()",repstr)
		lastcardid=repstr   ## 最后一个参数化的值,  供返回调用和判断等

	if "$lastcardid()" in strs:

		repstr=lastcardid
		strs=strs.replace("$lastcardid()",repstr)


	####### 银行卡号
	if "$bankcardid()" in strs:
		repstr=farmbankcardid()
		strs=strs.replace("$bankcardid()",repstr)
		lastbankcardid=repstr   ## 最后一个参数化的值,  供返回调用和判断等

	if "$lastbankcardid()" in strs:

		repstr=lastbankcardid
		strs=strs.replace("$lastbankcardid()",repstr)



	####### RANDOM
	restr="$random"
	(findstr,randomstr)=midstr(restr,strs)

	if randomstr!="" and randomstr!=None :	
		randomnum=int(randomstr)
		repstr=getnum(randomnum)
	
		### 原地替换
		strs=strs.replace(findstr,repstr)

		lastrandom=repstr   ## 最后一个参数化的值,  供返回调用和判断等

	elif randomstr=="":    #还有可能是 None
		hues.warn(u"$random(num) 中没设定 随机串长度")

	if "$lastrandom()" in strs:
		repstr=lastrandom
		strs=strs.replace("$lastrandom()",repstr)


	#########  GETVALUE  得到一个值储存起来
	restr="$getvalue"

	(findstr,tagvalues)=midstr(restr,strs)

	if tagvalues!=""  and tagvalues!=None :
		#print(tagvalues)
		addvaluelist([tagvalues,realvalue])   ### 以 tag 为标记插入 list ,  将实际值存储起来
		
		strs="$it's a tag for get somthing"	   

	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$getvalue(tag) 中没设定 tag 标记值")


	########  SETVLAUE 使用储存的值 
	restr="$setvalue"

	(findstr,tagvalues)=midstr(restr,strs)

	if tagvalues!=""  and tagvalues!=None :

		replacestr=""
		for i in range(len(valuelist)):   ###  轮询查询对应的 tag 标记的值 (最后一条符合的)
			#print(valuelist[i][0])
			if valuelist[i][0]==tagvalues:
				replacestr=valuelist[i][1]

		if replacestr!="":					
			strs=strs.replace(findstr,replacestr)

	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$setvalue(tag) 中没设定 tag 标记值")


	#########  SAVETOFILE  得到一个值储存到文件

	restr="$savetofile"
	(findstr,tagvalues)=midstr(restr,strs)

	if tagvalues!=""  and tagvalues!=None :

		#print(tagvalues)

		files=open(tagvalues,'a')
		files.write(realvalue)    ### 将实际值存储追加到文件
		files.write("\n")
		files.close()
		
		strs="$it's a tag for get somthing"
   
	elif tagvalues=="":    #还有可能是 None

		hues.warn(u"$savetofile(filename) 中没设定 filename 文件名")


	############  FROMFILE 从文件循环得到变量

	global filecyc

	restr="$fromfile"
	(findstr,tagvalues)=midstr(restr,strs)	

	if tagvalues!=""  and tagvalues!=None :

		replacestr=""
		#### 从文件循环读取
		if os.path.exists(tagvalues)!=False:
			if hasget==False:     ### 判断是否被引用过
				filecyc=readfilecycline(tagvalues)
			if sys.version_info.major==2:   #python2
				replacestr=filecyc.next()
			if sys.version_info.major==3:   #python3
				replacestr=filecyc.__next__()
	
		else:
			hues.warn(u"提取用文件: " + tagvalues + u" 未找到.")

		### 原地替换
		if replacestr!="":	### 空值不替换				
			strs=strs.replace(findstr,replacestr)

	elif tagvalues=="":    #还有可能是 None
		hues.warn(u"$fromfile(filename) 中没设定 filename 文件名")


	#####################

	#print(strs)
	return strs




