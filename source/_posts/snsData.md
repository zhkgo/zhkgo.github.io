---
title: SpaceSniffer导出sns文件存储格式分析
date: 2024-04-30
tags: [逆向工程, spaceSniffer,内存可视化]
img: images/img202405052255892.png
---
> 在处理大型软件系统时，我们经常需要分析系统运行时的内存分布，了解哪些数据结构占用了大量内存。虽然可以通过数值进行观察，但这并不直观。这时，我想到了SpaceSniffer这款软件。SpaceSniffer主要用于磁盘空间的管理和可视化，它使用treemap进行可视化，即使面对大量文件也能保持流畅的体验。

## 思路简介
我们的主要思路是根据SpaceSniffer导出的sns文件格式来构造内存分布，将其视为文件分布进行观察。由于没有找到任何公开的文档说明如何构造这种格式，我们只能通过观察二进制文件来进行分析。基本的方法是不断改变文件夹内容，导出二进制数据并观察其特征。


## 分析过程
### 创建一个以empty为名的空文件夹

![空文件夹](images/img202405050004926.png)

### 创建file.txt

![](images/img202405050007248.png)

有了以下观察结果和推测。
* 两个二进制文件都以0x0203开头，0x0100结尾。
* 有一段二进制数据，解码出来是可见字符。
* 考虑到此时不变的内容只有文件夹名字，且增加的可见文字是以=号结尾，故猜测他们是base64编码后的文件/文件夹名。

尝试解码。
```python
import base64
# base64解码
print(base64.b64decode('TDpcdG9vbHNcYW5hU25zXGVtcHR5').decode('utf-8'))
# output L:\tools\anaSns\empty
```
发现输出的确实是扫描的文件夹所在的路径。再解码另一个字符串看看

```python
print(base64.b64decode('ZmlsZS50eHQ=').decode('utf-8'))
# output file.txt
```

看起来已经找到了文件名所在。

### 修改file.txt，向里面写入2个字母

![](images/img202405050008657.png)

对此有以下观察和推断。

* 二进制文件的长度没有变化，但在0x58行06列的值从0变为2，推测这可能是表示文件长度的字段。通过修改这个值并重新加载sns文件到SpaceSniffer，验证了这个推测。

* 在0x70行06列开始的位置，发现了一些变化。同样的字段出现了两次，推测这可能是文件的最后修改时间和访问时间。这个推测是通过反复观察SpaceSniffer界面并注意到写入两个字节的数据后，除了文件大小，变化的就只有这两个时间。

* 通过验证，确认这两个8字节的字段确实是文件的最后修改时间和访问时间。

* 在这两个字段之前的8字节没有变化，推测这是文件的创建时间。


3. empty目录下创建一个新的文件file2.txt，并写入100个字母。

![](images/img202405050008852.png)

对此有以下观察和推断。

* 每个文件名或文件夹名前面都有一段长度为4的二进制数据，这段数据的值与文件或文件夹名称的字节数非常接近。这可能是表示文件或文件夹名称长度的字段。

* 在这个字段之前，有一个统一的标记，是0x0203或0x0202，这可能是表示文件或文件夹开头的标记。

* 如果将0x0203或0x0202后面的4个字节看作是文件名称的字节长度，那么在文件名称后面紧跟着的一个数字就可能是表示文件或文件夹所占的空间大小。


### empty目录下创建一个名为hahaha的新目录

![](images/img202405050010782.png)

通过对比该数据和以上数据，发现。
 
* 0x0203表示文件夹开头，0x0202表示文件开头，0x0100表示文件夹或文件结尾。


### 在新目录下创建一个文件test.txt并写入10个字母

再次观察并对比

![](images/img202405050010994.png)

## 分析结果
最后通过若干次对比确认以前的信息。
得出sns文件的构成如下：

- 文件夹开头：`0x0203`
- 文件夹结尾：`0x0100`

文件或文件夹的结构如下：

- 头部（head）：`0x0203`（文件夹）或`0x0202`（文件），占用2字节
- 名称长度（lenOfName）：无符号32位整数（uint32），占用4字节
- 名称（Base64Filename）：Base64编码的文件名，长度可变
- 大小1（Size1）：无符号64位整数（uint64），占用8字节, 为节点内存大小
- 大小2（Size2）：无符号64位整数（uint64），占用8字节，推测为节点所占磁盘空间大小，对文件夹来说似乎无意义。
- 创建时间（CreationTime）：占用8字节
- 访问时间（AccessedTime）：占用8字节
- 修改时间（ModifiedTime）：占用8字节 时间的存储格式暂未分析
- 分隔符（sep）：`0x0000`，占用2字节
- 其他文件/目录（otherfile/directory）：可选
- 尾部（tail）：`0x1000`

对于文件夹，大小1和大小2都等于文件夹的大小。

对于文件，大小1等于文件的大小，大小2是补偿文件大小。大小1和大小2的和等于文件所占的真实磁盘空间。
其中对于文件夹 size1 = size2 = 文件夹大小
对于文件来说 size1= 文件大小 size2为补偿文件大小，size1+size2= 文件所占真实磁盘空间。

## 生成代码实现
接下来根据这个格式来尝试递归构建文件夹。
写出了如下类， 由于不知道时间，且时间暂时无意义，直接置为0。一开始使用python来写这个代码效率不尽如人意，后面改为使用c++。
```cpp
class Node {
public:
    string name;          // 节点名
    uint64_t size;        // 节点大小
    uint64_t paddingSize; // paddingSize = 实际占用空间-size，只针对文件有效，文件夹通常=size
    bool isFile;          // 是否是文件
    vector<Node*> childs; // 子节点
    Node* parent;         // 父节点

    Node(string name, uint64_t size = 0, uint64_t paddingSize = 0):name(name), size(size), isFile(true),parent(nullptr),paddingSize(paddingSize) {}
    ~Node() {
        for (Node* child : this->childs) {
            delete child;
        }
    }
    void addChild(Node* child) {
        if(child->parent != nullptr) {
            printf("warning! child has parent\n");
            for(int i = 0; i < child->parent->childs.size(); i++) {
                if(child->parent->childs[i] == child) {
                    child->parent->childs.erase(child->parent->childs.begin() + i);
                    break;
                }
            }
        }
        this->isFile = false;
        child->parent = this;
        this->childs.push_back(child);
        this->size += child->size;
        if (this->parent) {
            this->parent->updateSize(child->size);
        }
    }

    void updateSize(uint64_t size = 0) {
        this->size += size;
        if (this->parent) {
            this->parent->updateSize(size);
        }
    }

    void toSns(ofstream& f) {
        string encode_name = base64_encode(reinterpret_cast<const unsigned char*>(this->name.c_str()), this->name.length());
        uint32_t len = encode_name.length();
        // 头部
        f.put(0x02);
        f.put(this->isFile ? 0x02 : 0x03);

        //文件名长度
        f.write(reinterpret_cast<const char*>(&len), sizeof(len));

        // 文件名
        f.write(encode_name.c_str(), encode_name.length());

        // 文件/文件夹大小
        f.write(reinterpret_cast<const char*>(&this->size), sizeof(this->size));

        // 8 个字节表示被额外占用的磁盘空间，这边留空 暂时不知道啥用
        f.write(reinterpret_cast<const char*>(&this->paddingSize), sizeof(this->paddingSize));

        // 24 个字节表示文件的创建时间，访问时间，修改时间，这边留空
        for (int i = 0; i < 24; ++i) {
            f.put(0x00);
        }

        // 2个字节表示分隔符
        f.put(0x00);
        f.put(0x00);

        if (!this->isFile) {
            for (Node* child : this->childs) {
                child->toSns(f);
            }
        }
        // 结束符
        f.put(0x01);
        f.put(0x00);
    }
};
```

## 结果验证
 最后通过以下代码尝试构造sns格式文件,并使用spacesniffer加载。
```cpp
void nodeGen(){
    Node* root = new Node("root");
    root->addChild(new Node("a", 10));
    root->addChild(new Node("b", 20));
    Node* c = new Node("c");
    c->addChild(new Node("d", 300));
    c->addChild(new Node("e", 400));
    root->addChild(c);
    root->addChild(new Node("f", 50));
    root->addChild(new Node("g", 60));
    root->addChild(new Node("h", 70));
    root->addChild(new Node("i", 80));
    root->addChild(new Node("j", 90));
    ofstream f("test.sns", ios::binary);
    root->toSns(f);
    f.close();
}
```

![test.sns](images/img202405050015451.png)

