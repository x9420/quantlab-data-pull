# -*- coding: utf-8 -*-
"""探针: GitHub runner 上 baostock 5min 全历史速度
用法: python probe_bs5.py <code> <start_date>
"""
import sys
import time

import baostock as bs

code = sys.argv[1] if len(sys.argv) > 1 else "sh.600519"
start = sys.argv[2] if len(sys.argv) > 2 else "2020-01-01"

t0 = time.time()
lg = bs.login()
rs = bs.query_history_k_data_plus(code, "date,time,open,high,low,close,volume,amount",
                                  start_date=start, end_date="2026-09-19",
                                  frequency="5", adjustflag="2")
rows = []
while rs.error_code == "0" and rs.next():
    rows.append(rs.get_row_data())
bs.logout()
el = time.time() - t0
print("RESULT %s since=%s rows=%d seconds=%.1f err=%s" % (code, start, len(rows), el, rs.error_code), flush=True)
