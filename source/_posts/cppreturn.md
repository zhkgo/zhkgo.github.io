---
title: 浅探C++返回局部对象的过程
date: 2022-09-15 10:01:59
tags: [cpp]
---

> 之前学习到过在返回值的时候,c++会在返回局部对象的时候进行返回值优化，现在想通过实践来一谈究竟。

## 右值引用(第一层)
C++11新增了一种引用，可以引用右值，又称右值引用。这也为函数返回值的优化提供了条件。先看这样一段代码。
```cpp

#include <iostream>
using namespace std;
class A {
public:
    int d = 0;
    A() { cout << "Create A\n"; }

    ~A() { cout << "Destroy A\n"; }

    A(const A &) { cout << "Copy A\n"; }

    A(A &&) { cout << "Move A\n"; }

    A& operator=(const A&a)
    {
        std::cout << "copy assignment" << std::endl;
        return *this;
    }

    A& operator=(A &&a) {
        cout << "move assignment\n";
        return *this;
    }
};
A DoA() {
    A a1;
    return a1;
}
int main() {
    A a; 
    a = DoA();
    return 0;
}
```
从程序设计者的角度来看，有一个显而易见的优化，就是DoA()中的变量a1是局部对象，在返回之后会被销毁，既然要被销毁，为何不使用右值引用来对这个a1对象中的一些元素加以利用，故在返回时会调用对象的右值引用构造函数或者移动赋值函数。
根据c++函数返回局部对象的过程，此时函数返回一个局部对象应该分为两步。
1. 局部对象 -> 临时对象。 调用**右值构造函数**将局部对象a1临时构造在栈上新开辟的空间上。
2. 临时对象-> 外部对象。 调用**移动赋值构造函数**将临时对象赋值给调用处的左值。

## 返回值优化(第二层)

为了验证上面的结果，我们采用g++(Ubuntu 7.5.0-3ubuntu1~18.04)对其进行编译运行。
输出结果如下。
```
Create A
Create A
move assignment
Destroy A
Destroy A
```
在这里发现，少了一个调用右值构造函数的过程。这时候就要提到C++编译器的返回值优化(RVO)了，编译器在发现这个临时对象最终会作为右值传输给外部对象a,那么为什么不直接把这个局部对象传输给外部对象a呢？故编译器对此过程进行了优化，减少了一次右值构造函数的调用。

当然我们可以尝试看看关掉这个优化(编译时加入-fno-elide-constructors)，结果是否如我们之前所料呢？
```
g++ test.cpp  -fno-elide-constructors 
output:
Create A
Create A
Move A
Destroy A
move assignment
Destroy A
Destroy A
```
此时的输出结果就和我们之前预料的一样了。

## 返回值优化(第三层)

返回值优化就到此结束了吗？其实并没有。
看下面这样一段代码。想像一下有几个A类对象会被创建并最终销毁？
```cpp
#include <iostream>
using namespace std;
class A {
public:
    int d = 0;
    A() { cout << "Create A\n"; }

    ~A() { cout << "Destroy A\n"; }

    A(const A &) { cout << "Copy A\n"; }

    A(A &&) { cout << "Move A\n"; }

    A& operator=(const A&a)
    {
        std::cout << "copy assignment" << std::endl;
        return *this;
    }

    A& operator=(A &&a) {
        cout << "move assignment\n";
        return *this;
    }
};
A DoA() {
    A a1;
    a1.d = 5;
    return a1;
}
int main() {
    A a = DoA();
    return 0;
}
```

如果你回答两个，说一个是局部对象a1,一个是外部对象a,那么你还是在第二层。而编译器的设计者想到了第三层。就是说既然这个局部对象a1迟早会被销毁，并且把他的所有内容交给一个尚未构造的外部对象a,为何不直接在外部对象a上构造这个局部对象。
所以此时只有一个A类对象被构造，输出如下。
```
Create A
Destroy A
```
为了更加严格的验证这个不是因为其他原因导致的看似一个对象构造。我们把外部对象a和局部对象a1的地址也输出来。
```
Create A
0x7ffdb4b99c14
0x7ffdb4b99c14
Destroy A
```
可以发现，函数内部的对象和外部对象居然是同一个地址，也印证了之前的说法。

## 返回值优化(第四层)

那么第三层优化是否有条件限制呢？接着看下一段代码。
```cpp
#include <iostream>
using namespace std;
class A {
public:
    int d = 0;
    A() { cout << "Create A\n"; }

    ~A() { cout << "Destroy A\n"; }

    A(const A &) { cout << "Copy A\n"; }

    A(A &&) { cout << "Move A\n"; }

    A& operator=(const A&a)
    {
        std::cout << "copy assignment" << std::endl;
        return *this;
    }

    A& operator=(A &&a) {
        cout << "move assignment\n";
        return *this;
    }
};
A DoA() {
    A a1;
    A a2;
    a1.d = 5;
    if(rand()>10)
        return a2;
    return a1;
}
int main() {
    A a = DoA();
    return 0;
}
```

对于这样一个函数，在编译期间，编译期无法确定最终会返回a1还是a2对象，那么无论是将a1构造在a的地址上，还是将a2构造在a的地址上都是不合适的，因此会导致第三层优化失效。此时会构造a1、a2、a这三个对象。

再来看一段代码。
```cpp
#include <iostream>
using namespace std;
class A {
public:
    int d = 0;
    A() { cout << "Create A\n"; }

    ~A() { cout << "Destroy A\n"; }

    A(const A &) { cout << "Copy A\n"; }

    A(A &&) { cout << "Move A\n"; }

    A& operator=(const A&a)
    {
        std::cout << "copy assignment" << std::endl;
        return *this;
    }

    A& operator=(A &&a) {
        cout << "move assignment\n";
        return *this;
    }
};
A DoA() {
    A a1;
    A a2;
    a1.d = 5;
    if(1)
        return a2;
    return a1;
}
int main() {
    A a = DoA();
    return 0;
}
```
对于这样一段代码，我们知道对于if(1)这样的判断 编译器是会直接进行优化的, 显而易见最终直接返回的就是a2,可以把a2与a对象进行共享，这样就只需要构造两次A类对象(a1,a2)。
而实际上他却构造了三次，看看输出。
```
Create A
Create A
Move A
Destroy A
Destroy A
Destroy A
```
起初我以为是因为编译器的RVO在if优化之前，导致了编译器以为存在分支，使得第三层优化失效。
直到我把DoA()函数改成如下模样并运行。
```cpp
A DoA() {
    A a1;
    A a2;
    a1.d = 5;
    return a2;
    return a1;
}
output:
Create A
Create A
Move A
Destroy A
Destroy A
Destroy A
```
说明在没有if的情况下，依然会有三次构造，所以**初步**判断编译器只是简单的根据return的局部对象是否唯一来判断是否需要构造到外部变量上。
