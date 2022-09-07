import plotly.offline as pyo
import pandas as pd
import plotly.express as px


def scatter_plots(sql_result_list, file_name):
    df = pd.DataFrame([[ij for ij in i] for i in sql_result_list])
    # print(df[0], df[1], df[2], df[3], df[4], df[5])
    df.rename(columns={0: 'ROWNUM', 1: 'STARTTIME', 2: 'EXETIME', 3: 'EUER', 4: 'SQL_TEXT', 5: 'OPTYPE'},
              inplace=True)
    df = df.sort_values(['EXETIME'], ascending=[1])
    # x是横线坐标数据来源，y是纵向坐标数据来源，匹配上面df重命名的列，color是用于对不同操作类型进行分类点击，log_y可以记录详细的信息
    # hover_data是悬停到浮点展示的各类信息
    fig = px.scatter(df, x="STARTTIME", y="EXETIME", color="OPTYPE", log_y=True,
                     hover_data={'STARTTIME': '|%H:%M:%S.%L',
                                 'EUER': True,
                                 'SQL_TEXT': True,
                                 })
    fig.update_traces(marker_size=5)  # 散点大小
    fig.update_layout(
        title={'text': "达梦SQL执行情况分布"},
        title_font_color="red",  # 散点图文字，标题等格式设置
        xaxis=dict(title='时间范围'),  # x轴坐标名称
        yaxis=dict(title_text="SQL执行耗时<b>(毫秒)</b>", titlefont=dict(color="#ff7f0e"), ),  # y轴坐标名称
        hovermode='x unified',  # 显示x轴纵向的虚线，只要横线滑动就有虚线定位
    )
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=30,  # 时间范围选择框的长度，拖动这个范围框，比如点30m就是30分钟的范围框
                         label="30m",
                         step="minute",
                         stepmode="backward"),
                    dict(count=1,
                         label="1h",
                         step="hour",
                         stepmode="backward"),
                    dict(count=2,
                         label="2h",
                         step="hour",
                         stepmode="backward"),
                    dict(count=1,
                         label="1d",
                         step="day",
                         stepmode="backward"),
                    dict(step="all")
                ]),
                x=1,  # 时间范围选择按钮的位置，实际是水平右上角，二维坐标系x=1的位置
                y=1,  # 时间范围选择按钮的位置，实际是水平右上角二维坐标系y=1的位置
                borderwidth=2,  # 时间范围按钮边框的宽度
                activecolor='red'  # 时间范围按钮激活选中的颜色
            ),
            rangeslider=dict(
                visible=True,  # 时间范围选择框是否展示
                thickness=0.05  # 时间范围选择框高度
            ),
            type="date"  # 范围选择框的类型
        )
    )
    # 设定y轴标尺在坐标系内部，y轴值加上后缀为毫秒，显示网格线以及颜色，显示值为0的线，y轴的值取整，比如100.0，取整为100
    fig.update_yaxes(ticklabelposition="inside top", ticksuffix="毫秒", showgrid=True, gridcolor='LightPink'
                     , zeroline=True, zerolinewidth=2, zerolinecolor='LightPink', tickformat=".1d")
    fig.update_xaxes(tickformat="%m-%d %H:%M:%S", )  # 设定x轴时间日期格式化，nticks=20是设定坐标轴图例显示数量
    pyo.plot(fig, filename=file_name)

