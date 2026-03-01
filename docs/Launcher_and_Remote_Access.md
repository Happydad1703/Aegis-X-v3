# 런처 및 원격 접속 (Desktop / Taskbar / Mobile / Push)

## 1. 바탕화면·툴바 바로가기

### 단일 디스플레이
- **런처 실행:** 브라우저에서 `http://localhost:8000/launcher/` 접속.
- 화면이 **세로로 2분할**됩니다.
  - **상단:** Warroom
  - **하단:** Dashboard & Control Panel
- **화면 맨 아래:** WSL Terminal 링크  
  → `run_wsl_terminal.bat` 다운로드 후 실행하거나, 프로젝트 루트에서 `scripts\run_wsl_terminal.bat` 실행.

### 복수 디스플레이
- 런처에서 **「복수 디스플레이 (창 분리)」** 클릭.
- **Warroom 열기**, **Dashboard & Control 열기** 버튼으로 각각 새 창을 띄운 뒤, 원하는 모니터로 드래그.

### 바탕화면·툴바 등록
1. **바로가기 생성:** `scripts\Create_Desktop_Shortcut.bat` 실행 → 바탕화면에 `Aegis-X v3 Warroom.bat` 생성.
2. **툴바 등록:** 생성된 `Aegis-X v3 Warroom.bat` 우클릭 → **작업 표시줄에 고정**.
3. **실행 전:** Backend가 떠 있어야 합니다. (`scripts\run_api.ps1` 또는 `uvicorn backend.main:app --host 0.0.0.0 --port 8000`)

---

## 2. Mobile 원격 접속 (S24 Ultra 등 Android)

- Warroom/Dashboard는 **반응형**이며, **S24 Ultra(Android)** 접속에 맞춰 터치·레이아웃을 조정했습니다.
- **같은 Wi‑Fi:** PC IP를 확인한 뒤 휴대폰 브라우저에서 `http://<PC-IP>:8000/warroom/` 접속.
- **다른 네트워크:** PC에서 터널 서비스(ngrok, cloudflared 등)로 8000 포트 노출 후, 발급 URL로 접속.

예시 (ngrok):
```bash
ngrok http 8000
```
→ 표시되는 HTTPS URL을 S24 브라우저에 입력.

- **API 기동 시:** `--host 0.0.0.0`으로 기동해야 같은 LAN 내 다른 기기에서 접속 가능합니다.  
  예: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`

---

## 3. Push 알림 (Telegram / Kakao Talk)

### 이벤트 종류
| 이벤트 | 설명 | Push 발송 시점 |
|--------|------|----------------|
| **market_open** | 시장 개시 | (스케줄러 연동 시 구현) |
| **market_close** | 시장 종료 | (스케줄러 연동 시 구현) |
| **target_selected** | Target 선정 | (후보군 선정 모듈 연동 시 구현) |
| **trade_filled** | 매매 성립 | Paper/KIS 주문 체결 시 (order_repo 기록 후) |
| **aar_done** | AAR 완료 | (AAR 엔진 연동 시 구현) |
| **freeze** | Freeze 발동 | Warroom에서 Freeze 버튼 클릭 시 |
| **retract** | Retract 발동 | Warroom에서 Retract 버튼 클릭 시 |
| **emergency_stop** | 비상 정지 | Warroom에서 Emergency Stop 클릭 시 |

### Telegram 설정
1. Bot 생성: [@BotFather](https://t.me/BotFather)에서 봇 생성 후 **토큰** 확보.
2. Chat ID 확보: 봇과 대화 한 번 한 뒤, `https://api.telegram.org/bot<TOKEN>/getUpdates`에서 `chat.id` 확인.
3. **Windows 11 환경변수** 설정:
   - `TELEGRAM_BOT_TOKEN` = 봇 토큰
   - `TELEGRAM_CHAT_ID` = 채팅 ID (숫자)

설정 후 Freeze/Retract/Emergency Stop 및 매매 체결 시 Telegram으로 푸시가 전송됩니다.

### Kakao Talk
- Kakao 알림은 **스텁** 상태입니다. 연동 시 `backend/app/core/notifications.py`의 `send_kakao()` 구현 및 `ENV_KAKAO_REST_KEY` 등 환경변수 사용.

---

## 4. 요약

| 항목 | 방법 |
|------|------|
| **단일 디스플레이** | 런처 → 상단 Warroom, 하단 Dashboard & Control, 하단 WSL 링크 |
| **복수 디스플레이** | 런처 → Warroom/Dashboard 각각 새 창 → 원하는 모니터로 이동 |
| **바탕화면/툴바** | `Create_Desktop_Shortcut.bat` → 생성된 bat 실행 또는 작업 표시줄에 고정 |
| **Mobile (S24)** | 같은 Wi‑Fi: `http://<PC-IP>:8000/warroom/` / 원격: 터널 URL |
| **Push** | Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 설정 → freeze/retract/emergency_stop/trade_filled 시 자동 발송 |
