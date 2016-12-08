# -*- coding: utf-8 -*-



######################### 本脚本用于颜色化日志输出， 用于补充 hues 的 windows 部分  

"""
import platform
sysstr = platform.system()  

if sysstr == "Linux":
        import hues

if sysstr == "Windows":
        import winhues as hues

"""

import sys
import time
import ctypes

STD_OUTPUT_HANDLE= -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


####### 字体色

## 暗色
FOREGROUND_BLACK = 0x00 # 黑色
FOREGROUND_BLUE = 0x01 #  蓝色
FOREGROUND_GREEN= 0x02 #  绿色
FOREGROUND_CYAN = 0x03 # 青色
FOREGROUND_RED = 0x04 #  红色
FOREGROUND_PURPLE = 0x05 #   紫色
FOREGROUND_YELLOW = 0x06 # 褐色/黄色
FOREGROUND_WHITE = 0x07 #  白色
FOREGROUND_INTENSITY = 0x08 # 灰色

## 亮色
FOREGROUND_LIGHTBLUE = 0x09 # 亮蓝色

#######  背景色

BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.  灰色



########################### 颜色输出部分

def printf(strs):

        sys.stdout.write(strs)

def resetwhitecolor():
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_WHITE)

def whitecolor(strs):
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_WHITE)  
        printf(strs)
        resetwhitecolor()

def syancolor(strs):
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_CYAN)
        printf(strs)
        resetwhitecolor()

def greencolor(strs):
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_GREEN)  
        printf(strs)
        resetwhitecolor()
        
def redcolor(strs):
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_RED)  
        printf(strs)
        resetwhitecolor()

def yellowcolor(strs):
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_YELLOW)  
        printf(strs)
        resetwhitecolor()

def purplecolor(strs):
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, FOREGROUND_PURPLE)  
        printf(strs)
        resetwhitecolor()


##################### 日志部分


def gettimes():
        
        ISOTIMEFORMAT="%X"
        times=time.strftime(ISOTIMEFORMAT, time.localtime())

        return times


def warn(strs):

        ret=""

        ## 时间
        purplecolor(gettimes())

        ##
        whitecolor(" - ")

        ## 类型
        yellowcolor("WARN")

        ##
        whitecolor(" - ")

        ##
        whitecolor(strs)

        ## 换行
        print("")




def info(strs):

        ret=""

        ## 时间
        purplecolor(gettimes())

        ##
        whitecolor(" - ")

        ## 类型
        syancolor("INFO")

        ##
        whitecolor(" - ")

        ##
        whitecolor(strs)

        ## 换行
        print("")

def log(strs):

        ret=""

        ## 时间
        purplecolor(gettimes())

        ##
        whitecolor(" - ")

        ##
        whitecolor(strs)

        ## 换行
        print("")

def error(strs):

        ret=""

        ## 时间
        purplecolor(gettimes())

        ##
        whitecolor(" - ")

        ## 类型
        redcolor("ERROR")

        ##
        whitecolor(" - ")

        ##
        whitecolor(strs)

        ## 换行
        print("")


def success(strs):


        ret=""

        ## 时间
        purplecolor(gettimes())

        ##
        whitecolor(" - ")

        ## 类型
        greencolor("SUCCESS")

        ##
        whitecolor(" - ")

        ##
        whitecolor(strs)

        ## 换行
        print("")






