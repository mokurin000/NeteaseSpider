import pandas as pd
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts

# 读取Excel文件
df = pd.read_excel("track_info.xlsx")

# 去除引号
df["track_name"] = df["track_name"].apply(lambda n: n[1:-1])
df["artist"] = df["artist"].apply(lambda n: n[1:-1])


# 统计每首音乐出现的频次
track_counts = df["track_name"].value_counts().head(10)

# 提取音乐名称和对应的频次
track_names = track_counts.index.tolist()
track_frequencies = track_counts.values.tolist()

artist_counts = df["artist"].value_counts().head(10)

# 创建条形图
bar = (
    Bar()
    .add_xaxis(track_names)
    .add_yaxis("频次", track_frequencies)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="最高频出现的十首音乐"),
        xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}),
        yaxis_opts=opts.AxisOpts(name="频次"),
    )
)

pie = (
    Pie()
    .add("", list(artist_counts.to_dict().items()))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="最高频出现的十首音乐"),
        xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}),
        yaxis_opts=opts.AxisOpts(name="频次"),
    )
)

# 渲染图表为HTML文件
bar.render("top_10_tracks.html")
pie.render("top_10_tracks_pie.html")
