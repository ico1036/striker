# GTI657 Flight Tracker

실시간 항공편 추적 애플리케이션으로, Atlas Air의 GTI657 항공편(보잉 747-400)이 시카고(ORD)에서 서울(ICN)으로 가는 경로를 추적합니다.

## 📋 프로젝트 개요

이 프로젝트는 FlightAware에서 실시간 항공편 데이터를 스크래핑하여 웹 기반 인터랙티브 지도에 표시하는 애플리케이션입니다. Playwright를 사용하여 동적으로 로드되는 JavaScript 데이터를 추출하고, FastAPI로 RESTful API를 제공하며, Leaflet.js를 통해 지도에 항공편 경로와 현재 위치를 시각화합니다.

## ✨ 주요 기능

- ✅ **실시간 항공편 데이터**: FlightAware에서 라이브 항공편 데이터 추출
- ✅ **인터랙티브 지도**: Leaflet.js를 사용한 완전한 항공편 경로 표시
- ✅ **현재 위치 표시**: 항공기의 현재 위치를 마커로 표시
- ✅ **항공편 정보**: 출발지, 목적지, 항공기 종류, 고도, 좌표 정보 제공
- ✅ **자동 업데이트**: 30초마다 데이터 자동 갱신

## 🛠 기술 스택

- **백엔드**: FastAPI (Python 3.12+)
- **웹 스크래핑**: Playwright
- **프론트엔드**: HTML5, JavaScript, Leaflet.js
- **패키지 관리**: uv
- **테스트**: pytest, pytest-asyncio

## 📦 요구사항

- Python 3.12 이상
- `uv` 패키지 매니저
- Chromium 브라우저 (Playwright가 자동 설치)

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
# 프로젝트 의존성 설치
uv sync

# Playwright 브라우저 설치
uv run playwright install chromium
```

### 2. 애플리케이션 실행

```bash
# 개발 서버 시작 (자동 리로드)
uv run uvicorn src.main:app --reload
```

서버가 시작되면 브라우저에서 다음 주소로 접속하세요:
```
http://localhost:8000
```

## 📖 사용 방법

1. 서버를 시작하면 자동으로 GTI657 항공편 데이터를 가져옵니다
2. 지도에 파란색 폴리라인으로 전체 항공편 경로가 표시됩니다
3. 항공기 아이콘이 현재 위치를 표시합니다
4. 상단 정보 패널에서 항공편 상세 정보를 확인할 수 있습니다
5. 데이터는 30초마다 자동으로 업데이트됩니다

## 🔧 작동 원리

애플리케이션은 FlightAware의 `trackpollBootstrap` JavaScript 변수를 스크래핑하여 다음 정보를 추출합니다:

- **완전한 항공편 경로 좌표**: 시카고에서 서울까지의 전체 경로
- **현재 위치**: 트랙 데이터의 마지막 포인트
- **출발지/목적지 공항**: IATA/ICAO 코드
- **항공기 종류 및 항공편 상태**: 항공기 모델 및 현재 상태

데이터는 Leaflet.js 지도에 다음과 같이 표시됩니다:
- **파란색 폴리라인**: 시카고에서 서울까지의 전체 항공편 경로
- **항공기 마커**: 태평양 상공의 현재 위치
- **정보 패널**: 항공편 상세 정보 및 실시간 좌표

## 📡 API 엔드포인트

### `GET /api/flight-data`

항공편 정보와 경로 데이터를 JSON 형식으로 반환합니다.

**응답 예시:**
```json
{
  "flight_id": "GTI657",
  "origin": "ORD",
  "destination": "ICN",
  "aircraft_type": "B744",
  "current_position": {
    "longitude": -150.123,
    "latitude": 45.678,
    "altitude_feet": 35000,
    "altitude_meters": 10668
  },
  "route": [[lon1, lat1], [lon2, lat2], ...],
  "raw_track_data": [...]
}
```

## 🧪 테스트

테스트 스위트 실행:

```bash
# 모든 테스트 실행
uv run pytest tests/

# 특정 테스트 파일 실행
uv run pytest tests/test_scraper.py
uv run pytest tests/test_main.py
```

## 📁 프로젝트 구조

```
striker/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 서버 및 라우팅
│   └── scraper.py           # FlightAware 웹 스크래퍼
├── static/
│   └── index.html           # 프론트엔드 지도 인터페이스
├── tests/
│   ├── __init__.py
│   ├── test_main.py         # API 엔드포인트 테스트
│   └── test_scraper.py      # 스크래퍼 통합 테스트
├── pyproject.toml           # 프로젝트 의존성 및 설정
├── uv.lock                  # 의존성 잠금 파일
└── README.md                # 프로젝트 문서
```

## 🔍 주요 컴포넌트 설명

### `src/main.py`
- FastAPI 애플리케이션 진입점
- 정적 파일 서빙 및 API 라우트 정의
- `/api/flight-data` 엔드포인트 제공

### `src/scraper.py`
- FlightAware 웹사이트 스크래핑 로직
- Playwright를 사용한 브라우저 자동화
- JavaScript 변수에서 항공편 데이터 추출 및 파싱

### `static/index.html`
- Leaflet.js 기반 인터랙티브 지도
- 항공편 경로 및 현재 위치 시각화
- 30초 간격 자동 데이터 갱신

## 🚧 향후 개선 사항

- [ ] 여러 항공편 동시 추적 지원
- [ ] 항공편 이력 데이터 저장 및 분석
- [ ] 웹소켓을 통한 실시간 업데이트
- [ ] 사용자 인터페이스 개선
- [ ] 데이터 캐싱으로 성능 최적화

## 📝 라이선스

MIT
