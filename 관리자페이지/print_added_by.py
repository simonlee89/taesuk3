import sqlite3

conn = sqlite3.connect('integrated.db')
cursor = conn.cursor()
cursor.execute('SELECT DISTINCT added_by FROM links')
rows = cursor.fetchall()
print('added_by 고유값 목록:')
for row in rows:
    print(row[0])
conn.close() 