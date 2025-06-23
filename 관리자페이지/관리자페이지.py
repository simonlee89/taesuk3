def permanent_delete_employee(emp_id):
    """직원 완전 삭제 (비활성화된 직원만, 모든 매물 숨김 처리 포함)"""
    import sqlite3
    import os
    import requests
    conn = sqlite3.connect('integrated.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_active, employee_id FROM employees WHERE id = ?', (emp_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'success': False, 'message': '직원을 찾을 수 없습니다.'})
    if result[0] == 1:
        conn.close()
        return jsonify({'success': False, 'message': '활성 상태인 직원은 완전 삭제할 수 없습니다. 먼저 비활성화해주세요.'})
    employee_id_value = result[1]
    # 보증보험 0 처리 (통합 DB)
    cursor.execute("UPDATE links SET guarantee_insurance = 0 WHERE added_by = ? OR added_by = ?", (employee_id_value, str(employee_id_value)))
    # 기존 고객/직원 완전 삭제 로직 유지
    cursor.execute('DELETE FROM employee_customers WHERE employee_id = ?', (employee_id_value,))
    cursor.execute('DELETE FROM employees WHERE id = ?', (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': '직원이 완전히 삭제(보증보험 0 및 row 삭제) 처리되었습니다.'})

def delete_employee(emp_id):
    """직원 삭제 (비활성화)"""
    import sqlite3
    import os
    import requests
    conn = sqlite3.connect('integrated.db')
    cursor = conn.cursor()
    # 직원의 employee_id 값 조회
    cursor.execute('SELECT employee_id FROM employees WHERE id = ?', (emp_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'success': False, 'message': '직원을 찾을 수 없습니다.'})
    employee_id_value = result[0]
    # 보증보험 0 처리 (통합 DB)
    cursor.execute("UPDATE links SET guarantee_insurance = 0 WHERE added_by = ? OR added_by = ?", (employee_id_value, str(employee_id_value)))
    # 기존 비활성화 로직
    cursor.execute('UPDATE employees SET is_active = 0 WHERE id = ?', (emp_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

def delete_customer_links_from_property_db(management_site_id):
    """매물 사이트 DB(통합 DB)에서 해당 고객의 링크들과 보증보험 로그 robust하게 삭제"""
    try:
        # 0. 먼저 guarantee_insurance를 0으로 업데이트
        robust_delete_query('integrated.db', "UPDATE links SET guarantee_insurance = 0 WHERE management_site_id = ?", (management_site_id,))
        # 1. links, guarantee_insurance_log robust 삭제
        robust_delete_query('integrated.db', "DELETE FROM links WHERE management_site_id = ?", (management_site_id,))
        robust_delete_query('integrated.db', "DELETE FROM guarantee_insurance_log WHERE management_site_id = ?", (management_site_id,))
        # links에서 삭제된 id로 guarantee_insurance_log도 추가 삭제 (link_id 기준)
        conn = sqlite3.connect('integrated.db', timeout=5.0)
        conn.execute('PRAGMA busy_timeout = 5000;')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM links WHERE management_site_id = ?", (management_site_id,))
        link_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        for link_id in link_ids:
            robust_delete_query('integrated.db', "DELETE FROM guarantee_insurance_log WHERE link_id = ?", (link_id,))
        return True
    except Exception as e:
        print('robust delete 실패:', e)
        return False

def ensure_is_deleted_column():
    """links 테이블에 is_deleted 컬럼이 없으면 추가 (통합 DB만)"""
    db_path = 'integrated.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(links)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'is_deleted' not in columns:
            cursor.execute("ALTER TABLE links ADD COLUMN is_deleted INTEGER DEFAULT 0")
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"{db_path} is_deleted 컬럼 추가 실패: {e}")

def hide_links_by_employee(employee_id, db_path):
    """해당 직원이 등록한 DB의 모든 매물 숨김 처리"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE links SET is_active = 0 WHERE added_by = ?", (employee_id,))
        conn.commit()
        conn.close()
        print(f"{db_path} 매물 숨기기 성공")
    except Exception as e:
        print(f"{db_path} 매물 숨기기 실패: {e}")

def get_unchecked_likes_count(management_site_id, db_path):
    """해당 매물 사이트의 미확인 좋아요 개수 반환"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM links WHERE management_site_id = ? AND is_active = 1 AND is_deleted = 0", (management_site_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"{db_path} 미확인 좋아요 개수 조회 실패: {e}")
        return 0

print('실제 연결된 DB 경로:', os.path.abspath('integrated.db')) 