# 집노트 - 매물사이트 구조 이중화 시스템

## 🏗️ 시스템 구조

### 매물사이트 이중화
- **주거용 사이트** (`주거용.py`) - 포트 5000
  - 아파트, 원룸, 오피스텔 등 주거용 매물 관리
  - 데이터베이스: `주거용.db`
  - 기존 Toss 스타일 UI/UX 유지

- **업무용 사이트** (`업무용.py`) - 포트 5001
  - 오피스, 상가, 업무공간 등 업무용 매물 관리
  - 데이터베이스: `업무용.db`
  - **에르메스 감성 프리미엄 UI/UX** 적용

- **관리자페이지** (`관리자페이지.py`) - 포트 8080
  - 직원 관리 및 시스템 통합 관리
  - 사이트 전환 UI 제공 (드롭다운 메뉴)
  - 데이터베이스: `admin_system.db`

## 🎨 에르메스 감성 디자인 (업무용 사이트)

### 색상 팔레트
- **Primary Orange**: `#FF6B00` (톤 다운된 오렌지)
- **Deep Brown**: `#3E2723` (딥 브라운)
- **Cream**: `#FFF8E1` (크림)
- **Charcoal**: `#2C2C2C` (차콜)
- **Gold**: `#FFD700` (골드 악센트)

### 디자인 특징
- **입체감과 그라데이션**: 버튼과 카드에 깊이감 있는 그림자
- **고급스러운 애니메이션**: 부드러운 hover 효과와 트랜지션
- **마이크로 인터랙션**: 세련된 UI 반응
- **프리미엄 타이포그래피**: Playfair Display + Pretendard 조합
- **반응형 디자인**: 모바일 최적화

## 🚀 실행 방법

### 방법 1: 배치 파일 사용 (권장)
```bash
start_servers.bat
```

### 방법 2: 개별 실행
```bash
# 주거용 사이트
python 주거용.py

# 업무용 사이트  
python 업무용.py

# 관리자페이지
python 관리자페이지.py
```

## 🌐 접속 주소

| 사이트 | 주소 | 설명 |
|--------|------|------|
| 주거용 사이트 | http://localhost:5000 | 주거용 매물 관리 |
| 업무용 사이트 | http://localhost:5001 | 업무용 매물 관리 (에르메스 UI) |
| 관리자페이지 | http://localhost:8080 | 통합 관리 및 사이트 전환 |

## 📁 데이터베이스 구조

### 분리된 데이터베이스
- `주거용.db`: 주거용 매물 데이터
- `업무용.db`: 업무용 매물 데이터  
- `admin_system.db`: 관리자 및 직원 데이터
- `admin_property.db`: 관리자 매물 데이터

### 테이블 구조
```sql
-- 매물 테이블 (주거용.db, 업무용.db)
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    platform TEXT NOT NULL,
    added_by TEXT NOT NULL,
    date_added TEXT NOT NULL,
    rating INTEGER DEFAULT 5,
    liked BOOLEAN DEFAULT 0,
    disliked BOOLEAN DEFAULT 0,
    memo TEXT DEFAULT '',
    customer_name TEXT DEFAULT '000',
    move_in_date TEXT DEFAULT '',
    management_site_id TEXT DEFAULT NULL,
    guarantee_insurance BOOLEAN DEFAULT 0
);
```

## 🎯 주요 기능

### 관리자페이지 사이트 전환
- 헤더의 "사이트 관리" 드롭다운 클릭
- 주거용/업무용 사이트로 바로 이동
- 새 탭에서 열림

### 에르메스 감성 UI (업무용)
- 고급스러운 그라데이션 버튼
- 부드러운 카드 호버 효과
- 프리미엄 색상 팔레트
- 입체적인 그림자 효과
- 우아한 애니메이션

### 데이터 완전 분리
- 주거용과 업무용 매물 데이터 독립
- 각 사이트별 전용 DB 접근
- 관리자페이지에서 통합 관리

## 🛠️ 기술 스택

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Custom (Toss 스타일 + 에르메스 감성)
- **Typography**: Pretendard, Playfair Display
- **Icons**: Unicode Emoji

## 📋 개발 완료 사항

✅ app.py → 주거용.py 분리  
✅ 업무용.py 생성 (포트 5001)  
✅ 데이터베이스 완전 분리  
✅ 에르메스 감성 UI/UX 적용  
✅ 관리자페이지 사이트 전환 UI  
✅ 반응형 디자인 최적화  
✅ 배치 파일 자동 실행  

---

**🎨 에르메스 감성의 프리미엄 업무공간 매물 관리 시스템**
