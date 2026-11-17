import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS toilets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    building TEXT NOT NULL,
    floor INTEGER NOT NULL,
    toilet_type TEXT NOT NULL
)
""")

columns = [
    row[1] for row in cursor.execute(
        "PRAGMA table_info(toilets)"
    ).fetchall()
]

if "latitude" not in columns:
    cursor.execute(
        "ALTER TABLE toilets ADD COLUMN latitude REAL"
    )

if "longitude" not in columns:
    cursor.execute(
        "ALTER TABLE toilets ADD COLUMN longitude REAL"
    )

cursor.execute("""
UPDATE toilets
SET latitude = ?, longitude = ?
WHERE building = 'A'
AND floor = 1
AND toilet_type = '男子'
""", (35.0001, 136.0001))

cursor.execute("""
UPDATE toilets
SET latitude = ?, longitude = ?
WHERE building = 'A'
AND floor = 1
AND toilet_type = '女子'
""", (35.0002, 136.0002))

cursor.execute("""
UPDATE toilets
SET latitude = ?, longitude = ?
WHERE building = 'A'
AND floor = 2
AND toilet_type = '多目的'
""", (35.0003, 136.0003))

cursor.execute("""
UPDATE toilets
SET latitude = ?, longitude = ?
WHERE building = 'B'
AND floor = 1
AND toilet_type = '男子'
""", (35.0004, 136.0004))

conn.commit()

conn.close()

print("データベースを更新しました。")