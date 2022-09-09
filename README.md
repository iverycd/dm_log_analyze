# dm_log_analyze
![commit](https://img.shields.io/github/last-commit/iverycd/dm_log_analyze?style=flat-square)
![tag](https://img.shields.io/github/v/tag/iverycd/dm_log_analyze)
![languages](https://img.shields.io/github/languages/top/iverycd/dm_log_analyze)

## 简介
此工具可用于分析达梦生成的慢日志（SVR_LOG）log文件，生成按时间以及执行次数执行情况的Excel表格，同时可以生成SQL执行情况散点图

备注：文末附开启达梦慢日志方法

## 运行概览

测试环境：
联想THINKPAD E490 Intel i5 8265U + 32G DDR4 + 三星850 EVO SSD 
单个日志文件在512MB
解析日志耗时：8s
![image](https://user-images.githubusercontent.com/35289289/189052736-d3f936a3-feed-4608-8423-fd95851ac5cd.png)

![image](https://user-images.githubusercontent.com/35289289/189052797-cb2585fe-e768-4ae3-8f56-90edaceeffaa.png)

![image](https://user-images.githubusercontent.com/35289289/189052820-dca4f625-9942-4fbc-82ad-963d4e8eb384.png)



## 如何运行
以下是在`Python 3.7.9`环境

* 安装dmPython
`解压dmPython.zip`
```python
源码直接安装（不分平台）
	python setup.py install
	
	
(python_code) D:\dmdbms\drivers\python\dmPython_C\dmPython>python setup.py install

输出过程：
running install
running bdist_egg
running egg_info
writing dmPython.egg-info\PKG-INFO
writing dependency_links to dmPython.egg-info\dependency_links.txt
writing top-level names to dmPython.egg-info\top_level.txt
reading manifest file 'dmPython.egg-info\SOURCES.txt'
writing manifest file 'dmPython.egg-info\SOURCES.txt'
installing library code to build\bdist.win-amd64\egg
running install_lib
running build_ext
creating build\bdist.win-amd64\egg
copying build\lib.win-amd64-3.7\dmPython.cp37-win_amd64.pyd -> build\bdist.win-amd64\egg
creating stub loader for dmPython.cp37-win_amd64.pyd
byte-compiling build\bdist.win-amd64\egg\dmPython.py to dmPython.cpython-37.pyc
creating build\bdist.win-amd64\egg\EGG-INFO
copying dmPython.egg-info\PKG-INFO -> build\bdist.win-amd64\egg\EGG-INFO
copying dmPython.egg-info\SOURCES.txt -> build\bdist.win-amd64\egg\EGG-INFO
copying dmPython.egg-info\dependency_links.txt -> build\bdist.win-amd64\egg\EGG-INFO
copying dmPython.egg-info\top_level.txt -> build\bdist.win-amd64\egg\EGG-INFO
writing build\bdist.win-amd64\egg\EGG-INFO\native_libs.txt
zip_safe flag not set; analyzing archive contents...
__pycache__.dmPython.cpython-37: module references __file__
creating 'dist\dmPython-2.3-py3.7-win-amd64.egg' and adding 'build\bdist.win-amd64\egg' to it
removing 'build\bdist.win-amd64\egg' (and everything under it)
Processing dmPython-2.3-py3.7-win-amd64.egg
creating c:\miniconda3\envs\python_code\lib\site-packages\dmPython-2.3-py3.7-win-amd64.egg
Extracting dmPython-2.3-py3.7-win-amd64.egg to c:\miniconda3\envs\python_code\lib\site-packages
Adding dmPython 2.3 to easy-install.pth file

Installed c:\miniconda3\envs\python_code\lib\site-packages\dmpython-2.3-py3.7-win-amd64.egg
Processing dependencies for dmPython==2.3
Finished processing dependencies for dmPython==2.3
```
以上完成了dmpython的安装，可以直接import了

* 其他依赖
```python
psycopg2 --> postgresql接口
openpyxl --> 输出Excel
plotly   --> 输出图表
```

* 编辑dm_config.ini文件
```bash
[dm]
# 慢sql日志路径--->log文件所在目录
sqlpath=C:\log\
# 存入数据库的慢日志表名--->可保持默认
tab_name=dm_slow_log
# 解析慢日志输出的目录--->生成Excel以及图表的输出目录
output_dir=C:\temp\
# 存储慢日志的数据库类型--->可保持默认
storage_db=pg
```

* 将pgsql_10.zip解压放在程序文件所在同一目录
![image](https://user-images.githubusercontent.com/35289289/189052875-8b78062c-f86f-4c85-9a03-3f48e1eecc45.png)

* 运行

```python
python DmLogAnalysis.py
```

## 打包
1、将pgsql_10.zip解压放在程序文件所在同一目录
![image](https://user-images.githubusercontent.com/35289289/189052875-8b78062c-f86f-4c85-9a03-3f48e1eecc45.png)


2、在PyInstaller目录下，比如
`C:\miniconda3\envs\python_code\Lib\site-packages\PyInstaller\hooks`目录下新建文件，内容如下：
文件名`hook-plotly.py`

![image](https://user-images.githubusercontent.com/35289289/189053056-0ba0131e-4a13-4355-a583-4683151e2930.png)



```python
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = collect_data_files('plotly') + copy_metadata('plotly')
```

3、在程序所在目录使用pyinstaller打包
```Python
C:\miniconda3\envs\python_code\Scripts\pyinstaller --add-data "C:/miniconda3/envs/python_code/Lib/site-packages/plotly;./plotly" --clean --noconfirm DmLogAnalysis.py
```

4、拷贝ini文件、动态库DLL文件以及pgsql到打包目录
```python
copy /y dm_config.ini dist\DmLogAnalysis
copy /y libeay32.dll dist\DmLogAnalysis
copy /y ssleay32.dll dist\DmLogAnalysis
ROBOCOPY dist\pgsql_10 dist\DmLogAnalysis\pgsql_10 /E
```

5、在DmLogAnalysis.exe文件所在目录编辑dm_config.ini文件
```bash
[dm]
# 慢sql日志路径--->log文件所在目录
sqlpath=C:\log\
# 存入数据库的慢日志表名--->可保持默认
tab_name=dm_slow_log
# 解析慢日志输出的目录--->生成Excel以及图表的输出目录
output_dir=C:\temp\
# 存储慢日志的数据库类型--->可保持默认
storage_db=pg
```
5、可直接运行exe文件
```python
C:\DmLogAnalysis>DmLogAnalysis.exe
```


## 附录：达梦开启慢日志

1、在达梦服务器上获取sqllog.ini文件路径

```bash
export log_path=`ps -ef|grep dm.ini|grep -v grep|awk '{print $9}'| sed "s/dm\.ini//g"| sed "s/path=//g"` && echo $log_path'sqllog.ini'
```


2、编辑SQL日志文件sqllog.ini

```sql

BUF_TOTAL_SIZE          = 10240         #SQLs Log Buffer Total Size(K)(1024~1024000)
BUF_SIZE                = 1024          #SQLs Log Buffer Size(K)(50~409600)
BUF_KEEP_CNT            = 6             #SQLs Log buffer keeped count(1~100)

[SLOG_ALL]
    FILE_PATH    = ../log
    PART_STOR = 0
    SWITCH_MODE = 2 #按文件大小切换
    SWITCH_LIMIT = 512 #设置单个日志最大512M，根据实际环境设置
    ASYNC_FLUSH = 1 #异步SQL日志功能，注意不要开同步
    FILE_NUM = 4 #总共记录4个日志文件，根据实际环境设置
    ITEMS = 0
    SQL_TRACE_MASK = 2:3:28:25 #LOG记录的语句类型掩码
    MIN_EXEC_TIME = 1500 #最小执行时间毫秒，根据实际环境设置
    USER_MODE = 0
    USERS =

```


3、在当前运行的数据库进行开启以及关闭svr慢日志
```
-- 每次修改sqllog.ini的配置文件后，用如下命令进行热加载

CALL SP_REFRESH_SVR_LOG_CONFIG(); 

--开启sql日志

SP_SET_PARA_VALUE(1,'SVR_LOG',1); 


--关闭SQL日志

SP_SET_PARA_VALUE(1,'SVR_LOG',0);
```
