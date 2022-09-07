import datetime
import os
import pathlib
import re
import socket
import sys
import time
import dmPython
from dm_config import ReadConfig
import shutil
import db_excel
import db_charts
import random
import string
from dm_info import print_info
import psycopg2


# 统计文件夹下的文件个数
def show_file_tree(file_path):
    # 获取当前目录下的文件列表
    file_list = os.listdir(file_path)
    file_count = 0
    folder_count = 0
    # 遍历文件列表，如果当前文件不是文件夹，则文件数量+1，如果是文件夹，则文件夹数量+1且再调用统计文件个数的方法
    for i in file_list:
        path_now = file_path + "\\" + i
        if os.path.isdir(path_now):
            folder_count = folder_count + 1
            show_file_tree(path_now)
        else:
            file_count = file_count + 1
    return file_count


# 验证时间字符串有效性
def verify_date_str_lawyer(datetime_str):
    try:
        datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
        return True
    except ValueError:
        return False


def fetch_mid_str(template, begin_str, end_str):
    mid_list = 0
    try:
        rule = r'%s(.*?)%s' % (begin_str, end_str)  # 正则规则
        mid_list = re.findall(rule, template)[0].strip()
    except Exception as e:
        mid_list = -1
        # print('检测到字符串', begin_str, end_str, '正则匹配失败', e)
    return mid_list


def start_pg():
    run_result = 1  # 当run_result变成0，说明pg启动完毕
    ini_file = ReadConfig()
    storage_db = 'pg' if ini_file.get_dm('storage_db') == -1 else ini_file.get_dm('storage_db')
    if storage_db.upper() == 'PG':
        if not check_port_in_use(15432):
            print('启动pg...')
            run_result = os.system('pgsql_10\\bin\\pg_ctl -D pgsql_10/data -l pgsql_10/data/logfile.log start')
    return run_result


def stop_pg():
    stop_result = 1  # 当run_result变成0，说明pg停止完毕
    ini_file = ReadConfig()
    storage_db = 'pg' if ini_file.get_dm('storage_db') == -1 else ini_file.get_dm('storage_db')
    if storage_db.upper() == 'PG':
        if check_port_in_use(15432):
            print('stopping pg...')
            stop_result = os.system('pgsql_10\\bin\\pg_ctl -D pgsql_10/data -l pgsql_10/data/logfile.log stop')
    return stop_result


class DbConn(object):
    def __init__(self):
        ini_file = ReadConfig()
        self.ip = ini_file.get_dm('ip')
        self.port = ini_file.get_dm('port')
        self.username = ini_file.get_dm('username')
        self.password = ini_file.get_dm('password')
        self.storage_db = 'pg' if ini_file.get_dm('storage_db') == -1 else ini_file.get_dm('storage_db')
        print('target database type:', self.storage_db)
        if self.storage_db.upper() == 'DM':
            if ini_file.get_dm('ip') == -1 or ini_file.get_dm('port') == -1 or \
                    ini_file.get_dm('username') == -1 or ini_file.get_dm('password') == -1:
                print('请取消config文件ip、端口、用户的注释,输入达梦数据库的信息！！！！！')
        try:
            if self.storage_db.upper() == 'DM':
                self.db_conn = dmPython.connect(user=self.username, password=self.password, server=self.ip,
                                                port=self.port,
                                                autoCommit=False)
            else:
                self.db_conn = psycopg2.connect(database='postgres', user='postgres', password='11111',
                                                host='localhost', sslmode='disable',
                                                port='15432')
            self.db_cursor = self.db_conn.cursor()
        except Exception as e:
            print(datetime.datetime.now(), "----------------", '连接数据库失败，请检查网络或者配置文件是否无误！', e)


class DmLog(object):
    def __init__(self):
        ini_file = ReadConfig()
        self.ip = ini_file.get_dm('ip')
        self.port = ini_file.get_dm('port')
        self.username = ini_file.get_dm('username')
        self.password = ini_file.get_dm('password')
        self.sqlpath = ini_file.get_dm('sqlpath')
        self.storage_db = 'pg' if ini_file.get_dm('storage_db') == -1 else ini_file.get_dm('storage_db')
        self.tab_name = 'dm_slow_log' if ini_file.get_dm('tab_name') == '' else ini_file.get_dm('tab_name')
        self.output_dir = ini_file.get_dm('output_dir')
        self.db_conn_obj = DbConn()

    def page_size(self):
        try:
            db_cursor = self.db_conn_obj.db_cursor
        except Exception as e:
            print("\033[0;31;42m请检查pgsql_10文件夹或者dm_config.ini文件是否存在\033[0m",e)
        cnt = ''
        if self.storage_db.upper() == 'DM':
            try:
                db_cursor.execute("""select page()""")
                cnt = db_cursor.fetchone()[0]
            except Exception as e:
                print(e)
        else:
            cnt = 32768
        return cnt

    def create_log_table(self):
        db_cursor = self.db_conn_obj.db_cursor
        tab_name = self.tab_name.upper()
        drop_table1 = "drop table if exists " + tab_name
        drop_table2 = "drop table if exists RWCOUNT"
        drop_table3 = "drop table if exists ERR_" + tab_name
        if self.storage_db.upper() == 'DM':
            sql3 = "CREATE TABLE if not exists RWCOUNT(SESS VARCHAR(500),STARTTIME TIMESTAMP(3),EXETIME INT,RCNT BIGINT) nologging"
            sql1 = "create table if not exists " + tab_name + "(starttime TIMESTAMP(3),sess varchar(500),sqlstr text,exetime float,sqlstr_sub varchar(8000),euer varchar(100),optype varchar(30),ROWCOUNT bigint,SQLSTR_PARA text,waittime varchar(10)) nologging"
            sql2 = "create table if not exists ERR_" + tab_name + "(starttime TIMESTAMP(3),sess varchar(500),euer varchar(100),sqlstr text)"
        else:
            sql3 = "CREATE UNLOGGED TABLE if not exists RWCOUNT(SESS VARCHAR(500),STARTTIME TIMESTAMP(3),EXETIME INT,RCNT BIGINT)"
            sql1 = "create UNLOGGED table if not exists " + tab_name + "(starttime TIMESTAMP(3),sess varchar(500),sqlstr text,exetime float,sqlstr_sub varchar(8000),euer varchar(100),optype varchar(30),ROWCOUNT bigint,SQLSTR_PARA text,waittime varchar(10))"
            sql2 = "create UNLOGGED table if not exists ERR_" + tab_name + "(starttime TIMESTAMP(3),sess varchar(500),euer varchar(100),sqlstr text)"
        try:
            db_cursor.execute(drop_table1)
            db_cursor.execute(drop_table2)
            db_cursor.execute(drop_table3)
            db_cursor.execute(sql1)
            db_cursor.execute(sql2)
            db_cursor.execute(sql3)
        except Exception as e:
            print(e)

    def update_log_table(self):
        tab_name = self.tab_name.upper()
        db_cursor = self.db_conn_obj.db_cursor
        if self.storage_db.upper() == 'DM':
            sql2 = "update " + tab_name + "  t1 set t1.rowcount=t2.rcnt from ( select * from ( " + " select  row_number() over(partition by a.sess order by  abs(datediff(ms,a.STARTTIME,dateadd(ms,-b.exetime,b.starttime)))) rn," + " a.sess,a.starttime,a.sqlstr_sub,b.RCNT" + " from " + tab_name + " a, (select    sess,max(starttime) starttime,max(exetime) exetime,max(rcnt) rcnt from RWCOUNT group by sess) b where a.sess=b.sess) where rn=1) t2 where t1.sess=t2.sess and t1.starttime=t2.starttime " + "     and t1.sqlstr_sub=t2.sqlstr_sub"
        else:
            sql2 = "update " + tab_name + " set rowcount=t2.rcnt from ( select * from (  select  row_number() over(partition by a.sess order by  abs(date_part('milliseconds',(b.starttime + ('-' || b.exetime || ' milliseconds')::interval)-a.starttime))) rn, a.sess,a.starttime,a.sqlstr_sub,b.RCNT from " + tab_name + " a, (select    sess,max(starttime) starttime,max(exetime) exetime,max(rcnt) rcnt from RWCOUNT group by sess) b where a.sess=b.sess) xx where rn=1) t2 where " + tab_name + ".sess=t2.sess and " + tab_name + ".starttime=t2.starttime    and " + tab_name + ".sqlstr_sub=t2.sqlstr_sub"
        try:
            db_cursor.execute(sql2)
            self.db_conn_obj.db_conn.commit()
        except Exception as e:
            print('update表失败', e)
            self.db_conn_obj.db_conn.rollback()

    def create_log_index(self):
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        tab_name = self.tab_name.upper()
        db_cursor = self.db_conn_obj.db_cursor
        if self.storage_db.upper() == 'DM':
            sql2 = "create or replace index idx_log_commit_" + ran_str + " on " + tab_name + "(exetime)"
        else:
            sql2 = "CREATE INDEX if not exists idx_log_commit_" + ran_str + " on " + tab_name + "(exetime)"
        try:
            db_cursor.execute(sql2)
        except Exception as e:
            print(e)
        self.db_conn_obj.db_conn.commit()

    def read_log_path(self, sql_log_path):
        ret = 0
        if sql_log_path != '':
            fileNum = show_file_tree(sql_log_path)
            if fileNum == 0:
                return 0
            # 获取慢日志目录下的所有文件名
            file_list = os.listdir(sql_log_path)
            for v_out in file_list:
                logfile_abs_name = sql_log_path + '\\' + v_out
                # 获取文件的后缀,用来判断是否是日志文件以及是否是目录，不是log为后缀名的一律忽略掉
                file_houzhui = pathlib.Path(v_out).suffix
                if file_houzhui == '.log':
                    print(datetime.datetime.now(), "----------------", "开始分析慢日志文件：" + v_out)
                    # 开始使用read_log_lines分析日志每一行
                    ret = self.read_log_lines(logfile_abs_name)
                else:
                    print("----------------忽略非SQL日志文件：" + v_out + "-------------")
        else:
            print(datetime.datetime.now(), "----------------", '获取慢日志文件路径异常，请检查配置文件！')
            return 0
        return ret

    def read_log_lines(self, filename):
        insert_result = 0
        line_num = 0
        list_all_data = []
        list_all_row_count = []
        insert_count = 0
        with open(filename, "r", encoding='utf-8', errors='ignore') as f:
            for line in f.readlines():
                # line是去掉列表中每一个元素的换行符之后的原始数据
                line = line.strip('\n')
                line_num += 1
                # 只解析包含EP字符串的内容,然后才写入到数据库,这里过滤掉dexp开头的查询
                if line.find('(EP[') > 0 and line.find('appname:dexp') < 0 and line.find('EXECTIME:') > 0:
                    sql_begin_time = line.split(" (EP[0]")[0]
                    if not verify_date_str_lawyer(sql_begin_time):
                        sql_begin_time = None
                    user = fetch_mid_str(line, 'user:', ' trxid:')
                    # 去除方括号的sql操作类型
                    optype2 = fetch_mid_str(line, "\) \[", "\] ")
                    # 判断字符串是否包含sql操作类型
                    optype2 = None if optype2 == -1 else optype2
                    # 加上转义符号的sql操作类型，如\[SEL\],用于正则匹配提取sql text
                    optype3 = '\\' + '[' + str(optype2) + '\\' + ']'
                    sql_text = fetch_mid_str(line, optype3, 'EXECTIME:')
                    exec_time = fetch_mid_str(line, 'EXECTIME:', '\(ms\)')
                    str_rowcount = fetch_mid_str(line, 'ROWCOUNT: ', '\(rows\)')
                    row_count = 0 if str_rowcount == -1 else str_rowcount
                    starttime = sql_begin_time
                    session = '(EP[0] ' + fetch_mid_str(line, '\(EP\[0\]', '\)') + ')'
                    sql_fulltext = sql_text
                    sql_exec_time = exec_time
                    sql_sub_text = sql_fulltext[0:4000]
                    exec_user = user
                    sql_op_type = optype2
                    sql_rowcount = row_count
                    sql_para = None
                    sql_wait = None
                    list_slow_log_content = [starttime, session, sql_fulltext, sql_exec_time, sql_sub_text, exec_user,
                                             sql_op_type, sql_rowcount, sql_para, sql_wait]
                    # 把一行一行数据存入到新的list，这个list用于批量插入到数据库
                    list_all_data.append(list_slow_log_content)
                    # dml影响行数存入到新的list，后面一次性插入到数据库
                    if line.find('ROWCOUNT:') > 0:
                        list_row_count = [session, sql_begin_time, exec_time, row_count]
                        list_all_row_count.append(list_row_count)
                if line_num % 10000 == 0:
                    print(datetime.datetime.now(), "----------------", '已处理行数：', line_num)
        if len(list_all_data) > 0:
            try:
                insert_count = self.insert(list_all_data)  # 一次性把list的数据批量插入到数据库
                self.db_conn_obj.db_conn.commit()
                insert_result = 1
            except Exception as e:
                print('插入数据异常', e)
                self.db_conn_obj.db_conn.rollback()
            print(datetime.datetime.now(), "----------------", '已处理行数：', line_num)
            print(datetime.datetime.now(), "----------------", '已插入行数：', insert_count)
        else:
            insert_result = 0
        if len(list_all_row_count) > 0:
            try:
                self.insert_rowcunt(list_all_row_count)
                self.db_conn_obj.db_conn.commit()
            except Exception as e:
                print('插入到rwcount异常', e)
                self.db_conn_obj.db_conn.rollback()
        return insert_result

    def insert(self, line_content):
        row_count = 0
        db_cursor = self.db_conn_obj.db_cursor
        if self.storage_db.upper() == 'DM':
            sql_str = "insert into " + self.tab_name + " values(?,?,?,?,?,?,?,?,?,?)"
            for dm_out in line_content:
                try:
                    db_cursor.execute(sql_str, dm_out)
                    row_count = row_count + db_cursor.rowcount
                except Exception as e:
                    print('插入数据库失败', e)
                    self.db_conn_obj.db_conn.rollback()
        else:
            sql_str = "insert into " + self.tab_name + " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            try:
                db_cursor.executemany(sql_str, line_content)
                row_count = db_cursor.rowcount
            except Exception as e:
                print('插入数据库失败', e)
                self.db_conn_obj.db_conn.rollback()
        return row_count

    def insert_rowcunt(self, line_str):
        db_cursor = self.db_conn_obj.db_cursor
        if self.storage_db.upper() == 'DM':
            sqlstr = "insert into RWCOUNT values(?,?,?,?)"
            for dm_out in line_str:
                try:
                    db_cursor.execute(sqlstr, dm_out)
                    self.db_conn_obj.db_conn.commit()
                except Exception as e:
                    print('插入数据库失败', e)
                    self.db_conn_obj.db_conn.rollback()
        else:
            sqlstr = "insert into RWCOUNT values(%s,%s,%s,%s)"
            try:
                db_cursor.executemany(sqlstr, line_str)
                self.db_conn_obj.db_conn.commit()
            except Exception as e:
                print('insert_rowcunt插入失败', e)
                self.db_conn_obj.db_conn.rollback()

    def query_max_exec_time(self):
        tab_name = self.tab_name
        # 分组汇总输出sql执行情况按最大执行耗时排序
        sql = """select row_number() over (order by max_tim desc) 序号,cast(s as varchar) SQL文本,max_tim 最大执行耗时_毫秒,min_tim 最小执行耗时_毫秒,CEILING(avg_90) 百分之90平均执行耗时_毫秒,CEILING(avg_tim) 平均执行耗时_毫秒,cnt 执行次数,max_rcount 行数,cast(SQLSTR_PARA as varchar) 替换参数后SQL,waittime 等待时间 from 
        (select s,max(tim)over(partition by sub) max_tim,min(tim)over(partition by sub) min_tim,avg(tim)over(partition by sub) avg_tim,
        avg(case when tile<=9 then tim else null end)over(partition by sub) avg_90,
        count(1)over(partition by sub) cnt,
        row_number()over(partition by sub order by tim desc) r ,
        max(ROWCOUNT)over(partition by sub) max_rcount,
        SQLSTR_PARA,waittime  from (select sqlstr s,sqlstr_sub sub,exetime tim,ntile(10) over(partition by sqlstr_sub order by exetime) tile,ROWCOUNT,SQLSTR_PARA,waittime from  %s  where  exetime >=  0 ) t1)  xx
         where r = 1""" % tab_name
        cur = self.db_conn_obj.db_cursor
        try:
            cur.execute(sql)  # 返回受影响的行数
        except Exception as e:
            print('查询按时间排序的慢sql失败', e)
        fields = [field[0] for field in cur.description]  # 获取所有字段名
        all_data = cur.fetchall()  # 所有数据
        excel_rows_num = len(all_data) + 1
        # print(excel_rows_num)
        return all_data, fields, excel_rows_num

    def query_max_exec_count(self):
        tab_name = self.tab_name
        # 分组汇总输出sql执行情况按最大执行次数排序
        sql = """select row_number() over (order by cnt desc) 序号,cast(s as varchar) SQL文本,max_tim 最大执行耗时_毫秒,min_tim 最小执行耗时_毫秒,
CEILING(avg_90) 百分之90平均执行耗时_毫秒,CEILING(avg_tim) 平均执行耗时_毫秒,cnt 执行次数,max_rcount 行数,cast(SQLSTR_PARA as varchar) 替换参数后SQL,waittime 等待时间 from 
(select s , max(tim)over(partition by sub) max_tim,min(tim)over(partition by sub) min_tim,avg(tim)over(partition by sub) avg_tim,avg(case when tile<=9 then tim else null end)over(partition by sub) avg_90,count(1)over(partition by sub) cnt,row_number()over(partition by sub order by tim desc) r ,max(ROWCOUNT)over(partition by sub) max_rcount,SQLSTR_PARA,waittime from (select sqlstr s,sqlstr_sub sub,exetime tim,ntile(10) over(partition by sqlstr_sub order by exetime) tile,
ROWCOUNT,SQLSTR_PARA,waittime from %s ) t1 ) xx where r = 1 and cnt>=0""" % tab_name
        cur = self.db_conn_obj.db_cursor
        try:
            cur.execute(sql)  # 返回受影响的行数
        except Exception as e:
            print('查询按次数排序的慢sql失败', e)
        fields = [field[0] for field in cur.description]  # 获取所有字段名
        all_data = cur.fetchall()  # 所有数据
        excel_rows_num = len(all_data) + 1
        # print(excel_rows_num)
        return all_data, fields, excel_rows_num

    def query_all_data(self):
        all_data = []
        tab_name = self.tab_name
        if self.storage_db.upper() == 'DM':
            sql = """select rownum,STARTTIME,exetime,euer,substr(replace(replace(cast(sqlstr as varchar),chr(10),''),chr(13),''),1,200),optype from %s""" % tab_name
        else:
            sql = """select row_number() over () as rownum,STARTTIME,exetime,euer,substr(replace(replace(cast(sqlstr as varchar),chr(10),''),chr(13),''),1,200),optype from %s""" % tab_name
        cur = self.db_conn_obj.db_cursor
        try:
            cur.execute(sql)
            all_data = cur.fetchall()
        except Exception as e:
            print('查询表', tab_name, '失败！', e)
        return all_data


def copyfile(old_file, new_file):
    try:
        if os.path.exists(old_file):
            shutil.copyfile(old_file, new_file)
    except Exception as e:
        print("复制单个文件操作出错", e)


class Logger(object):
    def __init__(self, filename='default.log', add_flag=True, stream=sys.stdout):
        self.terminal = stream
        self.filename = filename
        self.add_flag = add_flag
        # self.log = open(filename, 'a+')

    def write(self, message):
        if self.add_flag:
            with open(self.filename, 'a+') as log:
                self.terminal.write(message)
                log.write(message)
        else:
            with open(self.filename, 'w') as log:
                self.terminal.write(message)
                log.write(message)

    def flush(self):
        pass


def main():
    print_info()
    pg_run_result = start_pg()
    if pg_run_result == 0:
        print('pg启动完毕')
    time_start = time.time()
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    ss = time.localtime().tm_sec
    dmLog = DmLog()
    path = dmLog.sqlpath
    output_result_dir = dmLog.output_dir
    page_size = dmLog.page_size()
    if page_size != 32768:
        print(datetime.datetime.now(), "----------------", "当前dm库的page_size大小为:", str(page_size))
        print(datetime.datetime.now(), "----------------", "请用page_size为32k的dm库来分析")
    else:
        if len(output_result_dir) <= 0:
            output_result_dir = '.'
        destDirName = str(time.strftime("%Y_%m_%d"))
        destDirName = output_result_dir + "\\SLOW_LOG_" + destDirName + "_" + str(hour) + "_" + str(minute) + "_" + str(
            ss)
        excel_dest = destDirName + "\\dm_slow_sql.xlsx"
        sys.stdout = Logger(destDirName + "\\run_info.log", sys.stdout)
        if not os.path.exists(destDirName):
            os.makedirs(destDirName)
            print(datetime.datetime.now(), "----------------", "创建输出结果目录", destDirName, "成功！")
        else:
            print("输出结果目录" + destDirName + "已存在")
        # 以下开始在库里建表准备导入日志数据
        dmLog.create_log_table()
        ret = dmLog.read_log_path(path)
        dmLog.update_log_table()
        if ret != 0:
            # 创建索引
            dmLog.create_log_index()
            # 生成按执行时间维度统计结果
            sql_result_list = dmLog.query_max_exec_time()
            # 生成按执行次数分析的统计结果
            sql_result_list2 = dmLog.query_max_exec_count()
            # 生成SQL散点图之前获取数据
            sql_result_list3 = dmLog.query_all_data()
            if len(sql_result_list[0]) > 0 and len(sql_result_list2[0]) > 0:
                # 将以上2个结果写入到同一个excel不同的sheet
                print(datetime.datetime.now(), "----------------", '正在生成Excel')
                db_excel.read_db_to_xlsx(sql_result_list, sql_result_list2, destDirName + "\\dm_slow_sql.xlsx")
                # 生成SQL散点图
                print(datetime.datetime.now(), "----------------", '正在生成散点图')
                db_charts.scatter_plots(sql_result_list3, destDirName + "\\dm_slow_sql_charts.html")
                time_end = time.time()
                print(datetime.datetime.now(), "----------------", '程序解析耗时：', round(time_end - time_start, 2), '秒')
                print("解析慢日志完毕，请查看结果目录", os.path.dirname(os.path.realpath(excel_dest)))
            else:
                print('没有查询到慢日志数据，生成Excel以及散点图失败，请检查日志文件！')
        else:
            print('将慢日志数据插入到数据库失败！')
    stop_pg()


def check_port_in_use(port, host='127.0.0.1'):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, int(port)))
        return True
    except socket.error:
        return False
    finally:
        if s:
            s.close()


if __name__ == "__main__":
    main()
