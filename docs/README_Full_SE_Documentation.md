# Full SE Documentation 업로드 및 반영 안내

## 1. 파일 배치

Word 문서는 다음 경로에 두었습니다.

- **경로**: `docs/Aegis-x_v3_Full_SE_Documentation.docx`
- **추출본**: `docs/Full_SE_Extracted.md` (python-docx로 추출)
- **분할 결과**: `docs/00_System_Charter.md` ~ `52_Portfolio_State_Engine_Spec.md` 등 42개 파일

## 2. 반영 절차 (이미 수행됨)

1. **추출**: `python scripts/extract_docx_to_md.py` → `docs/Full_SE_Extracted.md` 생성  
2. **분할**: `python scripts/split_full_se_extracted.py` → `docs/` 에 00_~52_ 등 개별 문서 생성  
3. **실라인**: [System_Realignment_Checklist.md](./System_Realignment_Checklist.md) 로 DB·엔진·게이트·실행·API 점검

docx를 수정 후 재반영할 때는 위 1→2 순서로 다시 실행하면 된다.

## 3. 문서 세트 구성

- **SE_Master_Index.md**: 전체 인덱스 및 Full SE 문서 세트(00_~52_) 목록.
- **Full SE (00_~52_)**: Charter, SRS, SAD, DDD, Regime/Allocation/Fleet/Twin/Meta/SelfHealing/Governance/Scaling, TVP, Risk, Config, Security, Warroom, CIC, DB Schema, API, 실행/포트폴리오 스펙 등.
- **기존 SE_01~SE_64, SE-65**: 비전·모듈 스펙·디렉터리 락.
- **SE_Documentation_Integration_Process.md**, **System_Realignment_Checklist.md**: 반영 절차 및 실라인 체크리스트.
