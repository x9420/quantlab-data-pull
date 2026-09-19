# -*- coding: utf-8 -*-
"""GitHub runner: 按事件窗口拉 baostock 5min
用法: python pull_min5.py <start_idx> <end_idx>
读 events_5min.csv 的 [start_idx, end_idx) 行, 每行 = (code, start_date, end_date)
输出: out/{code}__{start}.csv (同股票不同窗口分文件)
"""
import os
import sys

import baostock as bs
import pandas as pd

start, end = int(sys.argv[1]), int(sys.argv[2])
pairs = pd.read_csv("events_5min.csv").iloc[start:end]
os.makedirs("out", exist_ok=True)

lg = bs.login()
if lg.error_code != "0":
    print("LOGIN_FAIL", lg.error_msg, flush=True)
    sys.exit(1)

n_ok = 0
for i, (_, row) in enumerate(pairs.iterrows(), 1):
    code, s, e = row["code"], str(row["start_date"]), str(row["end_date"])
    fn = os.path.join("out", "%s__%s.csv" % (code.replace(".", "_"), s))
    if os.path.exists(fn):
        continue
    try:
        rs = bs.query_history_k_data_plus(code, "date,time,open,high,low,close,volume,amount",
                                          start_date=s, end_date=e, frequency="5", adjustflag="2")
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if rows:
            pd.DataFrame(rows, columns=rs.fields).to_csv(fn, index=False)
            n_ok += 1
        else:
            print("EMPTY %s %s %s" % (code, s, rs.error_code), flush=True)
    except Exception as ex:
        print("ERR %s %s %s" % (code, s, str(ex)[:60]), flush=True)
        try:
            bs.login()
        except Exception:
            pass
    if i % 25 == 0:
        print("progress %d/%d ok=%d" % (i, end - start, n_ok), flush=True)

bs.logout()
print("DONE ok=%d/%d" % (n_ok, end - start), flush=True)
