# -*- coding: utf-8 -*-
"""生成 GitHub 拉取用的股票清单 (baostock 格式 sh.600000)"""
import os

import pandas as pd

files = sorted(os.listdir(r"E:\QuantLab\data\prices\all_a"))
codes = []
for f in files:
    if f.endswith(".csv") and f.count("-") == 1:
        name = f[:-4]
        if name.startswith(("sh-", "sz-")):
            codes.append(name.replace("-", "."))
df = pd.DataFrame({"code": codes})
df.to_csv(r"E:\QuantLab\github_pull\stock_list.csv", index=False)
print("股票清单:", len(df), "只")
