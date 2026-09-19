# -*- coding: utf-8 -*-
"""查排队/运行中批次的覆盖范围, 用于取消重排小批次"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = "x9420/quantlab-data-pull"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.stdout or ""


def run_ids(status):
    out = sh(["gh", "api", f"repos/{REPO}/actions/runs?status={status}&per_page=50",
              "--jq", ".workflow_runs[].id"])
    return [l for l in out.splitlines() if l.strip().isdigit()]


def batch_range(run_id):
    out = sh(["gh", "api", f"repos/{REPO}/actions/runs/{run_id}/jobs",
              "--jq", ".jobs[].steps[] | select(.name==\"Pull batch\") | .number"])
    if not out.strip():
        return None
    # 用 logs 拿 args 不直接; 改查 jobs steps 的 args? 尝试下载日志太慢。
    # 备选: 用 runs 的 display_title? 无 inputs。用 check-runs? 
    # 直接读 job 的 steps -> logs 需要; 这里返回 run_id 供外部 gh run view 处理
    return run_id


queued = run_ids("queued")
progress = run_ids("in_progress")
print("queued:", queued)
print("in_progress:", progress)

# 用 gh run view 拉日志找 batch 参数 (在 log 的 args 里)
for rid in queued + progress:
    out = sh(["gh", "api", f"repos/{REPO}/actions/runs/{rid}/jobs",
              "--jq", ".jobs[] | .id"])
    job_ids = [l for l in out.splitlines() if l.strip().isdigit()]
    for jid in job_ids:
        log = sh(["gh", "api", f"repos/{REPO}/actions/jobs/{jid}/logs"])
        # 日志是文本, 找 python pull_bs.py X Y
        for line in log.splitlines():
            if "pull_bs.py" in line:
                print(f"run {rid}: {line.strip()[:80]}")
                break
