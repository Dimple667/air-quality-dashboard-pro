#!/usr/bin/env python3
"""Netlify 构建阶段：把看板数据导出成函数可直接 import 的 JS 模块。

Netlify Functions 不支持 Python 运行时，所以聚合逻辑在构建阶段用 Python 跑完，
产物落到 netlify/data/snapshot.mjs，由 netlify/functions/api.mjs 在运行时读取。

演示数据按固定种子重新生成、日期窗口锚定到构建当天，
因此每次部署趋势图展示的都是"最近 14 天"，而不是仓库里那份过期数据。

用法（在仓库根目录执行）：
    python3 scripts/export_snapshot.py
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from air_quality_core import (  # noqa: E402  (需先设置 sys.path)
    DEMO_DAYS,
    build_dashboard_data,
    init_db,
    list_cities,
    trend_for_city,
)

OUT_PATH = ROOT / "netlify" / "data" / "snapshot.mjs"

# 各城市之间只有 selected_city / trend / update_time 不同，其余字段存一份即可
PER_CITY_FIELDS = ("selected_city", "trend", "update_time")


def build_snapshot() -> dict:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn, anchor=date.today())

    cities = list_cities(conn)

    # 不传 city 时由后端决定默认选中城市（AQI 最低的那个）
    default_payload = build_dashboard_data(conn, "")

    shared = {
        key: value
        for key, value in default_payload.items()
        if key not in PER_CITY_FIELDS
    }

    latest_date = conn.execute(
        "SELECT MAX(record_date) AS d FROM air_quality"
    ).fetchone()["d"]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_through": latest_date,
        "window_days": DEMO_DAYS,
        "cities": cities,
        "default_city": default_payload["selected_city"],
        "shared": shared,
        "trends": {city: trend_for_city(conn, city) for city in cities},
    }


def main() -> int:
    snapshot = build_snapshot()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))

    OUT_PATH.write_text(
        "// 本文件由 scripts/export_snapshot.py 自动生成，请勿手工编辑。\n"
        f"export default {payload}\n",
        encoding="utf-8",
    )

    size_kb = OUT_PATH.stat().st_size / 1024
    print(
        f"[snapshot] {len(snapshot['cities'])} 个城市 -> {OUT_PATH.relative_to(ROOT)} "
        f"({size_kb:.1f} KB, 数据截止 {snapshot['data_through']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
