# PanuOJ 版本号:2.0-240730-dev

### 说明

PanuOJ是一个在线评测网站，可以用于搭建自己的OJ网站。当然，PanuOJ以希望蓝(#0080FF)和希望橙(#FF8000)作为主色，以Apache License 2.0发行。

### 使用方法

1. 在根文件夹创建"题号"文件夹，在其中放入"1.in","1.out","2.in","2.out"...其中题号为四位补0整数，从0开始
2. 在problems文件夹中加入"题号.md"和"题号.title"，分别用来放题目说明与题目名称，题号意义同上
3. 使用docker pull一个ubuntu image，安装python3,python3-psutil,g++之后commit成psutil_gpp，作为评测层。
4. 在终端中用python3运行main.py

### 运行环境

Linux kernel >= 5.3

python3(both linux package and docker image) >= 3.8

Flask(python package) >= 2.0

docker(python package) >= 5.0

docker.io(linux package) >= 20.0

g++(docker image)最好保持CCF官网版本

##### 此软件由PanuGame开发团队制作，您的支持是我们的动力~
##### 在此鸣谢imken对UI的杰出贡献
