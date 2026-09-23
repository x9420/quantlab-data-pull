# -*- coding: utf-8 -*-
"""生成 OOS 段(2025+)恐慌日深跌型分钟线清单(不筛获利盘, 事后可筛)
+ 追加历史段 26 个已有关键窗口
输出: events_5min_key.csv (合并版)
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

DATA = r"E:\QuantLab\data\prices\amount"
HIST = r"E:\QuantLab\data\dashboard\signals_history"
PD = r"E:\QuantLab\data\dashboard\panic_days.json"
MIN = r"E:\QuantLab\data\minute\events5m"
OUT = r"E:\QuantLab\github_pull\events_5min_key.csv"

pd_info = json.load(open(PD, encoding="utf-8"))
days = sorted([d for d in pd_info["days"] if d["oos"]], key=lambda d: d["date"])  # OOS段

have = set(f[:-4] for f in os.listdir(MIN))

rows = []
have_cnt = 0
for d in days:
    f = os.path.join(HIST, d["date"] + ".json")
    if not os.path.exists(f):
        continue
    for s in json.load(open(f, encoding="utf-8"))["signals"]:
        if s["f20"] is None or s["close"] < 5:
            continue
        if s["dist60"] is None or s["dist60"] > -0.40:
            continue
        if s["code"] + "__" + d["date"] in have:
            have_cnt += 1
            continue
        df = pd.read_csv(os.path.join(DATA, s["code"] + ".csv"), usecols=["date"])
        df["date"] = df["date"].astype(str)
        pos = df.index[df["date"] == d["date"]].tolist()
        if not pos:
            continue
        p = pos[0]
        s_idx = max(p - 10, 0)
        e_idx = min(p + 20, len(df) - 1)
        rows.append((s["code"].replace("_", "."), str(df["date"].iloc[s_idx]), str(df["date"].iloc[e_idx])))

out = pd.DataFrame(rows, columns=["code", "start_date", "end_date"]).drop_duplicates()

# 合并历史段关键 26 个(若已生成)
old = r"E:\QuantLab\github_pull\events_5min_key.csv"
if os.path.exists(old):
    try:
        o = pd.read_csv(old)
        out = pd.concat([out, o]).drop_duplicates()
    except Exception:
        pass

out.to_csv(OUT, index=False)
print("OOS段深跌型窗口:", len(out), "个 (已有分钟文件跳过", have_cnt, "个)")
print(out.groupby(out["start_date"].str[:7]).size().to_string())
