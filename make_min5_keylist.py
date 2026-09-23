# -*- coding: utf-8 -*-
"""生成策略关键分钟线清单: 恐慌日深跌型+获利盘<5%信号(2024-11后)
+ 2025-2026 OOS段全部恐慌日深跌型信号
跳过已存在的分钟文件; 输出 events_5min_key.csv
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

DATA = r"E:\QuantLab\data\prices\amount"
HIST = r"E:\QuantLab\data\dashboard\signals_history"
PD = r"E:\QuantLab\data\dashboard\panic_days.json"
CHIP = r"E:\QuantLab\data\dashboard\chip_profit_ratio.csv"
MIN = r"E:\QuantLab\data\minute\events5m"
OUT = r"E:\QuantLab\github_pull\events_5min_key.csv"

chip = pd.read_csv(CHIP)
chip["key"] = chip["code"] + "|" + chip["date"]
chip_map = dict(zip(chip["key"], chip["profit_ratio"]))

pd_info = json.load(open(PD, encoding="utf-8"))
days = sorted([d for d in pd_info["days"]], key=lambda d: d["date"])

# 已有分钟文件集合
have = set()
for f in os.listdir(MIN):
    have.add(f[:-4])  # code__date

rows = []
have_cnt = 0
for d in days:
    if d["date"] < "2024-11-16":
        continue
    f = os.path.join(HIST, d["date"] + ".json")
    if not os.path.exists(f):
        continue
    for s in json.load(open(f, encoding="utf-8"))["signals"]:
        if s["f20"] is None or s["close"] < 5:
            continue
        if s["dist60"] is None or s["dist60"] > -0.40:
            continue
        pr = chip_map.get(s["code"] + "|" + d["date"])
        if pr is None or pr >= 0.05:
            continue
        if s["code"] + "__" + d["date"] in have:
            have_cnt += 1
            continue
        # 窗口: 事件前10交易日~后20交易日(从日线算)
        df = pd.read_csv(os.path.join(DATA, s["code"] + ".csv"), usecols=["date"])
        df["date"] = df["date"].astype(str)
        pos = df.index[df["date"] == d["date"]].tolist()
        if not pos:
            continue
        p = pos[0]
        s_idx = max(p - 10, 0)
        e_idx = min(p + 20, len(df) - 1)
        rows.append((s["code"].replace("_", "."), str(df["date"].iloc[s_idx]), str(df["date"].iloc[e_idx])))

out = pd.DataFrame(rows, columns=["code", "start_date", "end_date"])
out = out.drop_duplicates()
out.to_csv(OUT, index=False)
print("策略关键窗口:", len(out), "个 (已有分钟文件的跳过", have_cnt, "个)")
print(out.groupby(out["start_date"].str[:7]).size().to_string())
