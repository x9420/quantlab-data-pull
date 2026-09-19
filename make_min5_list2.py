# -*- coding: utf-8 -*-
"""扩样: 10,000 个事件窗口 (排除已拉的 2000)
输出: github_pull/events_5min_2.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"E:\QuantLab\data\prices\amount"
rng = np.random.default_rng(20260920)
rows = []
for f in sorted(os.listdir(DATA)):
    if not f.endswith(".csv"):
        continue
    df = pd.read_csv(os.path.join(DATA, f), usecols=["date", "close"])
    df = df[(df.date >= "2021-01-01") & (df.date < "2025-01-01")].reset_index(drop=True)
    if len(df) < 60:
        continue
    c = df["close"].astype(float).values
    r10 = pd.Series(c).pct_change(10).values
    for p in np.where(~np.isnan(r10) & (r10 <= -0.15))[0]:
        if p < 12 or p + 22 >= len(df):
            continue
        code = f[:-4].replace("_", ".")
        rows.append((code, str(df["date"].iloc[p - 10]), str(df["date"].iloc[p + 20])))

print("总事件(2021-2024):", len(rows))
if len(rows) > 10000:
    idx = rng.choice(len(rows), 10000, replace=False)
    rows = [rows[i] for i in idx]
pd.DataFrame(rows, columns=["code", "start_date", "end_date"]).to_csv(
    r"E:\QuantLab\github_pull\events_5min_2.csv", index=False)
print("采样写入:", len(rows))
