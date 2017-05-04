# -*- coding: utf-8 -*-


import sys,os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'    # 必须有这句  否则数据库中文识别有问题

import platform
sysstr = platform.system()   ### 判断操作系统类型   Windows   Linux    .   本脚本函数入口, 统一以 LINUX 为准, 其后在函数内进行转换

if sysstr == "Linux":
        import hues   ## pip install hues

if sysstr == "Windows":
        import winhues as hues

"""
######### ORACLE 支持

1)   Instant Client ,  普通情况下载  BASIC  SDK即可
http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html
SDK解压到同名目录下

/etc/profile  或  .bashrc 中
export ORACLE_HOME 到 Instant Client 对应路径
export LD_LIBRARY_PATH=$ORACLE_HOME:/usr/local/lib:${LD_LIBRARY_PATH}

2)  pip install cx_Oracle

某些情况下 找不到 库, 在对应 $ORACLE_HOME , ln -s 对应库即可, 如  libclntsh.so

"""

try:   #### 不一定需要oracle 支持
	import cx_Oracle
except:
	#traceback.print_exc()
	pass


import traceback


"""
############# MYSQL 支持

1)  安装 mysql 客户端
2)  pip install mysql-connector

"""

try:  ##### 不一定需要 mysql 支持
	import mysql.connector
except:
	#traceback.print_exc()
	pass


########################### oracle

def oraclesql(connectstr,sql):   # connectstr='username/password@host/tns'           只返回第一行第一个数值 (唯一值)

	#print(sql)

	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')
	
	try:
		db=cx_Oracle.connect(connectstr)
	except:
		hues.warn(u"Oracle数据库连接失败: " +connectstr )
		traceback.print_exc()
		return ""

	cr=db.cursor()

	## 如果最后一个是 ; 则去掉
	if sql[len(sql)-1:]==";":
		sql=sql[:len(sql)-1]

	try:
		hues.info(sql)
		cr.execute(sql)
	except:
		hues.warn(u"Oracle数据库语句执行失败")
		traceback.print_exc()
		return ""		

	try:
		rs=cr.fetchall()
		if sys.version_info.major==2:   #   /x
			rs=str(rs[0][0]).decode("utf-8")
		if sys.version_info.major==3:   
			rs=str(rs[0][0])	
	except:            #非查询  或语句有问题等
		rs=""

	db.commit()

	cr.close()
	db.close()

	return rs

############################# mysql

def mysqls(connectstr,sql):   # connectstr='username/password@host:port/dbname'           只返回第一行第一个数值 (唯一值)


	#print(sql)

	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')

	try:
		temp=connectstr.split("@")
		username=temp[0].split("/")[0]
		password=temp[0].split("/")[1]
		host=temp[1].split("/")[0]
		dbname=temp[1].split("/")[1]

		port=host.split(":")[1]	
		host=host.split(":")[0]
	except:
		hues.warn(u"connectstr格式错误")
		return ""

	"""	
	print(username)
	print(password)
	print(host)
	print(dbname)
	"""

	try:
		db = mysql.connector.connect(host=host,port=port,user=username,password=password,database=dbname)
	except:
		hues.warn(u"Mysql数据库连接失败")
		traceback.print_exc()
		return ""

	try:
		cursor = db.cursor(buffered=True)
		cursor.execute(sql)
	except:
		hues.warn(u"Mysql语句执行失败")
		traceback.print_exc()
		return ""
	
	try:
		rs=cursor.fetchone()[0]
		if sys.version_info.major==2:   #   /x
			rs=str(rs).decode("utf-8")
		if sys.version_info.major==3:   
			rs=str(rs)	
	except:            #非查询  或语句有问题等
		rs=""


	db.commit()

	cursor.close()
	db.close()

	return rs


################################################  测试

if __name__ == '__main__':  

	#######  oracle

	"""
	connectstr='core_ppe/core123@10.17.5.18/zmcftest'

	sql=u"update UP_CARD_BINDING set BINDING_CARD_NO='666611111111339912' where BINDING_NAME='六零二'"
	rs=oraclesql(connectstr,sql)

	sql=u"select BINDING_CARD_NO from  UP_CARD_BINDING where BINDING_NAME='六零二'"
	rs=oraclesql(connectstr,sql)
	print(rs)
	"""

	####### mysql

	connectstr='zmit/zmit123456@10.17.5.151:3307/Biz'

	sql=u"update Biz.TB_BRANCH set NAME='测试1234'  where ID='638582CB-074F-4B32-944D-24F58B945699'"
	rs=mysqls(connectstr,sql)

	sql=u"SELECT count(*) FROM Biz.RF_AUTOBID_REPAYMETHOD;"
	rs=mysqls(connectstr,sql)

	print(rs)


