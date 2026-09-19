# -*- coding: utf-8 -*-
"""GitHub Actions 上的 baostock 拉取 worker。
用法: python pull_bs.py <start_idx> <end_idx>
gentle 模式: 单登录 + 顺序查询 + 单查询全历史 + 失败重试2次(不并发, 不触发封禁)
输出: out/sh_600000.csv ...
"""
import os
import sys

import baostock as bs
import pandas as pd

start, end = int(sys.argv[1]), int(sys.argv[2])
codes = pd.read_csv("stock_list.csv")["code"].tolist()[start:end]
os.makedirs("out", exist_ok=True)

lg = bs.login()
assert lg.error_code == "0", "login failed: %s" % lg.error_msg

n_ok = 0
for i, c in enumerate(codes, 1):
    fn = os.path.join("out", c.replace(".", "_") + ".csv")
    if os.path.exists(fn):
        continue
    rows = []
    for attempt in range(2):
        rs = bs.query_history_k_data_plus(
            c, "date,code,open,high,low,close,volume,amount",
            start_date="1990-01-01", end_date="2026-09-19",
            frequency="d", adjustflag="2")
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if rows:
            break
    if rows:
        pd.DataFrame(rows, columns=rs.fields).to_csv(fn, index=False)
        n_ok += 1
    else:
        print("EMPTY %s %s %s" % (c, rs.error_code, rs.error_msg[:60]), flush=True)
    if i % 50 == 0:
        print("progress %d/%d ok=%d" % (i, end - start, n_ok), flush=True)

bs.logout()
print("DONE ok=%d/%d" % (n_ok, end - start), flush=True)
