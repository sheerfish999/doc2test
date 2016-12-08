

##############   设置为 1 返回调试具体信息

isDebug=0
#isDebug=1

##############   设置为 1 生成测试记录文件

isSave=0
#isSave=1


##############  接口返回的超时时间  单位 秒

timeouts=5

##############  是否开启邮件发送

sendmail=0
#sendmail=1



############## 邮件服务器配置

## 可能被 子函数 exec, 这种情况下必须 global

global mail_host
global mail_user
global mail_pass
global mail_postfix

mail_host="pop3.163.com"   
mail_user="username"   
mail_pass="password"   
mail_postfix="163.com"  #发件箱的后缀




