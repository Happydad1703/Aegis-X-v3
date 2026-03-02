# 외부 자료원 통신 상태 점검

**실행**: `python scripts/check_comm.py`  
**환경**: `.env` + Windows 환경변수 (env_keys.py 기준)

---

## 점검 대상 (ICD 기준)

### 매크로·공시·뉴스

| 자료원 | 용도 | 환경변수 | 비고 |
|--------|------|----------|------|
| FRED | 매크로 (미국) | FRED_API_KEY | St. Louis Fed API |
| ECOS | 매크로 (한국) | ECOS_API_KEY | 한국은행 통계 |
| DART | 전자공시 | DART_API_KEY | opendart.fss.or.kr |
| Naver | 뉴스/검색 | NAVER_CLIENT_ID, NAVER_CLIENT_SECRET | 검색 API |
| 연합뉴스 RSS | 뉴스 | (없음) | economy.xml 연결 확인 |
| 이데일리 RSS | 뉴스 | (없음) | idailynews.co.kr RSS |
| Finnhub | 뉴스/시세 | FINNHUB_API_KEY | 미국 시장 |
| Alpha Vantage | 시세/뉴스 | ALPHA_VANTAGE_API_KEY | 미국 시장 |

### LLM

| 자료원 | 용도 | 환경변수 | 비고 |
|--------|------|----------|------|
| OpenAI | LLM | OPENAI_API_KEY | Fallback 1순위 |
| Anthropic | LLM (Claude) | ANTHROPIC_API_KEY | Fallback 2순위 |
| Gemini | LLM | GEMINI_API_KEY / GOOGLE_API_KEY | Fallback 3순위 |
| DeepSeek | LLM | DEEPSEEK_API_KEY | Fallback 4순위 |

### 브로커

| 자료원 | 용도 | 환경변수 | 비고 |
|--------|------|----------|------|
| KIS | 브로커 (한국투자증권) | KIS_APP_KEY, KIS_APP_SECRET | 단일 실행 채널 |

---

## 최근 점검 결과 (예시)

```
FRED (macro):           OK
ECOS (macro):           OK
DART (공시):            OK / SKIP (키 미설정 시)
Naver (뉴스/검색):       OK
연합뉴스 RSS:           OK
이데일리 RSS:           OK
Finnhub (뉴스/시세):    OK (타임아웃 시 재시도 권장)
Alpha Vantage:          OK
OpenAI (LLM):           OK
Anthropic (LLM):        OK
Gemini (LLM):           OK
DeepSeek (LLM):         OK
KIS (broker):           OK
```

- **OK**: 해당 API/URL 연결 성공.
- **SKIP**: 환경변수 미설정으로 점검 생략 (RSS는 키 없이 연결만 확인).
- **FAIL**: 연결 실패·HTTP 오류·타임아웃 (키·네트워크·할당량 점검).

RSS(연합·이데일리)는 공개 URL만 HEAD/GET으로 확인. Gemini는 `GET /v1beta/models`로 키 검증.

---

## 재실행 방법

```powershell
cd D:\AEGIS-X_v3
python scripts/check_comm.py
```

종료 코드 0 = 모두 OK 또는 SKIP, 1 = 1개 이상 FAIL.
