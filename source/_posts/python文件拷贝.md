---
title: python文件拷贝
date: 2018-06-18 10:11:54
tags: python
img: images/7604477-973ee37916aff7cf.jpg
---
### **背景**

&#160;&#160;&#160;&#160;&#160;&#160;&#160;前段时间准备六级的时候，拿到了一个光盘，里面有很多听力，但是听力分为很多文件夹，还有很多听力的字幕（.lrc）,就想要把里面的听力都拷贝出来全部放到我的手机某个文件夹里，但是一个个文件夹打开，全选，拷贝，粘贴，这一系列操作显得效率不高，因此我想到了使用python来实现这一系列功能。

### **实现**

&#160;&#160;&#160;&#160;&#160;&#160;&#160;制作出了一个可以实现**筛选该程序所在目录下的所有文件**，通过关键词进行筛选，然后复制到目标文件夹里，高效得实现了文件的整理。还可以用到一些资料的整理上，比如想整理所有关于毕业设计的资料，我就把毕业设计作为关键词，（当然平常命名的时候还得要规范一点），然后把我的程序放到磁盘根目录下运行，就能筛选出当前磁盘下的全部含关键词的文件了。代码如下

```python
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 13:50:09 2018

@author: zhkgo
"""

import os
import re
import shutil
def findmykey(keyword,head=os.path.abspath('.')):
    dirs=set()
    files=[]
    pattern='.*'+keyword+'.*'
    dirs.add(head)
    while(len(dirs)!=0):
        mydir=dirs.pop()
        for x in os.listdir(mydir):
          #  print(x)
            absp=os.path.join(mydir,x)
            if os.path.isdir(absp):
                dirs.add(absp)           
            elif os.path.isfile(absp):
            #    print(pattern+' '+keyword)
             #   print("isfile")    
                if re.match(pattern,x):
                    files.append(absp)
    return files
            
        
 
#shutil.copyfile(r'F:\华研外语\2.六级2套预测\Model Test 2.lrc','F:\\fas\\'+'madel.lrc')
goal="" 
goal=input('复制到哪里？ (例如 F:\\文档)\n')
while not os.path.exists(goal):  
   print("文件夹不存在！")         
   goal=input('复制到哪里？ (例如 F:\\文档)\n')
keyword=input('输入关键词(例如 jpg)\n')
ret=findmykey(keyword)
#print(ret)

try:
    for x in ret:
        pa=os.path.join(goal,os.path.split(x)[1])    
   # print(pa)
        shutil.copyfile(x,pa)
except:
    print("复制失败")
else:
    print('复制完成')
```

### **最后**

&#160;&#160;&#160;&#160;&#160;&#160;&#160;代码肯定是不完善的，没有考虑很多情况，目前这个代码实现的时候 ，对于重复的文件，后面进入的会覆盖已经存在的文件。
&#160;&#160;&#160;&#160;&#160;&#160;&#160;这个还可以加入输入正则表达式来进行匹配文件名，这样就不是单纯的文件名匹配了，还可以加入运算符，如 “与”，“或”等来进行匹配。就写到这里吧，有错误希望能够指正。
