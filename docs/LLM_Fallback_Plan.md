# LLM Fallback Plan — 통신 두절 시 시스템 실행 안정성 유지

**원칙**: 어떠한 경우에도 **특정 LLM/모델과의 통신 두절이 시스템 실행 안정성 하락으로 이어지지 않는다.**  
LLM은 "최종 판정 및 해설" 등 **보조 역할**에 한정하며, 핵심 계산(Regime/Allocation)은 수식 Locking으로 이미 보장.

---

## 1. Fallback 체인 (우선순위)

| 순위 | Provider | 환경변수 | 용도 | 실패 시 |
|------|----------|----------|------|----------|
| 1 | OpenAI | OPENAI_API_KEY | 1선 (JCS/해설 등) | 2선으로 자동 전환 |
| 2 | Anthropic (Claude) | ANTHROPIC_API_KEY | 2선 백업 | 3선으로 전환 |
| 3 | Google (Gemini) | GEMINI_API_KEY / GOOGLE_API_KEY | 3선 백업 | 4선으로 전환 |
| 4 | DeepSeek | DEEPSEEK_API_KEY | 4선 백업 | Blackout 처리 |
| — | **LKS / Structured Only** | (없음) | **전원 실패 시** | incident 기록, LKS 모드로 시스템 계속 운영 |

- **LKS (Last-Known Strategy)**: system_config에 저장된 마지막 유효 전략/해설. LLM 전원 불가 시 이 값으로 계속 동작.
- **Structured Only**: LLM 호출 없이 수식·규칙만으로 동작 (regime_engine, allocation_engine 이미 해당).

---

## 2. 적용 위치

| 모듈 | LLM 사용 여부 | Fallback 적용 |
|------|----------------|----------------|
| regime_engine | 사용 안 함 (수식 Locking) | 해당 없음 |
| allocation_engine | 사용 안 함 (수식 Locking) | 해당 없음 |
| llm_gateway | 사용 (해설/보조) | request_llm() 내 1→2→3→4 순차 시도, 전원 실패 시 on_blackout() + LKS 반환 |
| check_comm | 통신 점검만 | OpenAI, Gemini 등 점검 실패 시 SKIP. **시스템 실행과 무관** (안정성 하락 아님). |

---

## 3. Blackout 시 동작

1. **모든 Provider 요청 실패** 시:
   - `llm_gateway.on_blackout(db)` 호출 → incident_log에 `LLM_BLACKOUT` 기록.
   - `get_lks(db)`로 Last-Known Strategy 반환. 호출자는 LKS를 사용해 계속 진행.
2. **엔진 사이클**: Regime/Allocation은 LLM 미의존이므로 **엔진 1사이클은 Blackout과 무관하게 정상 수행**.
3. **Warroom/API**: 스냅샷은 DB만 읽으므로 **LLM 상태와 무관**하게 제공 가능.

---

## 4. 환경변수 및 점검

| 변수 | 용도 | check_comm |
|------|------|------------|
| OPENAI_API_KEY | 1선 LLM | ✅ OpenAI (LLM) |
| ANTHROPIC_API_KEY | 2선 LLM | (확장 시) |
| GEMINI_API_KEY / GOOGLE_API_KEY | 3선 LLM | ✅ Gemini (LLM) |
| DEEPSEEK_API_KEY | 4선 LLM | (확장 시) |

- 통신 점검 실패(FAIL)는 **시스템 기동/실행을 막지 않음**. SKIP 또는 FAIL 시에도 엔진·API는 동작.

---

## 5. 검증 체크리스트

- [ ] llm_gateway.request_llm()이 1→2→3→4 순차 시도 후 전원 실패 시 LKS + on_blackout 호출
- [ ] regime_engine / allocation_engine는 LLM 호출 없음 (수식만)
- [ ] check_comm 실패 시에도 Run_Stability_Check 4·5·6·7 항목(DB·엔진·스냅샷·계약테스트) 통과 가능

---

*문서 버전: v1.0 | LLM 통신 두절 ≠ 실행 안정성 하락*
