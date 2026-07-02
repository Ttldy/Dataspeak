"""Read-only SQL execution and demo DB initialization."""

from __future__ import annotations

import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

from dataspeak.schema_index.schema_store import project_sqlite_path


def ensure_demo_sqlite(db_path: str | Path | None = None) -> Path:
    """Create a SQLite demo database when it does not exist."""

    path = Path(db_path or project_sqlite_path())
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(_sqlite_schema())
        conn.commit()
    finally:
        conn.close()
    return path


def execute_sql(sql: str, database: str = "dataspeak_demo", db_path: str | Path | None = None) -> Dict[str, Any]:
    """Execute a read-only SQL query and return a structured log."""

    start = time.perf_counter()
    path = ensure_demo_sqlite(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description or []]
        preview = [dict(row) for row in rows[:50]]
        return {
            "database": database,
            "sql": sql,
            "success": True,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "row_count": len(rows),
            "columns": columns,
            "preview_rows": preview,
            "error_message": None,
        }
    except Exception as exc:
        return {
            "database": database,
            "sql": sql,
            "success": False,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "row_count": 0,
            "columns": [],
            "preview_rows": [],
            "error_message": str(exc),
        }
    finally:
        conn.close()


def execute_sql_steps(sql_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute generated SQL steps in order."""

    results = []
    for item in sql_list:
        if not item.get("safety_passed"):
            results.append(
                {
                    "database": item["database"],
                    "sql": item["sql"],
                    "success": False,
                    "duration_ms": 0,
                    "row_count": 0,
                    "columns": [],
                    "preview_rows": [],
                    "error_message": item.get("error_message") or "SQL safety audit failed.",
                    "step": item["step"],
                }
            )
            continue
        result = execute_sql(item["sql"], database=item["database"])
        result["step"] = item["step"]
        results.append(result)
    return results


def explain_sql(sql: str) -> Dict[str, Any]:
    """Return a lightweight SQLite query plan."""

    path = ensure_demo_sqlite()
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute(f"EXPLAIN QUERY PLAN {sql}").fetchall()
        return {"sql": sql, "plan": [tuple(row) for row in rows]}
    finally:
        conn.close()


def _sqlite_schema() -> str:
    """SQLite-compatible schema and seed data."""

    return """
    CREATE TABLE customers (
      customer_id INTEGER PRIMARY KEY,
      customer_name TEXT NOT NULL,
      city TEXT NOT NULL,
      customer_level TEXT NOT NULL,
      registered_at DATE NOT NULL
    );
    CREATE TABLE products (
      product_id INTEGER PRIMARY KEY,
      product_name TEXT NOT NULL,
      category TEXT NOT NULL,
      list_price REAL NOT NULL,
      unit_cost REAL NOT NULL,
      is_active INTEGER NOT NULL
    );
    CREATE TABLE orders (
      order_id INTEGER PRIMARY KEY,
      customer_id INTEGER NOT NULL,
      order_date DATE NOT NULL,
      status TEXT NOT NULL,
      total_amount REAL NOT NULL,
      FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE order_items (
      item_id INTEGER PRIMARY KEY,
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      unit_price REAL NOT NULL,
      line_amount REAL NOT NULL,
      FOREIGN KEY(order_id) REFERENCES orders(order_id),
      FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    CREATE TABLE payments (
      payment_id INTEGER PRIMARY KEY,
      order_id INTEGER NOT NULL,
      payment_method TEXT NOT NULL,
      paid_amount REAL NOT NULL,
      payment_status TEXT NOT NULL,
      FOREIGN KEY(order_id) REFERENCES orders(order_id)
    );
    CREATE TABLE refunds (
      refund_id INTEGER PRIMARY KEY,
      item_id INTEGER NOT NULL,
      refund_amount REAL NOT NULL,
      refund_reason TEXT NOT NULL,
      refund_status TEXT NOT NULL,
      FOREIGN KEY(item_id) REFERENCES order_items(item_id)
    );
    CREATE TABLE marketing_events (
      event_id INTEGER PRIMARY KEY,
      customer_id INTEGER NOT NULL,
      event_name TEXT NOT NULL,
      channel TEXT NOT NULL,
      event_date DATE NOT NULL,
      converted INTEGER NOT NULL,
      FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE customer_feedback (
      feedback_id INTEGER PRIMARY KEY,
      customer_id INTEGER NOT NULL,
      order_id INTEGER NOT NULL,
      rating INTEGER NOT NULL,
      feedback_text TEXT NOT NULL,
      created_at DATE NOT NULL,
      FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
      FOREIGN KEY(order_id) REFERENCES orders(order_id)
    );
    INSERT INTO customers VALUES
      (1,'Alice','北京','gold','2026-01-04'),(2,'Bob','上海','silver','2026-02-11'),
      (3,'Cathy','深圳','gold','2026-03-02'),(4,'David','杭州','bronze','2026-03-18'),
      (5,'Eva','北京','platinum','2026-04-01'),(6,'Frank','成都','silver','2026-04-18'),
      (7,'Grace','武汉','bronze','2026-05-01'),(8,'Henry','广州','gold','2026-05-15');
    INSERT INTO products VALUES
      (1,'智能音箱','硬件',299,120,1),(2,'AI写作会员','订阅',99,15,1),(3,'数据分析课','课程',499,80,1),
      (4,'智能手环','硬件',199,70,1),(5,'企业插件包','软件',899,200,1),(6,'降噪耳机','硬件',599,240,1);
    INSERT INTO orders VALUES
      (1001,1,date('now','-5 day'),'paid',398),(1002,2,date('now','-12 day'),'paid',998),
      (1003,3,date('now','-25 day'),'refunded',599),(1004,4,date('now','-75 day'),'paid',199),
      (1005,5,date('now','-2 day'),'paid',1397),(1006,1,date('now','-35 day'),'paid',99),
      (1007,6,date('now','-18 day'),'paid',499),(1008,8,date('now','-8 day'),'paid',798);
    INSERT INTO order_items VALUES
      (1,1001,1,1,299,299),(2,1001,2,1,99,99),(3,1002,3,2,499,998),(4,1003,6,1,599,599),
      (5,1004,4,1,199,199),(6,1005,5,1,899,899),(7,1005,3,1,499,499),(8,1006,2,1,99,99),
      (9,1007,3,1,499,499),(10,1008,1,1,299,299),(11,1008,4,1,199,199),(12,1008,2,3,100,300);
    INSERT INTO payments VALUES
      (1,1001,'alipay',398,'success'),(2,1002,'card',998,'success'),(3,1003,'wechat',599,'success'),
      (4,1004,'alipay',199,'success'),(5,1005,'card',1397,'success'),(6,1006,'wechat',99,'success'),
      (7,1007,'alipay',499,'success'),(8,1008,'card',798,'success');
    INSERT INTO refunds VALUES
      (1,4,599,'降噪效果不满意','approved'),(2,3,200,'课程重复购买','approved'),(3,11,199,'尺寸不合适','approved');
    INSERT INTO marketing_events VALUES
      (1,1,'618促销','短信',date('now','-20 day'),1),(2,2,'新品试用','公众号',date('now','-70 day'),0),
      (3,4,'老客召回','邮件',date('now','-10 day'),0),(4,7,'618促销','短信',date('now','-15 day'),0),
      (5,8,'会员日','App Push',date('now','-9 day'),1);
    INSERT INTO customer_feedback VALUES
      (1,3,1003,2,'耳机降噪没有预期好',date('now','-24 day')),(2,5,1005,5,'企业插件很实用',date('now','-1 day')),
      (3,2,1002,3,'课程内容还可以',date('now','-10 day')),(4,8,1008,2,'物流慢且包装破损',date('now','-6 day')),
      (5,1,1001,5,'音箱体验很好',date('now','-4 day'));
    """


def mysqlish_to_sqlite(sql_text: str) -> str:
    """Convert a small MySQL-ish seed file to SQLite-compatible SQL."""

    text = re.sub(r"--.*", "", sql_text)
    text = text.replace("AUTO_INCREMENT", "")
    text = re.sub(r"\bDECIMAL\([^)]*\)", "REAL", text)
    text = re.sub(r"\bTINYINT\b", "INTEGER", text)
    text = re.sub(r"\bVARCHAR\([^)]*\)", "TEXT", text)
    return text
