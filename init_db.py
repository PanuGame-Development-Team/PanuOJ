from main import *
from random import randint
with app.app_context():
    db.create_all()
    problemhw = Problem()
    problemhw.markdown = """# A+B Problem
## 题目描述

输入两个整数 $a, b$，输出它们的和（$|a|,|b| \le {10}^9$）。

注意

1. 有负数哦！
2. C/C++ 的 main 函数必须是 `int` 类型，而且 C 最后要 `return 0`。这不仅对洛谷其他题目有效，而且也是 NOIP/CSP/NOI 比赛的要求！

好吧，同志们，我们就从这一题开始，向着大牛的路进发。

> 任何一个伟大的思想，都有一个微不足道的开始。

## 输入格式

两个以空格分开的整数。

## 输出格式

一个整数。

## 样例 #1

### 样例输入 #1

```
20 30
```

### 样例输出 #1

```
50
```

**本题程序范例：**

C
```c
#include <stdio.h>

int main()
{
    int a,b;
    scanf("%d%d",&a,&b);
    printf("%d\\n", a+b);
    return 0;
}
```
----------------

C++
```cpp
#include <iostream>
#include <cstdio>

using namespace std;

int main()
{
    int a,b;
    cin >> a >> b;
    cout << a+b << endl;
    return 0;
}
```"""
    ls = []
    for i in range(10):
        a = randint(-1e9,1e9)
        b = randint(-1e9,1e9)
        c = a + b
        ls.append([f"{a} {b}",f"{c}"])
    problemhw.points = str(ls)
    problemhw.title = "A+B Problem"
    db.session.add(problemhw)
    admin = User()
    admin.username = "admin"
    admin.password = generate_password_hash("admin")
    admin.admin = True
    admin.disabled = False
    admin.verified = True
    db.session.add(admin)
    db.session.commit()