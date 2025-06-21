---
title: 简易Shell实现
date: 2022-05-30 19:53:57
tags: ['cpp']
img: images/img20220530195308.png
---

## 描述
np
实现了一个简单的shell,  主要通过C语言来实现。[项目地址](https://github.com/zhkgo/codeTemplate/tree/main/inner_cpp/shellproject)

主要有以下功能。

1. 向标准输出打印一个命令提示符
2. 从标准输入读取一个命令
3. 判断要执行哪些命令

对内置命令进行了解析，主要包括。

1）`cd`

```shell
cd xxx
```

进入某个目录（上述代码会进入`xxx`目录）——你可以查阅`chdir()`函数的用法。如果目录不存在，则要打印`xxx: No such file or directory`并换行，其中`xxx`表示输入的目录名称。

2）`exit`

```shell
exit
```

退出 shell 程序，在`execute`函数中直接返回 000。在其他情况下，`execute`返回一个非零值即可。

3）显示历史命令

```shell
!#
```

所有输入的命令都保存在一个`log_t`中，这个命令的作用是显示所有输入过的命令，每个占一行。**从栈底元素开始输出，`log_t`变量名为`Log`，定义在 shell.h 文件中，请勿修改。**

**注意，以`!`开头的所有命令都不会被放入命令栈中。**

4）根据前缀查找命令

```shell
!prefix
```

查找是否曾经输入过包含前缀`prefix`的命令，如果找到（**如果有多个，只找最靠近栈底的一个**），则执行这条命令，如果没有，则返回`No Match`换行。新执行的命令也会被放入栈顶。

5）`ls`

```shell
ls
```

跟 bash shell 的`ls`命令一样，列举当年目录下所有子目录和文件——你可以直接用`system()`函数执行这个命令。

执行外部命令

需要使用`fork()`和`exec()`等函数来执行一个外部命令——如果执行失败，则输出`%s: no such command`换行。

如果外部命令无法执行，则输出`XXX: no such command`并换行，其中`XXX`表示输入的完整外部命令。注意，你必须确保无论执行成功还是失败，都 **不要有额外的子进程留下**。

**即使外部命令未正确执行，也依然将这条命令放入命令栈中。**

## 实现部分

主要实现了`shell.c`和`log.c`两个模块。

`shell.c`负责解析读取到的命令。用到了`system`,`execv`,`fork`等系统调用。

```c
#include "shell.h"
/**
 * shell的入口
 */
void prefix() {
    char *cwd=getcwd(NULL,0);
    printf("%s$ ",cwd);
    free(cwd);
}
void list_log(log_t *log){
    node *p=log->head;
    while(p){
        printf("%s\n",p->cmd);
        p = p->next;
    }
}
void parse_cd(){
    char *arg = strtok(NULL," ");
    if(strtok(NULL," ") != NULL){
        printf("bash: cd: too many arguments\n");
    }else{
        int res=chdir(arg);
        if(res){
           printf("%s: No such file or directory\n",arg); 
        }
    }
}
void parse_ls(char *cmd){
    system(cmd);
}
void parse_outer(char *path){
    int pid = fork();
    if(pid){
        waitpid(pid,NULL,0);
    }else{
        char* args[100];
        args[0] = path;
        int c=1;
        while((args[c]=strtok(NULL," ")) != NULL)c++;
        execv(path,args);
        printf("%s: no such command\n",path);
        exit(-1);
    }
}
int execute(char* buffer) {
    if(buffer==NULL || buffer[0]=='\0')
        return 1;
    if(buffer[0] == '!'){
        if(buffer[1] == '#'){
            list_log(&Log);
        }else{
            char *res=log_search(&Log,buffer+1);
            if(res==NULL){
                printf("No Match\n");
            }else{
                return execute(res);
            }
        }
    }else{
        log_push(&Log,buffer);
        char *tmp=strtok(buffer," ");
        if(match(tmp,"cd")){
            parse_cd();
        }else if(match(tmp,"exit")){
            return 0;
        }else if(match(tmp,"ls")){
            parse_ls(Log.tail->cmd);
        }else{
            parse_outer(tmp);
        }
    }
    return 1;
}
```

`log.c`负责命令栈相关操作。

```c
/** @file log.c */
#include <stdlib.h>
#include <string.h>
#include "log.h"

/**
对log进行初始化，log的“构造函数”
 */

void log_init(log_t *l) {
    l->head = NULL;
    l->tail = NULL;
}

/**
销毁一个log，释放所有内存空间，log的“析构函数”
 */

void log_destroy(log_t* l) {
    node *p=l->head;
    node *nxt;
    while(p){
        nxt=p->next;
        free(p->cmd);
        free(p);
        p=nxt;
    }
    l->tail = l->head = NULL;
}

/**
向log中推入一个字符串，你可以将log视为一个由链表组成的栈
 */

void log_push(log_t* l, const char *item) {
    node *cur = (node*) malloc(sizeof(node));
    cur->cmd = malloc(strlen(item)+1);
    strcpy(cur->cmd,item);
    cur->next = NULL;
    if(l->head == NULL){
        l->head = l->tail = cur;
    }else{
        l->tail->next = cur;
        l->tail = cur;
    }
}

int match(const char *str,const char *prefix){
    while(*str != '\0' && *prefix != '\0'){
        if(*str != *prefix)
            return 0;
        ++str;
        ++prefix;
    }
    return *prefix == '\0';
}
/**
搜索log中是否含有对应前缀的字符串
 */
char *log_search(log_t* l, const char *prefix) {
    node *cur = l->head;
    while(cur){
        if(match(cur->cmd,prefix)){
            return cur->cmd;
        }
        cur=cur->next;
    }
    return NULL;
}
```
