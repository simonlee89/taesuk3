import sqlite3
import os

# 통합 DB 파일명
INTEGRATED_DB = 'integrated.db'

# 기존 DB 파일명
DB_FILES = ['admin_system.db', '주거용.db', '업무용.db']

# 테이블별 복사 쿼리
TABLES = [
    'employees',
    'employee_customers',
    'links',
    'customer_info',
    'guarantee_insurance_log'
]

def create_integrated_schema(conn):
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        name TEXT,
        is_active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS employee_customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        customer_name TEXT,
        move_in_date TEXT,
        management_site_id TEXT
    );
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        platform TEXT NOT NULL,
        added_by TEXT NOT NULL,
        date_added TEXT NOT NULL,
        rating INTEGER DEFAULT 5,
        liked INTEGER DEFAULT 0,
        disliked INTEGER DEFAULT 0,
        memo TEXT DEFAULT '',
        customer_name TEXT DEFAULT '000',
        move_in_date TEXT DEFAULT '',
        management_site_id TEXT DEFAULT NULL,
        guarantee_insurance INTEGER DEFAULT 0,
        is_checked INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS customer_info (
        id INTEGER PRIMARY KEY,
        customer_name TEXT DEFAULT '000',
        move_in_date TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS guarantee_insurance_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        management_site_id TEXT,
        link_id INTEGER,
        click_time TEXT,
        user_ip TEXT
    );
    """)
    conn.commit()

def copy_table_data(src_db, dst_conn, table):
    src_conn = sqlite3.connect(src_db)
    src_cursor = src_conn.cursor()
    dst_cursor = dst_conn.cursor()
    try:
        src_cursor.execute(f"SELECT * FROM {table}")
        rows = src_cursor.fetchall()
        if not rows:
            return
        placeholders = ','.join(['?'] * len(rows[0]))
        dst_cursor.executemany(
            f"INSERT INTO {table} VALUES ({placeholders})", rows
        )
        dst_conn.commit()
        print(f"{src_db} → {table} {len(rows)}개 복사 완료")
    except Exception as e:
        print(f"{src_db} → {table} 복사 실패: {e}")
    finally:
        src_conn.close()

def main():
    if os.path.exists(INTEGRATED_DB):
        print(f"{INTEGRATED_DB} 이미 존재. 삭제 후 새로 생성합니다.")
        os.remove(INTEGRATED_DB)
    conn = sqlite3.connect(INTEGRATED_DB)
    create_integrated_schema(conn)
    for db_file in DB_FILES:
        if not os.path.exists(db_file):
            print(f"{db_file} 없음, 건너뜀")
            continue
        for table in TABLES:
            copy_table_data(db_file, conn, table)
    conn.close()
    print("모든 데이터 이전 완료!")

if __name__ == "__main__":
    main() 