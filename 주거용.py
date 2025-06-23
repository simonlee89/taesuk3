from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import os
import json

app = Flask(__name__)

# 데이터베이스 연결 함수 (integrated.db만 사용)
def get_db_connection():
    conn = sqlite3.connect('integrated.db')
    return conn

# 고객 정보 조회 함수 (integrated.db만 사용)
def get_customer_info(management_site_id):
    print(f"[DEBUG] get_customer_info 호출됨 - management_site_id: {management_site_id}")
    customer_name = None
    move_in_date = ''
    try:
        system_conn = sqlite3.connect('integrated.db')
        system_cursor = system_conn.cursor()
        system_cursor.execute('''
            SELECT customer_name, move_in_date 
            FROM employee_customers 
            WHERE management_site_id = ?
        ''', (management_site_id,))
        customer_data = system_cursor.fetchone()
        print(f"[DEBUG] integrated.db 조회 결과: {customer_data}")
        system_conn.close()
        if customer_data:
            customer_name = customer_data[0] if customer_data[0] else '고객'
            move_in_date = customer_data[1] if customer_data[1] else ''
            print(f"[DEBUG] 고객 정보 찾음 - 이름: {customer_name}, 입주일: {move_in_date}")
            return customer_name, move_in_date, True
    except sqlite3.Error as e:
        print(f"integrated.db 조회 실패: {e}")
    print(f"[DEBUG] 고객 정보를 찾을 수 없음: {management_site_id}")
    return None, '', False

# 데이터베이스 초기화 (integrated.db만)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # links 테이블 생성
    cursor.execute('''
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
            is_checked INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0,
            residence_extra TEXT DEFAULT ''
        )
    ''')
    # customer_info 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_info (
            id INTEGER PRIMARY KEY,
            customer_name TEXT DEFAULT '000',
            move_in_date TEXT DEFAULT ''
        )
    ''')
    # guarantee_insurance_log 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guarantee_insurance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            management_site_id TEXT,
            link_id INTEGER,
            click_time TEXT,
            user_ip TEXT
        )
    ''')
    # 기본 고객 정보 삽입
    cursor.execute('INSERT OR IGNORE INTO customer_info (id, customer_name, move_in_date) VALUES (1, "제일좋은집 찾아드릴분", "")')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT customer_name, move_in_date FROM customer_info WHERE id = 1')
    customer_info = cursor.fetchone()
    customer_name = customer_info[0] if customer_info else '제일좋은집 찾아드릴분'
    move_in_date = customer_info[1] if customer_info else ''
    conn.close()
    # 로그인된 직원의 employee_id를 템플릿 변수로 전달
    from flask import session
    employee_id = session.get('employee_id', '')
    return render_template('index.html', customer_name=customer_name, move_in_date=move_in_date, employee_id=employee_id)

@app.route('/customer/<management_site_id>')
def customer_site(management_site_id):
    print(f"고객 사이트 접근 - management_site_id: {management_site_id}")
    customer_name, move_in_date, found = get_customer_info(management_site_id)
    if not found:
        print(f"고객 정보를 찾을 수 없음: {management_site_id}")
        return render_template('customer_site.html'), 404
    else:
        print(f"고객 정보 조회 성공 - 이름: {customer_name}, 입주일: {move_in_date}")
    # 미확인 좋아요 is_checked=0 → 1로 일괄 갱신
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE links SET is_checked = 1 WHERE management_site_id = ? AND liked = 1 AND is_checked = 0', (management_site_id,))
    conn.commit()
    conn.close()
    return render_template('index.html', 
                         customer_name=customer_name, 
                         move_in_date=move_in_date,
                         management_site_id=management_site_id)

@app.route('/api/customer_info', methods=['GET', 'POST'])
def customer_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    management_site_id = request.args.get('management_site_id')
    if management_site_id:
        _, _, found = get_customer_info(management_site_id)
        if not found:
            conn.close()
            return jsonify({'success': False, 'error': '고객 정보를 찾을 수 없습니다. 삭제되었거나 존재하지 않는 고객입니다.'}), 404
    if request.method == 'POST':
        data = request.json
        customer_name = data.get('customer_name', '제일좋은집 찾아드릴분')
        move_in_date = data.get('move_in_date', '')
        if not move_in_date:
            move_in_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('UPDATE customer_info SET customer_name = ?, move_in_date = ? WHERE id = 1', 
                      (customer_name, move_in_date))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    else:
        cursor.execute('SELECT customer_name, move_in_date FROM customer_info WHERE id = 1')
        info = cursor.fetchone()
        conn.close()
        return jsonify({
            'customer_name': info[0] if info else '제일좋은집 찾아드릴분',
            'move_in_date': info[1] if info else ''
        })

@app.route('/api/links', methods=['GET', 'POST'])
def links():
    conn = get_db_connection()
    cursor = conn.cursor()
    management_site_id = request.args.get('management_site_id')
    if request.method == 'POST':
        data = request.json
        url = data.get('url')
        platform = data.get('platform')
        from flask import session
        added_by = session.get('employee_id', '중개사')
        memo = data.get('memo', '')
        guarantee_insurance = data.get('guarantee_insurance', False)
        residence_extra = data.get('residence_extra', '')
        if not url or not platform or not added_by:
            return jsonify({'success': False, 'error': '필수 정보가 누락되었습니다.'})
        date_added = datetime.now().strftime('%Y-%m-%d')
        if management_site_id:
            _, _, found = get_customer_info(management_site_id)
            if not found:
                return jsonify({'success': False, 'error': '존재하지 않는 고객입니다.'})
        cursor.execute('''
            INSERT INTO links (url, platform, added_by, date_added, memo, management_site_id, guarantee_insurance, residence_extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url, platform, added_by, date_added, memo, management_site_id, guarantee_insurance, residence_extra))
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"새 링크 추가됨 - ID: {link_id}, 고객: {management_site_id or '기본'}")
        return jsonify({'success': True, 'id': link_id})
    else:
        platform_filter = request.args.get('platform', 'all')
        user_filter = request.args.get('user', 'all')
        like_filter = request.args.get('like', 'all')
        date_filter = request.args.get('date', '')
        guarantee_filter = request.args.get('guarantee', 'all')
        query = 'SELECT * FROM links WHERE 1=1'
        params = []
        if management_site_id:
            print(f"고객별 링크 조회 - management_site_id: {management_site_id}")
            query += ' AND management_site_id = ?'
            params.append(management_site_id)
        else:
            query += ' AND management_site_id IS NULL'
        if platform_filter != 'all':
            query += ' AND platform = ?'
            params.append(platform_filter)
        if user_filter != 'all':
            query += ' AND added_by = ?'
            params.append(user_filter)
        if like_filter == 'liked':
            query += ' AND liked = 1'
        elif like_filter == 'disliked':
            query += ' AND disliked = 1'
        if date_filter:
            query += ' AND date_added = ?'
            params.append(date_filter)
        if guarantee_filter == 'available':
            query += ' AND guarantee_insurance = 1'
        elif guarantee_filter == 'unavailable':
            query += ' AND guarantee_insurance = 0'
        query += ' ORDER BY id DESC'
        cursor.execute(query, params)
        links_data = cursor.fetchall()
        total_count = len(links_data)
        conn.close()
        links_list = []
        for index, link in enumerate(links_data):
            link_number = total_count - index
            links_list.append({
                'id': link[0],
                'number': link_number,
                'url': link[1],
                'platform': link[2],
                'added_by': link[3],
                'date_added': link[4],
                'rating': link[5],
                'liked': bool(link[6]),
                'disliked': bool(link[7]),
                'memo': link[8] if len(link) > 8 else '',
                'guarantee_insurance': bool(link[12]) if len(link) > 12 else False
            })
        print(f"링크 조회 완료 - 총 {len(links_list)}개, 고객: {management_site_id or '기본'}")
        return jsonify(links_list)

@app.route('/api/links/<int:link_id>', methods=['PUT', 'DELETE'])
def update_link(link_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT management_site_id FROM links WHERE id = ?', (link_id,))
    link_result = cursor.fetchone()
    if link_result and link_result[0]:
        management_site_id = link_result[0]
        _, _, found = get_customer_info(management_site_id)
        if not found:
            conn.close()
            return jsonify({'success': False, 'error': '삭제된 고객의 링크입니다. 작업을 수행할 수 없습니다.'}), 404
    if request.method == 'PUT':
        data = request.json
        action = data.get('action')
        if action == 'rating':
            rating = data.get('rating', 5)
            cursor.execute('UPDATE links SET rating = ? WHERE id = ?', (rating, link_id))
        elif action == 'like':
            liked = data.get('liked', False)
            cursor.execute('UPDATE links SET liked = ?, disliked = ?, is_checked = 0 WHERE id = ?', (liked, 0 if liked else 0, link_id))
        elif action == 'dislike':
            disliked = data.get('disliked', False)
            cursor.execute('UPDATE links SET disliked = ?, liked = ? WHERE id = ?', (disliked, 0 if disliked else 0, link_id))
        elif action == 'memo':
            memo = data.get('memo', '')
            cursor.execute('UPDATE links SET memo = ? WHERE id = ?', (memo, link_id))
        elif action == 'guarantee':
            guarantee_insurance = data.get('guarantee_insurance', False)
            cursor.execute('UPDATE links SET guarantee_insurance = ? WHERE id = ?', (guarantee_insurance, link_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM links WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/backup', methods=['GET'])
def backup_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'links': [],
            'customer_info': None
        }
        cursor.execute('SELECT * FROM links')
        links = cursor.fetchall()
        cursor.execute("PRAGMA table_info(links)")
        columns = [row[1] for row in cursor.fetchall()]
        for link in links:
            link_dict = dict(zip(columns, link))
            backup_data['links'].append(link_dict)
        cursor.execute('SELECT * FROM customer_info')
        customer = cursor.fetchone()
        if customer:
            cursor.execute("PRAGMA table_info(customer_info)")
            customer_columns = [row[1] for row in cursor.fetchall()]
            backup_data['customer_info'] = dict(zip(customer_columns, customer))
        conn.close()
        return jsonify(backup_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/restore', methods=['POST'])
def restore_data():
    try:
        backup_data = request.json
        if not backup_data or 'links' not in backup_data:
            return jsonify({'success': False, 'error': '잘못된 백업 데이터입니다.'})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM links')
        cursor.execute('DELETE FROM customer_info')
        if backup_data.get('customer_info'):
            customer_info = backup_data['customer_info']
            cursor.execute('''
                INSERT INTO customer_info (id, customer_name, move_in_date)
                VALUES (?, ?, ?)
            ''', (
                customer_info.get('id', 1),
                customer_info.get('customer_name', '제일좋은집 찾아드릴분'),
                customer_info.get('move_in_date', '')
            ))
        else:
            cursor.execute('INSERT INTO customer_info (id, customer_name, move_in_date) VALUES (1, "제일좋은집 찾아드릴분", "")')
        for link_data in backup_data['links']:
            cursor.execute('''
                INSERT INTO links (url, platform, added_by, date_added, rating, liked, disliked, memo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                link_data.get('url', ''),
                link_data.get('platform', 'other'),
                link_data.get('added_by', 'unknown'),
                link_data.get('date_added', datetime.now().strftime('%Y-%m-%d')),
                link_data.get('rating', 5),
                link_data.get('liked', 0),
                link_data.get('disliked', 0),
                link_data.get('memo', '')
            ))
        conn.commit()
        conn.close()
        return jsonify({
            'success': True, 
            'message': f'{len(backup_data["links"])}개의 링크가 복원되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/cleanup-customer-links/<management_site_id>', methods=['DELETE'])
def cleanup_customer_links(management_site_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM links WHERE management_site_id = ?', (management_site_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"관리자페이지 요청으로 management_site_id {management_site_id} 관련 링크 {deleted_count}개 삭제됨")
        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        print(f"링크 정리 실패: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/guarantee-log', methods=['POST'])
def guarantee_log():
    data = request.get_json()
    link_id = data.get('link_id')
    if not link_id:
        return jsonify({'success': False, 'message': 'link_id가 필요합니다.'})
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE links SET guarantee_insurance = 1 WHERE id = ?', (link_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/guarantee-insurance-reset', methods=['POST'])
def guarantee_insurance_reset():
    data = request.get_json()
    employee_id = data.get('employee_id')
    if not employee_id:
        return jsonify({'success': False, 'message': 'employee_id 누락'}), 400
    try:
        conn = sqlite3.connect('integrated.db')
        c = conn.cursor()
        c.execute("UPDATE links SET guarantee_insurance = 0 WHERE added_by = ?", (employee_id,))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'affected': affected})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def auto_expire_guarantee_insurance():
    """보증보험이 1이고 date_added가 30일 이상 지난 링크는 guarantee_insurance를 0으로 자동 변경"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # SQLite에서 날짜 차이 계산: julianday('now') - julianday(date_added)
    cursor.execute('''
        UPDATE links
        SET guarantee_insurance = 0
        WHERE guarantee_insurance = 1
        AND date(date_added) IS NOT NULL
        AND (julianday('now') - julianday(date_added)) >= 30
    ''')
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected:
        print(f"만료된 보증보험 {affected}건 자동 해제 완료")

if __name__ == '__main__':
    init_db()
    auto_expire_guarantee_insurance()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 