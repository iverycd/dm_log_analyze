import configparser
import os

exepath = os.getcwd()
exepath = os.path.join(exepath, "dm_config.ini")

config = configparser.ConfigParser()
config.read(exepath, encoding='utf-8-sig')


class ReadConfig:
    @staticmethod
    def get_dm(name):
        value = 0
        try:
            value = config.get('dm', name)  # 通过config.get拿到配置文件中DATABASE的name的对应值
        except Exception as e:
            value = -1
        return value


if __name__ == '__main__':
    print('config_path', exepath)  # 打印输出config_path测试内容是否正确
    print('通过config.get拿到配置文件中DATABASE的对应值\n',
          'ip', ReadConfig().get_dm('ip'),
          'port', ReadConfig().get_dm('port'),
          'username', ReadConfig().get_dm('username'),
          'password', ReadConfig().get_dm('password'),
          'sqlpath', ReadConfig().get_dm('sqlpath'),
          'tab_name', ReadConfig().get_dm('tab_name'),
          )
