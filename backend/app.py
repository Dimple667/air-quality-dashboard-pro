"""本地开发用的 Flask 服务（Netlify 上由 netlify/functions/api.mjs 承担同样的接口）。

业务逻辑全部在 air_quality_core.py 中，本文件只负责 HTTP 层。
"""

from __future__ import annotations

from contextlib import closing
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from air_quality_core import (
    NoDataError,
    build_dashboard_data,
    connect,
    init_db,
    list_cities,
)

# 所有路径基于本文件所在目录计算，不依赖终端工作目录
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "air_quality.db"

app = Flask(__name__)
CORS(app)

# 本地开发（debug=True）时也统一走 JSON 错误处理，
# 避免把 Python traceback 直接返回给前端。
app.config["PROPAGATE_EXCEPTIONS"] = False


def get_conn():
    return connect(DB_PATH)


def ok(data):
    """统一成功响应结构。"""
    return jsonify({"code": 0, "message": "success", "data": data})


def fail(message: str, code: int = 500):
    """统一失败响应结构。"""
    return jsonify({"code": code, "message": message, "data": None}), code


@app.errorhandler(404)
def not_found(_):
    return fail("接口不存在", 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return fail("请求方法不允许", 405)


@app.errorhandler(NoDataError)
def no_data(e):
    return fail(str(e))


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
        return ok(list_cities(conn))


@app.get("/api/dashboard_data")
def dashboard_data():
    with closing(get_conn()) as conn:
        return ok(build_dashboard_data(conn, request.args.get("city") or ""))


if __name__ == "__main__":
    with closing(get_conn()) as conn:
        init_db(conn)
    # 仅作为本地开发使用
    app.run(host="127.0.0.1", port=5000, debug=True)
