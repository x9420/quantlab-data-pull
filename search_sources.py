# -*- coding: utf-8 -*-
"""GitHub 搜索涨停相关数据仓库 (正确 URL 编码)"""
import subprocess
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

queries = ["涨停板 数据", "涨停池", "涨停 历史", "limit up A-share data"]
for q in queries:
    url = "search/repositories?q=%s&sort=stars&per_page=8" % quote(q)
    r = subprocess.run(["gh", "api", url, "--jq",
                        ".items[] | .full_name + \" \" + (.stargazers_count|tostring) + \" \" + (.description // \"\")"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    print("=== %s ===" % q)
    print((r.stdout or r.stderr)[:500])
    print()
