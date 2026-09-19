# -*- coding: utf-8 -*-
"""本地下载器: 拉取 GitHub Actions 产出的 baostock 批次 artifacts。
用法: python gh_download.py [--once]
--once: 只跑一轮(轮询完成批并下载), 否则循环直到全下载完或超时。
存储: E:\QuantLab\data\prices\baostock_gh\ (源隔离)
清单: E:\QuantLab\github_pull\batch_state.json
"""
import json
import os
import subprocess
import sys
import time

REPO = "x9420/quantlab-data-pull"
OUT = r"E:\QuantLab\data\prices\baostock_gh"
OUT_MIN5 = r"E:\QuantLab\data\minute\events5m"
os.makedirs(OUT_MIN5, exist_ok=True)
STATE = r"E:\QuantLab\github_pull\batch_state.json"
os.makedirs(OUT, exist_ok=True)

BATCHES = [("0", "10")]  # 探针批先算上
for i in range(10, 5200, 250):
    BATCHES.append((str(i), str(min(i + 250, 5200))))


def sh(cmd, timeout=120):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or "")


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {}


def save_state(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    state = load_state()
    if "done_batches" not in state:
        state["done_batches"] = {}
    # 扫描已完成 run
    txt = sh(["gh", "run", "list", "--repo", REPO, "--limit", "40", "--json",
              "databaseId,status,name,displayTitle,conclusion"])
    try:
        runs = json.loads(txt[txt.index("["):])
    except Exception:
        print("gh run list 解析失败", txt[:200])
        return
    for r in runs:
        name = r.get("displayTitle") or r.get("name") or ""
        if name not in ("bs-pull", "min5-pull"):
            continue
        out_dir = OUT if name == "bs-pull" else OUT_MIN5
        did = str(r["databaseId"])
        if did in state["done_batches"]:
            continue
        if r.get("status") != "completed":
            continue
        if r.get("conclusion") != "success":
            print("run %s 失败(conclusion=%s)，跳过" % (did, r.get("conclusion")))
            state["done_batches"][did] = "failed"
            save_state(state)
            continue
        print("下载 run %s ..." % did)
        tmp = r"E:\QuantLab\data_pull\tmp_gh\run_%s" % did
        os.makedirs(tmp, exist_ok=True)
        out = sh(["gh", "run", "download", did, "--repo", REPO, "--dir", tmp], timeout=600)
        n = 0
        for root, _, files in os.walk(tmp):
            for f in files:
                if f.endswith(".csv"):
                    src = os.path.join(root, f)
                    dst = os.path.join(out_dir, f)
                    if not os.path.exists(dst):
                        try:
                            os.replace(src, dst)
                            n += 1
                        except Exception as e:
                            print("  移动失败 %s: %s" % (f, e))
        print("  run %s 入库 %d 个文件" % (did, n))
        state["done_batches"][did] = {"run": did, "files": n}
        save_state(state)
    total = len([f for f in os.listdir(OUT) if f.endswith(".csv")])
    print("累计入库: %d 个文件 / 批次完成 %d/%d" % (total, len(state["done_batches"]), len(BATCHES)))
    return total


if __name__ == "__main__":
    once = "--once" in sys.argv
    t0 = time.time()
    while True:
        total = main()
        if once or total >= 5200:
            break
        if time.time() - t0 > 6 * 3600:
            print("超时退出")
            break
        time.sleep(300)
