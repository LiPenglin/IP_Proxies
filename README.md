# IP_Proxies

## 实现思路

i.	Getter：获取代理ip
ii.	Adder：将获取的ip放到tester中测试，ok则add
iii.	Tester：
    1.	保证代理池不爆，不空
    2.	按时测试代理池中ip是否能使用，不能用则删掉
iv.	Schedule：
    1.	通过redis 中ip数量调度adder
    2.	检测redis中ip，及时删除过期ip
v.	Api：flask 接口，对外提供可用ip + port


## 项目架构以及笔记

[python - IP Proxies](http://blog.csdn.net/peerslee/article/details/71173320)

## 版本

1. python 3.6
2. redis 3.2.1
3. flask 0.12.2
4. requests 2.14.2
5. pyquery 1.2.17
6. redis（python）2.10.6
7. aiohttp 2.3.1 
