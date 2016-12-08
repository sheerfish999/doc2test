# -*- coding: utf-8 -*-

import os,time,sys
from time import sleep

import platform
sysstr = platform.system()  

if sysstr == "Linux":
        import hues   ## pip install hues

if sysstr == "Windows":
        import winhues as hues

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication

import datetime
import codecs


from jenkins import *    ###  jenkins  支持脚本
   

############################## 本脚本用于封装发送邮件操作


# 发送邮件动作  邮件服务器位置, 用户名, 密码, 邮箱后缀,  标题, 内容

def sendmaill(mail_host,mail_user,mail_pass,mail_postfix, to_list, sub,content):

	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')

	#####

	msg = MIMEMultipart('alternative')    ## 创建一个实例

	#mailtype="text"  
	mailtype="html"	

	if mailtype=="html":
		heads="<head><meta http-equiv='Content-Type' content='text/html; charset=utf-8' /> </head>"
		content=content.replace("\n","<br>")
		msgcontent = MIMEText(heads + content,_subtype='html',_charset='utf-8')    

	if mailtype=="text":
		msgcontent = MIMEText(content,_charset='utf-8')   

	msg.attach(msgcontent)

	me="Auto-Report"+"<"+mail_user+"@"+mail_postfix+">"   #发送人姓名
	msg['Subject'] = sub    #设置主题
	msg['From'] = me
	msg['To'] = ";".join(to_list)  

	### 附件列表

	attachlist="attachlist"     ### 默认的附件列表文件, 可以生成该文件

	file_object= codecs.open(attachlist,'r','utf-8')             
	attach_list = file_object.readline() 
	
	while attach_list: 

		attach_list=attach_list.replace('\n','')    #处理换行

		if len(attach_list)>1:            # 行有内容


			attach_list=attach_list.replace('\n','')
			attach_list=attach_list.replace('\r','')


			data = codecs.open(attach_list, 'rb','utf-8') 
			file_msg = MIMEApplication(data.read( ))    ### 可以应对所有文件类型
			data.close( )

			file_msg.add_header('Content-Disposition', 'attachment', filename = attach_list)  
			msg.attach(file_msg)

		attach_list = file_object.readline() 

	file_object.close()  


	### 发送

	try:  

		#s= smtplib.SMTP()   ## 常规模式, 在禁止非常规的模式的情况下, 可能 报  SMTPAuthenticationError(550, 'User suspended')
		s = smtplib.SMTP_SSL()    ## SSL  模式
		
		print("connect....")
		s.connect(mail_host)  #连接smtp服务器
		print("login....")
		s.login(mail_user,mail_pass)  #登陆服务器
		print("send....")
		s.sendmail(me, to_list, msg.as_string())  #发送邮件
		s.close()  
		time.sleep(1)   #避免被服务器认为是攻击
		return True  
	except: 
		print(sys.exc_info())   
		return False	


def tosendmaill(mail_host,mail_user,mail_pass,mail_postfix, mailto_list, sub,content):  

	if sendmaill(mail_host,mail_user,mail_pass,mail_postfix, mailto_list, sub,content):  
		print (u"发送成功:"+mailto_list) 
	else:  
		print (u"发送失败:"+mailto_list)


#按列表发送   邮件服务器位置, 用户名, 密码, 邮箱后缀,   标题, 内容
def sendmaillist(mail_host,mail_user,mail_pass,mail_postfix, sub):


	#### 发送的邮件信息

	filename="mailcontent"           ####  默认的邮件内容文件, 可以生成该文件
	file_object = open(filename)
	content = file_object.read( )	   #内容
	file_object.close()


	##### 支持外部临时环境变量的发送地址, 以便支持诸如 jenkins

	if getenvs('maillist')=="":    ## 使用配置文件列表地址
		#### 逐行提取邮件列表
		maillist = "maillists"          	     ###  默认的邮件收件人列表文件, 可以维护该文件

		file_object= open(maillist)             
		mailto_list = file_object.readline() 

		while mailto_list: 
			mailto_list=mailto_list.replace('\n','')    #处理换行
			if len(mailto_list)>1:

				if mailto_list.find('#')!= 0:   # 非注释行

					#### 发送
					tosendmaill(mail_host,mail_user,mail_pass,mail_postfix, mailto_list, sub,content)
					####

			mailto_list = file_object.readline() 

		file_object.close()  



	if getenvs('maillist')!="":   ## 使用环境变量地址

		mailto_list=getenvs('maillist')

		tosendmaill(mail_host,mail_user,mail_pass,mail_postfix, mailto_list, sub,content)













