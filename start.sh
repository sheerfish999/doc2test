#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/libreoffice/program

################

#  循环次数,  注意 大循环模式 ,  config.py 不要 设置  isSave=1 , 即记录生成, 速度会减慢而且会生成大量的文件
times=1

################  没有采用以下在内存中执行方案,需求不大,而且需要将用例记录拷贝出来  ########

#  临时目录相对路径
#  tmppath=memrun
#  echo  $PWD/${tmppath}

### 临时目录挂载到内存中
## sudo fuser -m -k -s  $PWD/${tmppath}   ## 运行这行会造成桌面重启
#sudo umount -f $PWD/${tmppath}
#sudo mount -t tmpfs -o size=128m tmpfs $PWD/${tmppath}

#cp -r * $PWD/${tmppath}/

for (( i=1; i<=${times}; i++ ))
do
	#python  $PWD/${tmppath}/modules/caserun.py
	python  ./modules/caserun.py

	echo Cycle:${i}
done


#sudo umount -f $PWD/${tmppath}



