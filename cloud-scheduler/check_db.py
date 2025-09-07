import sqlite3

# 连接到数据库
conn = sqlite3.connect('generated_apps.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("数据库中的所有表:")
for table in tables:
    print(f"  - {table[0]}")

# 检查特定表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apps';")
apps_table = cursor.fetchone()

if apps_table:
    print("\n发现'apps'表!")
else:
    print("\n未发现'apps'表")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generated_apps';")
generated_apps_table = cursor.fetchone()

if generated_apps_table:
    print("发现'generated_apps'表!")
    # 检查表结构
    cursor.execute("PRAGMA table_info(generated_apps);")
    columns = cursor.fetchall()
    print("\n'generated_apps'表结构:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("未发现'generated_apps'表")

conn.close()