# -*- coding: utf-8 -*-
"""生成分钟线增量事件清单: 2024-11-16 ~ 最新交易日 的超跌事件窗口
口径与原清单一致: 10日跌>15%, 窗口=事件前10交易日~事件后20交易日(不超过最新交易日)
输出: github_pull/events_5min_new.csv
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

DATA = r"E:\QuantLab\data\prices\amount"
OUT = r"E:\QuantLab\github_pull\events_5min_new.csv"

files = sorted(f for f in os.listdir(DATA) if f.endswith(".csv"))
rows = []
for f in files:
    df = pd.read_csv(os.path.join(DATA, f), usecols=["date", "close"])
    df = df[(df.date >= "2024-11-16") & (df.date <= "2026-09-18")]
    if len(df) < 40:
        continue
    df = df.reset_index(drop=True)
    c = df["close"].astype(float).values
    ret10 = pd.Series(c).pct_change(10).values
    ev = np.where(~np.isnan(ret10) & (ret10 <= -0.15))[0]
    for p in ev:
        if p < 12:
            continue
        # 窗口: 前10日(留2日余量) ~ 后20日(不超过数据末尾)
        s = str(df["date"].iloc[max(p - 12, 0)])
        e = str(df["date"].iloc[min(p + 20, len(df) - 1)])
        code = f[:-4].replace("_", ".")
        rows.append((code, s, e))

out = pd.DataFrame(rows, columns=["code", "start_date", "end_date"])
out.to_csv(OUT, index=False)
print("增量事件窗口:", len(out), "个")
print("日期范围:", out["start_date"].min(), "->", out["end_date"].max())
# 按季分布
out["q"] = out["start_date"].str[:7]
print(out.groupby("q").size().to_string())
