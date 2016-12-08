# -*- coding: utf-8 -*-

import sys,os
import codecs


#######################  本脚本用于配合 jenkins 支持


######  获得环境变量

def getenvs(string):

	try:
		envs=os.environ[string]   
		return envs
	except:
		return ""	  
