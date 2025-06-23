import subprocess
import time
import os
import sys
import sqlite3

def start_server(script_name, port, description):
    """개별 서버를 백그라운드에서 시작"""
    try:
        print(f"🚀 {description} 시작 중... (포트 {port})")
        
        # Windows에서 새 창으로 서버 시작
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                'cmd', '/c', 'start', 
                f'{description} (포트 {port})', 
                'cmd', '/k', 
                f'python {script_name}'
            ], shell=True)
        else:  # Linux/Mac
            subprocess.Popen([
                'gnome-terminal', '--', 
                'python3', script_name
            ])
            
        time.sleep(2)  # 서버 시작 대기
        print(f"✅ {description} 시작됨!")
        return True
        
    except Exception as e:
        print(f"❌ {description} 시작 실패: {e}")
        return False

def init_links_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            platform TEXT,
            added_by TEXT,
            date_added TEXT,
            rating INTEGER,
            liked INTEGER DEFAULT 0,
            disliked INTEGER DEFAULT 0,
            memo TEXT,
            management_site_id TEXT,
            guarantee_insurance INTEGER DEFAULT 0,
            is_checked INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0,
            office_extra TEXT,
            residence_extra TEXT
        )
    ''')
    # residence_extra 컬럼이 없으면 추가
    cursor.execute("PRAGMA table_info(links)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'residence_extra' not in columns:
        cursor.execute("ALTER TABLE links ADD COLUMN residence_extra TEXT DEFAULT ''")
    conn.commit()
    conn.close()

def get_unchecked_likes_count(management_site_id, db_path):
    # Implementation of get_unchecked_likes_count function
    pass

def main():
    print("🏡 매물사이트 구조 이중화 시스템 시작")
    print("=" * 40)
    print()
    print("🏠 주거용 사이트: http://localhost:5000")
    print("🏢 업무용 사이트: http://localhost:5001") 
    print("👤 관리자페이지: http://localhost:8080")
    print()
    print("서버를 시작합니다...")
    print()
    
    servers = [
        ("주거용.py", 5000, "주거용 사이트"),
        ("업무용.py", 5001, "업무용 사이트"), 
        ("관리자페이지.py", 8080, "관리자페이지")
    ]
    
    success_count = 0
    for script, port, desc in servers:
        if start_server(script, port, desc):
            success_count += 1
    
    print()
    if success_count == len(servers):
        print("✅ 모든 서버가 성공적으로 시작되었습니다!")
    else:
        print(f"⚠️  {success_count}/{len(servers)} 서버가 시작되었습니다.")
    
    print()
    print("🌐 브라우저에서 다음 주소로 접속하세요:")
    print("   - 주거용 사이트: http://localhost:5000")
    print("   - 업무용 사이트: http://localhost:5001 (에르메스 감성 UI)")
    print("   - 관리자페이지: http://localhost:8080 (사이트 전환 기능)")
    print()
    print("📁 데이터베이스 파일:")
    print("   - integrated.db (통합 매물/관리자 데이터)")
    print()
    
    input("계속하려면 Enter를 누르세요...")

    # 서버 시작 시 호출
    init_links_table('integrated.db')

    unchecked_likes_jug = get_unchecked_likes_count(management_site_id, 'integrated.db')
    unchecked_likes_work = get_unchecked_likes_count(management_site_id, 'integrated.db')

    conn = sqlite3.connect('integrated.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE links SET guarantee_insurance = 1 WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main() 