import sqlite3

DB_PATH = 'integrated.db'

# 기존 데이터 일괄 변환 함수
def migrate_added_by_to_employee_id(db_path, old_value, new_employee_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE links SET added_by = ? WHERE added_by = ?", (new_employee_id, old_value))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"{affected}개의 links 레코드의 added_by 값을 '{old_value}'에서 '{new_employee_id}'로 변경 완료.")

def clear_all_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # sqlite의 시스템 테이블은 제외
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        cursor.execute(f'DELETE FROM {table_name};')
        # AUTOINCREMENT 초기화 (옵션)
        cursor.execute(f'DELETE FROM sqlite_sequence WHERE name=\'{table_name}\';')
    conn.commit()
    conn.close()
    print('모든 테이블의 데이터가 삭제되었습니다.')

if __name__ == '__main__':
    # 예시: '중개사'를 '1'로 변경
    migrate_added_by_to_employee_id(DB_PATH, '중개사', '1')
    # clear_all_tables(DB_PATH) 