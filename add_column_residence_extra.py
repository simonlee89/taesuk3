import sqlite3

conn = sqlite3.connect('integrated.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE links ADD COLUMN residence_extra TEXT DEFAULT ''")
    print('컬럼 추가 완료')
except Exception as e:
    print('에러:', e)
finally:
    conn.commit()
    conn.close() 