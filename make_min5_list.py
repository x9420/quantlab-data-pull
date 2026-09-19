# -*- coding: utf-8 -*-
"""生成事件窗口分钟线清单: 2021-2024 超跌事件采样 2000 个
窗口: 事件前 10 交易日 ~ 事件后 20 交易日 (下跌形态研究够用)
输出: github_pull/events_5min.csv (code,start_date,end_date)
"""
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"E:\QuantLab\data\prices\amount"
rng = np.random.default_rng(20260919)
rows = []
files = sorted(os.listdir(DATA))
for f in files:
    if not f.endswith(".csv"):
        continue
    df = pd.read_csv(os.path.join(DATA, f), usecols=["date", "close"])
    df = df[(df.date >= "2021-01-01") & (df.date < "2025-01-01")]
    if len(df) < 60:
        continue
    df = df.reset_index(drop=True)
    c = df["close"].astype(float).values
    ret10 = pd.Series(c).pct_change(10).values
    ev = np.where(~np.isnan(ret10) & (ret10 <= -0.15))[0]
    for p in ev:
        if p < 12 or p + 22 >= len(df):
            continue
        code = f[:-4].replace("_", ".")
        rows.append((code, str(df["date"].iloc[p - 10]), str(df["date"].iloc[p + 20])))

print("总事件(2021-2024):", len(rows))
if len(rows) > 2000:
    idx = rng.choice(len(rows), 2000, replace=False)
    rows = [rows[i] for i in idx]
out = pd.DataFrame(rows, columns=["code", "start_date", "end_date"])
out.to_csv(r"E:\QuantLab\github_pull\events_5min.csv", index=False)
print("采样写入:", len(out), "个事件窗口")
