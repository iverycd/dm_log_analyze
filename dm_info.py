from prettytable import PrettyTable

"""
V1.1.9.7.2 2022-09-07
1、修改打包方式
"""


def print_info():
    k = PrettyTable(field_names=["达梦慢日志分析工具"])
    k.align["达梦慢日志分析工具"] = "l"  # 以name字段左对齐
    k.padding_width = 1  # 填充宽度
    k.add_row(["Tool Version: 1.1.9.7.2"])
    k.add_row(["Release Date: 2022-09-07"])
    print(k.get_string(sortby="达梦慢日志分析工具", reversesort=False))


if __name__ == '__main__':
    print_info()
