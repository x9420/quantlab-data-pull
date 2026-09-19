# -*- coding: utf-8 -*-
"""GitHub Actions 上的东财个股资金流拉取 worker。
用法: python pull_ff.py <start_idx> <end_idx>
akshare stock_individual_fund_flow: 每只一次调用返回长期历史(约3年+)
输出: out/sh_600000.csv ...
"""
import os
import sys

import akshare as ak
import pandas as pd

start, end = int(sys.argv[1]), int(sys.argv[2])
df = pd.read_csv("stock_list.csv")
codes = df["code"].tolist()[start:end]
os.makedirs("out", exist_ok=True)

n_ok = 0
for i, c in enumerate(codes, 1):
    fn = os.path.join("out", c.replace(".", "_") + ".csv")
    if os.path.exists(fn):
        continue
    try:
        # c 形如 sh.600519
        mkt = c.split(".")[0]
        sym = c.split(".")[1]
        d = ak.stock_individual_fund_flow(stock=sym, market=mkt)
        if d is not None and len(d):
            d.to_csv(fn, index=False)
            n_ok += 1
        else:
            print("EMPTY %s" % c, flush=True)
    except Exception as e:
        print("ERR %s %s" % (c, str(e)[:80]), flush=True)
    if i % 50 == 0:
        print("progress %d/%d ok=%d" % (i, end - start, n_ok), flush=True)

print("DONE ok=%d/%d" % (n_ok, end - start), flush=True)
