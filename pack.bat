rd /s /q  __pycache__ build
del /f /s /q *.spec

C:\miniconda3\envs\python_code\Scripts\pyinstaller --add-data "C:/miniconda3/envs/python_code/Lib/site-packages/plotly;./plotly" --clean --noconfirm DmLogAnalysis.py
rem C:\miniconda3\envs\python_code\Scripts\pyinstaller  --clean --noconfirm DmLogAnalysis.py
copy /y dm_config.ini dist\DmLogAnalysis
copy /y libeay32.dll dist\DmLogAnalysis
copy /y ssleay32.dll dist\DmLogAnalysis
ROBOCOPY dist\pgsql_10 dist\DmLogAnalysis\pgsql_10 /E

rem copy /y dm_config.ini dist\mysql_mig_kingbase_%version%
rem type nul > dist\mysql_mig_kingbase_%version%\custom_table.txt

rem cd dist\mysql_mig_kingbase_%version%
rem ren mysql_mig_kingbase_%version%.exe mysql_mig_kingbase.exe
rem cd ..

rem "C:\Program Files\WinRAR\Rar.exe" a -r -s -m1 C:\PycharmProjects\python_code\mysql_mig_kingbase\mysql_mig_kingbase_%version%_win.rar mysql_mig_kingbase_%version% ^

