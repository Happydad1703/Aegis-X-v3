# Windows 11 환경변수 — API Key 설정 가이드

**원칙**: 모든 API Key는 **Windows 11 시스템/사용자 환경변수**에만 설정한다.  
코드·.env 파일에 키를 하드코딩하지 않는다.  
앱은 `backend/app/core/env_keys.py`를 통해 **환경변수에서만** 키를 획득하여 외부 기관(뉴스/정보원, LLM, KIS)과 통신한다.

---

## 1. 환경변수 설정 방법 (Windows 11)

1. **시스템 속성** → **고급** → **환경 변수**
2. **사용자 변수** 또는 **시스템 변수**에서 **새로 만들기** → 변수 이름 / 변수 값 입력
3. 또는 PowerShell (현재 세션만):

   ```powershell
   $env:FRED_API_KEY = "your-fred-key"
   $env:OPENAI_API_KEY = "sk-..."
   ```

4. **영구 반영**: [시스템 속성] → [환경 변수]에서 추가한 뒤, **새로 연 터미널/IDE**에서 적용된다.

---

## 2. 외부 기관별 환경변수 목록

### 2.1 DB (로컬 개발 시 .env도 사용 가능)

| 변수명 | 용도 |
|--------|------|
| `DATABASE_URL` | 동기 DB 연결 (psycopg2). 예: `postgresql+psycopg2://postgres:2041@localhost:5433/aegisx` |
| `ASYNC_DATABASE_URL` | 비동기(API) 연결 (asyncpg). 없으면 DATABASE_URL에서 유도 |

### 2.2 뉴스/정보원·매크로

| 변수명 | 용도 | 비고 |
|--------|------|------|
| `FRED_API_KEY` | FRED (미국 매크로) | check_comm.py 통신 확인 대상 |
| `ECOS_API_KEY` | ECOS (한국 선행지표 등) | |
| `DART_API_KEY` | 전자공시 (DART) | |
| `NAVER_CLIENT_ID` | 네이버 API (뉴스/검색) | |
| `NAVER_CLIENT_SECRET` | 네이버 API Secret | |
| `FINNHUB_API_KEY` | Finnhub (뉴스/시세) | |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage | |

### 2.3 LLM

| 변수명 | 용도 | 비고 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI (GPT) | check_comm.py 통신 확인 대상 |
| `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY` | Google Gemini | check_comm.py 통신 확인 대상 |
| `ANTHROPIC_API_KEY` | Claude | |
| `DEEPSEEK_API_KEY` | DeepSeek | |

### 2.4 브로커 (KIS)

| 변수명 | 용도 | 비고 |
|--------|------|------|
| `KIS_APP_KEY` | 한국투자증권 앱 키 | check_comm.py 통신 확인 대상 |
| `KIS_APP_SECRET` | 한국투자증권 앱 시크릿 | |

### 2.5 Push 알림 (Telegram / Kakao)

| 변수명 | 용도 | 비고 |
|--------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram 봇 토큰 (BotFather 발급) | Freeze/Retract/E-Stop/매매체결 등 푸시 |
| `TELEGRAM_CHAT_ID` | 수신 채팅 ID (숫자) | 봇과 1:1 대화 후 getUpdates로 확인 |
| `KAKAO_REST_KEY` | Kakao 알림용 (선택) | 현재 스텁, 연동 시 사용 |

---

## 3. 통신 확인 (개발 착수 전)

키를 환경변수에 설정한 뒤, 아래 스크립트로 **API Key를 환경변수에서 읽어** 외부 기관과의 통신만 검증한다.

```powershell
cd D:\AEGIS-X_v3
python scripts/check_comm.py
```

- **OK**: 해당 키로 API 호출 성공  
- **SKIP (xxx not set)**: 해당 환경변수 미설정 (선택 항목이면 무시 가능)  
- **FAIL**: 키 오류 또는 네트워크/API 오류 → 변수값·네트워크 확인  

---

## 4. 참조

- **키 조회 모듈**: `backend/app/core/env_keys.py` — 모든 키는 여기서 `os.environ`으로만 조회
- **통신 확인**: `scripts/check_comm.py` — FRED, OpenAI, Gemini, KIS 순으로 확인
- **SE**: 03_External_Interface_Control_Document_ICD, 16_Config_Management_Plan, 17_Security_Model
