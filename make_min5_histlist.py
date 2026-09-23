# -*- coding: utf-8 -*-
"""历史补拉采样清单: 82,176 全量 -> 分季度分层采样 ~4000
跳过已拉过的窗口(events5m 已有 12,023 文件)
输出: events_5min_hist.csv
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

NEW = r"E:\QuantLab\github_pull\events_5min_new.csv"
MIN = r"E:\QuantLab\data\minute\events5m"
OUT = r"E:\QuantLab\github_pull\events_5min_hist.csv"

have = set(f[:-4] for f in os.listdir(MIN))

df = pd.read_csv(NEW)
df["key"] = df["code"].str.replace(".", "_") + "__" + df["start_date"]
df = df[~df["key"].isin(have)]
print("未拉窗口:", len(df), flush=True)

# 分季度分层采样: 每季度最多 400 个, 均匀
rng = np.random.default_rng(20260923)
df["quarter"] = df["start_date"].str[:7]
out = []
for q, g in df.groupby("quarter"):
    n = min(len(g), 400)
    idx = rng.choice(len(g), n, replace=False)
    out.append(g.iloc[idx])
sampled = pd.concat(out)[["code", "start_date", "end_date"]]
sampled.to_csv(OUT, index=False)
print("采样:", len(sampled), "个窗口")
print(sampled.groupby(sampled["start_date"].str[:7]).size().to_string())
