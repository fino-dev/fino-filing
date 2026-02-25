import random
from datetime import datetime, timezone

import duckdb

# DB接続（ファイルでも :memory: でもOK）
conn = duckdb.connect("example.duckdb")

# テーブル作成
conn.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER,
    created_at TIMESTAMP NOT NULL,
    creatad_at_direct TIMESTAMP NOT NULL
)
""")

# ✅ UTCのdatetimeを生成
now_utc = datetime.now(timezone.utc)
print("utc: ", now_utc)
print(now_utc.tzinfo)
now = datetime.now()

# そのまま挿入（文字列化しない）
conn.execute(
    "INSERT INTO events VALUES (?, ?, ?)", (random.randint(1, 1000000), now_utc, now)
)

# 確認
result = conn.execute("SELECT id, created_at, creatad_at_direct FROM events").fetchall()
time_utc = result[-1][1]
time_local = result[-1][2]
print(result[-1])
print(isinstance(time_utc, datetime))
print("time_utc: ", time_utc)
print(isinstance(time_local, datetime))
print("time_local: ", time_local)
#
