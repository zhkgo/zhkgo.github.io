---
title: 魔兽世界之开战-代码实现
date: 2022-05-05 22:03:50
tags: ['cpp','魔兽世界']
img: images/img20220506152352.png
---

> 回忆起之前上过北大郭炜老师的课程，里面有个大作业借用了魔兽世界的一些IP,设计了一个类似红蓝双方对战的场景,正好自己写C++算法多，但是做项目少，就再次写一下这个作业，并且把每个模块抽离出来制作。

[项目地址](https://github.com/zhkgo/codeTemplate/tree/main/gameMoudle/World_of_Warcraft_3)

## 具体场景

**描述**

魔兽世界的西面是红魔军的司令部，东面是蓝魔军的司令部。两个司令部之间是依次排列的若干城市，城市从西向东依次编号为1,2,3 .... N ( N <= 20)。红魔军的司令部算作编号为0的城市，蓝魔军的司令部算作编号为N+1的城市。司令部有生命元，用于制造武士。

两军的司令部都会制造武士。武士一共有dragon 、ninja、iceman、lion、wolf 五种。每种武士都有编号、生命值、攻击力这三种属性。

双方的武士编号都是从1开始计算。红方制造出来的第n 个武士，编号就是n。同样，蓝方制造出来的第n 个武士，编号也是n。

武士在刚降生的时候有一个初始的生命值，生命值在战斗中会发生变化，如果生命值减少到0（生命值变为负数时应当做变为0处理），则武士死亡（消失）。

武士可以拥有武器。武器有三种，sword, bomb,和arrow，编号分别为0,1,2。

sword的攻击力是使用者当前攻击力的20%(去尾取整)。

bomb的攻击力是使用者当前攻击力的40%(去尾取整)，但是也会导致使用者受到攻击，对使用者的攻击力是对敌人取整后的攻击力的1/2(去尾取整)。Bomb一旦使用就没了。

arrow的攻击力是使用者当前攻击力的30%(去尾取整)。一个arrow用两次就没了。

武士降生后就朝对方司令部走，在经过的城市如果遇到敌人（同一时刻每个城市最多只可能有1个蓝武士和一个红武士），就会发生战斗。战斗的规则是：

1. 在奇数编号城市，红武士先发起攻击
2. 在偶数编号城市，蓝武士先发起攻击
3. 战斗开始前，双方先对自己的武器排好使用顺序，然后再一件一件地按顺序使用。编号小的武器，排在前面。若有多支arrow，用过的排在前面。排好序后，攻击者按此排序依次对敌人一件一件地使用武器。如果一种武器有多件，那就都要用上。每使用一件武器，被攻击者生命值要减去武器攻击力。如果任何一方生命值减为0或小于0即为死去。有一方死去，则战斗结束。
4. 双方轮流使用武器，甲用过一件，就轮到乙用。某一方把自己所有的武器都用过一轮后，就从头开始再用一轮。如果某一方没有武器了，那就挨打直到死去或敌人武器用完。武器排序只在战斗前进行，战斗中不会重新排序。
5. 如果双方武器都用完且都还活着，则战斗以平局结束。如果双方都死了，也算平局。
6. 有可能由于武士自身攻击力太低，而导致武器攻击力为0。攻击力为0的武器也要使用。如果战斗中双方的生命值和武器的状态都不再发生变化，则战斗结束，算平局。
7. 战斗的胜方获得对方手里的武器。武士手里武器总数不超过10件。缴获武器时，按照武器种类编号从小到大缴获。如果有多件arrow，优先缴获没用过的。
8. 如果战斗开始前双方都没有武器，则战斗视为平局。如果先攻击方没有武器，则由后攻击方攻击。

不同的武士有不同的特点。

编号为n的dragon降生时即获得编号为n%3 的武器。dragon在战斗结束后，如果还没有战死，就会欢呼。

编号为n的ninjia降生时即获得编号为n%3 和(n+1)%3的武器。ninja 使用bomb不会让自己受伤。

编号为n的iceman降生时即获得编号为n%3 的武器。iceman每前进一步，生命值减少10%(减少的量要去尾取整)。

编号为n的lion降生时即获得编号为n%3 的武器。lion 有“忠诚度”这个属性，其初始值等于它降生之后其司令部剩余生命元的数目。每前进一步忠诚度就降低K。忠诚度降至0或0以下，则该lion逃离战场,永远消失。但是已经到达敌人司令部的lion不会逃跑。lion在己方司令部可能逃跑。

wolf降生时没有武器，但是在战斗开始前会抢到敌人编号最小的那种武器。如果敌人有多件这样的武器，则全部抢来。Wolf手里武器也不能超过10件。如果敌人arrow太多没法都抢来，那就先抢没用过的。如果敌人也是wolf，则不抢武器。

**以下是不同时间会发生的不同事件：**

在每个整点，即每个小时的第0分， 双方的司令部中各有一个武士降生。

红方司令部按照iceman、lion、wolf、ninja、dragon 的顺序制造武士。

蓝方司令部按照lion、dragon、ninja、iceman、wolf 的顺序制造武士。

制造武士需要生命元。

制造一个初始生命值为m 的武士，司令部中的生命元就要减少m 个。

如果司令部中的生命元不足以制造某本该造的武士，那就从此停止制造武士。

在每个小时的第5分，该逃跑的lion就在这一时刻逃跑了。

在每个小时的第10分：所有的武士朝敌人司令部方向前进一步。即从己方司令部走到相邻城市，或从一个城市走到下一个城市。或从和敌军司令部相邻的城市到达敌军司令部。

在每个小时的第35分：在有wolf及其敌人的城市，wolf要抢夺对方的武器。

在每个小时的第40分：在有两个武士的城市，会发生战斗。

在每个小时的第50分，司令部报告它拥有的生命元数量。

在每个小时的第55分，每个武士报告其拥有的武器情况。

武士到达对方司令部后就算完成任务了，从此就呆在那里无所事事。

任何一方的司令部里若是出现了敌人，则认为该司令部已被敌人占领。

任何一方的司令部被敌人占领，则战争结束。战争结束之后就不会发生任何事情了。

**给定一个时间，要求你将从0点0分开始到此时间为止的所有事件按顺序输出。事件及其对应的输出样例如下：**

1) 武士降生

输出样例：000:00 blue dragon 1 born

表示在0点0分，编号为1的蓝魔dragon武士降生

如果造出的是lion，那么还要多输出一行，例:

000:00 blue lion 1 born

Its loyalty is 24

表示该lion降生时的忠诚度是24

2) lion逃跑

输出样例：000:05 blue lion 1 ran away

表示在0点5分，编号为1的蓝魔lion武士逃走

3) 武士前进到某一城市

输出样例：

000:10 red iceman 1 marched to city 1 with 20 elements and force 30

表示在0点10分，红魔1号武士iceman前进到1号城市，此时他生命值为20,攻击力为30

对于iceman,输出的生命值应该是变化后的数值

4) wolf抢敌人的武器

000:35 blue wolf 2 took 3 bomb from red dragon 2 in city 4

表示在0点35分，4号城市中，红魔1号武士wolf 抢走蓝魔2号武士dragon 3个bomb。为简单起见，武器不写复数形式

5) 报告战斗情况

战斗只有3种可能的输出结果：

000:40 red iceman 1 killed blue lion 12 in city 2 remaining 20 elements

表示在0点40分，1号城市中，红魔1号武士iceman 杀死蓝魔12号武士lion后，剩下生命值20

000:40 both red iceman 1 and blue lion 12 died in city 2

注意，把红武士写前面

000:40 both red iceman 1 and blue lion 12 were alive in city 2

注意，把红武士写前面

6) 武士欢呼

输出样例：003:40 blue dragon 2 yelled in city 4

7) 武士抵达敌军司令部

输出样例：001:10 red iceman 1 reached blue headquarter with 20 elements and force 30

（此时他生命值为20,攻击力为30）对于iceman,输出的生命值和攻击力应该是变化后的数值

8) 司令部被占领

输出样例：003:10 blue headquarter was taken

9) 司令部报告生命元数量

000:50 100 elements in red headquarter

000:50 120 elements in blue headquarter

表示在0点50分，红方司令部有100个生命元，蓝方有120个

10) 武士报告情况

000:55 blue wolf 2 has 2 sword 3 bomb 0 arrow and 7 elements

为简单起见，武器都不写复数形式。elements一律写复数，哪怕只有1个

交代武器情况时，次序依次是：sword,bomb, arrow。

**输出事件时：**

首先按时间顺序输出；

同一时间发生的事件，按发生地点从西向东依次输出. 武士前进的事件, 算是发生在目的地。

在一次战斗中有可能发生上面的 5 至 6 号事件。这些事件都算同时发生，其时间就是战斗开始时间。一次战斗中的这些事件，序号小的应该先输出。

两个武士同时抵达同一城市，则先输出红武士的前进事件，后输出蓝武士的。

对于同一城市，同一时间发生的事情，先输出红方的，后输出蓝方的。

显然，8号事件发生之前的一瞬间一定发生了7号事件。输出时，这两件事算同一时间发生，但是应先输出7号事件

虽然任何一方的司令部被占领之后，就不会有任何事情发生了。但和司令部被占领同时发生的事件，全都要输出。

**输入**

第一行是t,代表测试数据组数

每组样例共三行。

第一行，4个整数 M,N,K, T。其含义为：
每个司令部一开始都有M个生命元( 1 <= M <= 100000)
两个司令部之间一共有N个城市( 1 <= N <= 20 )
lion每前进一步，忠诚度就降低K。(0<=K<=100)
要求输出从0时0分开始，到时间T为止(包括T) 的所有事件。T以分钟为单位，0 <= T <= 6000

第二行：五个整数，依次是 dragon 、ninja、iceman、lion、wolf 的初始生命值。它们都大于0小于等于200

第三行：五个整数，依次是 dragon 、ninja、iceman、lion、wolf 的攻击力。它们都大于0小于等于200

**输出**

对每组数据，先输出一行：

Case n:

如对第一组数据就输出 Case 1:

然后按恰当的顺序和格式输出到时间T为止发生的所有事件。每个事件都以事件发生的时间开头，时间格式是“时: 分”，“时”有三位，“分”有两位。

**样例输入**

```
1
20 1 10 400
20 20 30 10 20
5 5 5 5 5
```

**样例输出**

```
Case 1:
000:00 blue lion 1 born
Its loyalty is 10
000:10 blue lion 1 marched to city 1 with 10 elements and force 5
000:50 20 elements in red headquarter
000:50 10 elements in blue headquarter
000:55 blue lion 1 has 0 sword 1 bomb 0 arrow and 10 elements
001:05 blue lion 1 ran away
001:50 20 elements in red headquarter
001:50 10 elements in blue headquarter
002:50 20 elements in red headquarter
002:50 10 elements in blue headquarter
003:50 20 elements in red headquarter
003:50 10 elements in blue headquarter
004:50 20 elements in red headquarter
004:50 10 elements in blue headquarter
005:50 20 elements in red headquarter
005:50 10 elements in blue headquarter
```

**提示**

请注意浮点数精度误差问题。OJ上的编译器编译出来的可执行程序，在这方面和你电脑上执行的程序很可能会不一致。5 *0.3 的结果，有的机器上可能是 15.00000001，去尾取整得到15,有的机器上可能是14.9999999，去尾取整后就变成14。因此,本题不要写 5* 0.3，要写 5 * 3 / 10。

**来源**

Guo Wei

## 部分代码实现

完整的代码可以去[github](https://github.com/zhkgo/codeTemplate/tree/main/gameMoudle/World_of_Warcraft_3)看,这边只给出了一些类的声明。

城市类声明

```cpp
#ifndef CITY_H
#define CITY_H
#include "warriors.h"
#include "arm.h"
#include "world.h"
class Warrior;
class City{
public:
 int c_id;//城市编号
 list<Warrior*> red_warriors,blue_warriors;//红蓝阵营的武士
 City(int c_id):c_id(c_id){
 }
 void addWarrior(Warrior* p);//武士进入该城市
 void removeWarrior(Warrior* p);//武士离开该城市
 list<Warrior*> battle(Warrior* w1,Warrior* w2);//两个武士在该城市展开战斗，返回存活的武士
 void judge();//判断该城市是否有战斗发生，如果有则展开战斗
 void wolfPlunder();//如果该城市有wolf，则他可以开始抢夺武器
 void report(); //该城市报告有哪些武士到达了此城市
 void warriorReport();//在该城市的武士报告自己的武器持有情况
 void lionRun();//在该城市的lion若忠诚度不够，则可以逃跑了！
};
#endif
```

世界类声明

```cpp
#ifndef World_H
#define World_H
#include<vector>
#include<string>
#include<cstdio>
#include<list>
using namespace std;

#define MESSAGE_LENGTH 300
#include "city.h"
class Headquarter;
class City;
//世界类
class World{
public:
 int now;
 Headquarter *h1,*h2;
 vector<City> citys;
 World():now(0){
 }
 void reset(Headquarter* _h1,Headquarter *_h2,int N);//重启世界，h1为红阵营，h2为蓝阵营，N为中间城市数量
 void log(const string &message,bool timer=true);//世界日志
 bool addTime();//时间流逝 返回true代表有总部被占领
};
extern World mlog;
#endif
```

武士类声明

```cpp
#ifndef WARRIORS_H
#define WARRIORS_H

#include "world.h" 
#include "arm.h" 
extern const string names[5];
//武士类
class Warrior{ 
public:
 static int MAX_ARMS;//武士最多持有武器数量
 int id;//武士编号
 string name;//武士类型 
 int health;//武士生命值
 int ack;//武士攻击力
 list<Arm*> arms;//武士持有的武器
 int pos;//武士所在位置
 string headq;//所属司令部
 decltype(arms.begin()) curArm;//武士下一个要使用的武器 
 Warrior(int id,const string &name,int health,int ack,const string& headq,int num);
 void place(int x){//放置武士
  pos=x;
 }
 virtual bool goAhead(int dir);//前进
 void prepare();//准备战斗
 bool isDead(){//是否死亡
  return health<=0;
 }
 bool hasArms(){//是否拥有武器
  return arms.size()!=0;
 }
 void getArmFrom(Warrior* enemy);//从死亡的敌人那边抢夺武器
 string totName(){//武士全名 总部+自身类别+编号
  return headq+" "+name+" "+to_string(id);
 }
 bool noMoreChange();//表示武士不会再造成任何伤害，并且武器状态不会变化
 void report();//武士报告自身武器持有情况
 virtual bool attack(Warrior* enemy);//武士攻击敌人
 virtual bool beAttacked(int harm);//武士受到伤害
 virtual ~Warrior(){
  for(auto &p:arms){
   delete p;
  }
 }
};

class dragon:public Warrior{
public:
 double morale;//士气
 dragon(int id,int health,int ack,double morale,const string& headq,int num);
 void yelled(int c_id);//武士欢呼
};
class ninja:public Warrior{
public:
 ninja(int id=1,int health=10,int ack=5,const string& headq="red",int num=1)
 :Warrior(id,"ninja",health,ack,headq,num){
  arms.push_back(ArmFactory::product(id%3));
  arms.push_back(ArmFactory::product((id+1)%3));
 }
};

class iceman:public Warrior{
public:
 iceman(int id=1,int health=10,int ack=5,const string& headq="red",int num=1)
 :Warrior(id,"iceman",health,ack,headq,num){
  arms.push_back(ArmFactory::product(id%3));
 }
 virtual bool goAhead(int dir){//iceman前进 减少生命值
  health -= health/10;
  return Warrior::goAhead(dir);
 }
};
class lion:public Warrior{
public:
 int loyalty;
 int lionk;
 lion(int id,int health,int ack,int loyalty,const string& headq,int num,int lionk);
 virtual bool goAhead(int dir);//lion前进 减少忠诚度
 void run();
};

class wolf:public Warrior{
public:
 wolf(int id,int health,int ack,const string& headq,int num)
 :Warrior(id,"wolf",health,ack,headq,num){
 }
 void wolfgetArmFrom(Warrior* enemy,int c_id);//wolf在某城市抢夺武器
};
#endif
```

武器类声明

```cpp
#ifndef ARM_H
#define ARM_H

#include <string>
using namespace std;
extern string armNames[3];

class Warrior;
class Arm{
public:
 int arm_id;//武器编号
 int ackp;//武器伤害百分比
 int used;//武器耐久度
 Arm(int arm_id=0,int ackp=20,int used=1000):arm_id(arm_id),ackp(ackp),used(used){
 }
 static bool arm_cmp_use(Arm* a1,Arm* a2);//武器使用优先级 优先编号最小的 优先使用耐久度较低的
 static bool arm_cmp_get(Arm* a1,Arm* a2);//武器抢夺优先级 优先编号最小的 优先抢夺耐久度较高的
 virtual bool attack(Warrior* owner,Warrior* enemy);//使用该武器进攻
 virtual ~Arm(){}
};
//宝剑
class sword:public Arm{
public:
 sword():Arm(0,20,10000000){
 }
};
//炸弹
class bomb:public Arm{
public:
 bomb():Arm(1,40,1){
 }
};
//弓箭
class arrow:public Arm{
public:
 arrow():Arm(2,30,2){
 }
};
//武器生产工厂
class ArmFactory{
public:
 static Arm* product(int id);//生产编号为id的武器
};
#endif
```

司令部类声明

```cpp
#ifndef HEADQUATER_H
#define HEADQUATER_H
#include "arm.h"
#include "world.h"
#include "warriors.h"
extern int HP[5];
extern int ACK[5];

class Headquarter{
private:
 int power;//司令部生命元
 vector<int> order;//武士生产顺序
 vector<int> count;//武士数量
 int bound;//ֹͣ停止生成边界，保留使用
 list<Warrior*> warriors;//武士列表 
 int w_id;//下一个生成武士的编号
 int cur; //指向武士生产顺序，表示下一个生产的武士所在下标
 int pos;//总部所在位置
 int lionk;//武士lion每前进一步下降的忠诚度
 int dir;// 该总部武士的前进方向
 list<Warrior*> enemys; //到达该总部的敌人，当前最多只有一个，保留为列表
public:
 string name;//总部名称
 bool stop;//总部是否停止生产武士
 Headquarter(vector<int>& order,const string &name="headquarter",int power=100,int pos=0,int lionk=1,int dir=-1)
 :name(name),power(power),order(order),w_id(1),count(order.size(),0),pos(pos),lionk(lionk),dir(dir){
  bound=1e9+7;
  stop=false;
  for(auto &p:order){
   bound=min(bound,HP[p]);
  }
  cur=0;
 }
 void enemysReach(Warrior* wa){//敌人抵达总部
  enemys.push_back(wa);
 }
 Warrior* born(int hero_id){//总部生产指定编号的武士
  if(power>=HP[hero_id]){
   power-=HP[hero_id];
   count[hero_id]+=1;
   Warrior* hero=nullptr;
   switch (hero_id){
    case 0:
     hero =static_cast<Warrior*>(new dragon(w_id++,HP[hero_id],ACK[hero_id],1.0*power/HP[hero_id],name,count[hero_id]));
     break;
    case 1:
     hero =static_cast<Warrior*>(new ninja(w_id++,HP[hero_id],ACK[hero_id],name,count[hero_id]));
     break;
    case 2:
     hero =static_cast<Warrior*>(new iceman(w_id++,HP[hero_id],ACK[hero_id],name,count[hero_id]));
     break;
    case 3:
     hero =static_cast<Warrior*>(new lion(w_id++,HP[hero_id],ACK[hero_id],power,name,count[hero_id],lionk));
     break;
    case 4:
     hero =static_cast<Warrior*>(new wolf(w_id++,HP[hero_id],ACK[hero_id],name,count[hero_id]));
     break;
   }
   return hero;
  }
  return nullptr;
 }
 void lionRun(){//lion 逃跑，移除指定武士
  warriors.remove_if([](Warrior* p){
   lion* lp=dynamic_cast<lion*>(p);
   if(lp!=nullptr && lp->loyalty<=0){
    delete p;
    return true;
   }
   return false;
  });
 }
 void clearDead(){//清理死去的武士
  warriors.remove_if([](Warrior* p){
   if(p->isDead()){
    delete p;
    return true;
   }
   return false;
  });
 }
 void goAhead(){//所有武士前进一步 
  for(auto &p:warriors){
   p->goAhead(dir);
  }
 }
 void report(){//报告总部自身生命元情况
  string message=to_string(power)+" elements in "+name+" headquarter";
  mlog.log(message);
 }
 void warriorReport(){//该总部的武士报告自身武器情况，（保留使用，原题要求按照城市顺序报告）
  for(auto &p:warriors){
   p->report();
  }
 }
 bool enemyReport(){//该总部如果存在敌人则被占领并播报。若被占领则返回true结束此局游戏
  for(auto &p:enemys){
   char message[MESSAGE_LENGTH];
   sprintf(message,"%s reached %s headquarter with %d elements and force %d"
   ,p->totName().c_str(),name.c_str(),p->health,p->ack);
   mlog.log(message);
  }
  if(enemys.size()!=0){
   mlog.log(name+" headquarter was taken");
   return true;
  }
  return false;
 }
 bool bornNext(){//生产下一个武士
  if(stop){
   return false;
  }
  Warrior* war;
  war=born(order[cur]);
  cur=(cur+1)%order.size();
  if(war==nullptr){
   stop=true;
   return false;
  }
  war->place(pos);
  warriors.push_back(war);
  return true;
 }
 ~Headquarter(){
  for(auto &wa:warriors){
   delete wa;
  }
 }
};
#endif 
```

## 收获

### 实践了一些知识

1. 成员函数的声明和实现分离，很大程度上能解决循环依赖问题。
2. 成员函数在声明后，不需要在实现部分注明其是否static 是否virtual等等。
3. 成员函数的默认参数只需要在实现或者声明部分注明即可，只能选其中一个。一般选择在声明部分设置默认参数，这样一来方便修改，二来能够在其他地方调用的时候能够正确匹配到该成员函数。
4. 一些全局变量在.cpp文件中定义，在.h中extern可以在一定程度上解决变量重复定义问题。
5. 优雅的系统性设计有助于代码的拓展与修改。

### 内存泄露检测工具的初次使用

内存泄露工具valgrind的第一次使用。对于new出来的每把武器，我都交给战士自身来delete。对于new出来的每个武士，我都交给其所属的司令部来delete，这样可以防止重复delete的问题。写完代码后我突发奇想用内存泄露检测工具来看看我是否存在内存泄露。然后我满怀期待的输入了

```bash
 valgrind --leak-check=full --show-reachable=yes --track-origins=yes  -v ./war3 <in.txt
```

然后就返回给了我这个

```bash
==4067047== 168 bytes in 7 blocks are definitely lost in loss record 15 of 15
==4067047==    at 0x483BE63: operator new(unsigned long) (in /usrb/x86_64-linux-gnualgrindgpreload_memcheck-amd64-linux.so)
==4067047==    by 0x10B647: ArmFactory::product(int) (in /home/zhkgo/clearn/war/war3)
==4067047==    by 0x1136CA: iceman::iceman(int, int, int, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, int) (in /home/zhkgo/clearn/war/war3)
==4067047==    by 0x113B73: Headquarter::born(int) (in /home/zhkgo/clearn/war/war3)
==4067047==    by 0x114408: Headquarter::bornNext() (in /home/zhkgo/clearn/war/war3)
==4067047==    by 0x1130A2: World::addTime() (in /home/zhkgo/clearn/war/war3)
==4067047==    by 0x10E769: main (in /home/zhkgo/clearn/war/war3)
==4067047== 
==4067047== LEAK SUMMARY:
==4067047==    definitely lost: 1,464 bytes in 61 blocks
==4067047==    indirectly lost: 0 bytes in 0 blocks
==4067047==      possibly lost: 0 bytes in 0 blocks
==4067047==    still reachable: 0 bytes in 0 blocks
==4067047==         suppressed: 0 bytes in 0 blocks
==4067047== 
==4067047== ERROR SUMMARY: 15 errors from 15 contexts (suppressed: 0 from 0)
```

虽然没学过valgrind的，但是它的提示确实很好用，很明显可以看到哪里new出来的对象出现了内存泄露。

这边可以看到调用栈，生产的武器有些没有被销毁，我就回头去看了一下代码。在武器耐久度为0的时候，我直接从武士的成员list中移除了这个武器，并没有delete，这样在武士类被析构的时候，武器也不会出现在list里，就不会被delte，所以就导致了内存泄露。最后通过加上delete自然就解决了这个问题。 其实最好的办法是把移除武器这个操作封装成一个成员函数来使用，默认在移除武器的时候delete这个武器，也可以设置不delete(用于抢夺武器的情况),这样就优雅很多了。
