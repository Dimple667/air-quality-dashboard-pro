from __future__ import annotations

import math
import random
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# 所有路径基于本文件所在目录计算，不依赖终端工作目录
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "air_quality.db"

app = Flask(__name__)
CORS(app)

# 本地开发（debug=True）时也统一走 JSON 错误处理，
# 避免把 Python traceback 直接返回给前端。
app.config["PROPAGATE_EXCEPTIONS"] = False

CITY_SEED = [
    ("北京", "北京市", "华北", 116.4074, 39.9042),
    ("天津", "天津市", "华北", 117.2008, 39.0842),
    ("上海", "上海市", "华东", 121.4737, 31.2304),
    ("南京", "江苏省", "华东", 118.7969, 32.0603),
    ("杭州", "浙江省", "华东", 120.1551, 30.2741),
    ("合肥", "安徽省", "华东", 117.2272, 31.8206),
    ("福州", "福建省", "华东", 119.2965, 26.0745),
    ("广州", "广东省", "华南", 113.2644, 23.1291),
    ("深圳", "广东省", "华南", 114.0579, 22.5431),
    ("南宁", "广西壮族自治区", "华南", 108.3200, 22.8240),
    ("海口", "海南省", "华南", 110.1983, 20.0440),
    ("武汉", "湖北省", "华中", 114.3055, 30.5928),
    ("长沙", "湖南省", "华中", 112.9388, 28.2282),
    ("郑州", "河南省", "华中", 113.6254, 34.7466),
    ("成都", "四川省", "西南", 104.0665, 30.5728),
    ("重庆", "重庆市", "西南", 106.5516, 29.5630),
    ("昆明", "云南省", "西南", 102.8329, 24.8801),
    ("西安", "陕西省", "西北", 108.9398, 34.3416),
    ("兰州", "甘肃省", "西北", 103.8343, 36.0611),
    ("乌鲁木齐", "新疆维吾尔自治区", "西北", 87.6168, 43.8256),
    ("沈阳", "辽宁省", "东北", 123.4315, 41.8057),
    ("长春", "吉林省", "东北", 125.3235, 43.8171),
    ("哈尔滨", "黑龙江省", "东北", 126.5349, 45.8038),
]


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ok(data):
    """统一成功响应结构。"""
    return jsonify({"code": 0, "message": "success", "data": data})


def fail(message: str, code: int = 500):
    """统一失败响应结构。"""
    return jsonify({"code": code, "message": message, "data": None}), code


def quality_level(aqi: int) -> str:
    if aqi <= 50:
        return "优"
    if aqi <= 100:
        return "良"
    if aqi <= 150:
        return "轻度污染"
    if aqi <= 200:
        return "中度污染"
    if aqi <= 300:
        return "重度污染"
    return "严重污染"


def init_db() -> None:
    with closing(get_conn()) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT UNIQUE NOT NULL,
            province TEXT NOT NULL,
            region TEXT NOT NULL,
            lng REAL NOT NULL,
            lat REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            record_date TEXT NOT NULL,
            aqi INTEGER NOT NULL,
            pm25 INTEGER NOT NULL,
            pm10 INTEGER NOT NULL,
            so2 INTEGER NOT NULL,
            no2 INTEGER NOT NULL,
            co REAL NOT NULL,
            o3 INTEGER NOT NULL,
            UNIQUE(city, record_date)
        );
        """)

        if conn.execute("SELECT COUNT(*) AS c FROM cities").fetchone()["c"] == 0:
            conn.executemany(
                "INSERT INTO cities(city, province, region, lng, lat) VALUES (?, ?, ?, ?, ?)",
                CITY_SEED,
            )

        if conn.execute("SELECT COUNT(*) AS c FROM air_quality").fetchone()["c"] == 0:
            rng = random.Random(20260906)
            today = date.today()
            rows = []

            for city, _, _, _, _ in CITY_SEED:
                base = rng.randint(45, 165)
                for days_ago in range(13, -1, -1):
                    d = today - timedelta(days=days_ago)
                    seasonal = int(18 * math.sin(days_ago / 2.2))
                    noise = rng.randint(-16, 16)
                    aqi = max(25, min(240, base + seasonal + noise))
                    pm25 = max(8, int(aqi * rng.uniform(0.45, 0.72)))
                    pm10 = max(15, int(aqi * rng.uniform(0.72, 1.05)))
                    so2 = rng.randint(4, 32)
                    no2 = rng.randint(12, 58)
                    co = round(rng.uniform(0.3, 1.7), 2)
                    o3 = rng.randint(35, 150)
                    rows.append((city, d.isoformat(), aqi, pm25, pm10, so2, no2, co, o3))

            conn.executemany("""
                INSERT OR IGNORE INTO air_quality
                (city, record_date, aqi, pm25, pm10, so2, no2, co, o3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)

        conn.commit()


def query_latest_rows(conn: sqlite3.Connection):
    latest_date = conn.execute("SELECT MAX(record_date) AS d FROM air_quality").fetchone()["d"]
    if latest_date is None:
        return []
    return conn.execute("""
        SELECT
            c.city, c.province, c.region, c.lng, c.lat,
            a.aqi, a.pm25, a.pm10, a.so2, a.no2, a.co, a.o3
        FROM cities c
        JOIN air_quality a ON a.city = c.city
        WHERE a.record_date = ?
        ORDER BY a.aqi ASC
    """, (latest_date,)).fetchall()


@app.errorhandler(404)
def not_found(_):
    return fail("接口不存在", 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return fail("请求方法不允许", 405)


@app.errorhandler(Exception)
def handle_exception(e):
    # 记录完整 traceback 到服务端日志，方便排查
    app.logger.exception("API 内部异常: %s", e)
    return fail("服务器内部错误")


@app.get("/api/health")
def health():
    return ok({"status": "ok"})


@app.get("/api/cities")
def cities():
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT city FROM cities ORDER BY id").fetchall()
    return ok([row["city"] for row in rows])


@app.get("/api/dashboard_data")
def dashboard_data():
    selected_city = (request.args.get("city") or "").strip()

    with closing(get_conn()) as conn:
        latest_rows = query_latest_rows(conn)
        if not latest_rows:
            return fail("数据库暂无空气质量数据")

        ranking = []
        region_values = {}
        level_distribution = {}

        for row in latest_rows:
            aqi = int(row["aqi"])
            level = quality_level(aqi)

            ranking.append({
                "city": row["city"],
                "province": row["province"],
                "aqi": aqi,
                "quality_level": level,
                "pm25": int(row["pm25"]),
                "pm10": int(row["pm10"]),
                "so2": int(row["so2"]),
                "no2": int(row["no2"]),
                "co": float(row["co"]),
                "o3": int(row["o3"]),
                "lng": float(row["lng"]),
                "lat": float(row["lat"]),
            })

            region_values.setdefault(row["region"], []).append(aqi)
            level_distribution[level] = level_distribution.get(level, 0) + 1

        region_stats = {
            region: round(sum(values) / len(values))
            for region, values in region_values.items()
        }

        all_names = [r["city"] for r in ranking]
        if not selected_city or selected_city not in all_names:
            selected_city = ranking[0]["city"]

        trend_rows = conn.execute("""
            SELECT record_date, aqi, pm25
            FROM air_quality
            WHERE city = ?
            ORDER BY record_date DESC
            LIMIT 7
        """, (selected_city,)).fetchall()

        trend = [
            {"date": row["record_date"], "aqi": int(row["aqi"]), "pm25": int(row["pm25"])}
            for row in reversed(trend_rows)
        ]

    avg_aqi = round(sum(item["aqi"] for item in ranking) / len(ranking))
    good = sum(item["aqi"] <= 100 for item in ranking)

    return ok({
        "total_cities": len(ranking),
        "avg_aqi": avg_aqi,
        "good_cities": good,
        "polluted_cities": len(ranking) - good,
        "city_ranking": ranking,
        "region_stats": region_stats,
        "level_distribution": level_distribution,
        "selected_city": selected_city,
        "trend": trend,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


if __name__ == "__main__":
    init_db()
    # 仅作为本地开发使用
    app.run(host="127.0.0.1", port=5000, debug=True)
