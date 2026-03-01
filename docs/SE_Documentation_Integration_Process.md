# SE Documentation Integration Process

**목적**: Aegis-x v3 SE 문서 세트를 정확히 반영하고 전체 시스템을 실라인하는 절차를 정의한다.

**권장 참조 소스(Realign 기준)**: `D:\AEGIS-X_v3\docx_md` — docs의 SE 문서는 **docx_md** 내 문서를 참조하여 Realign한다. docx_md 수정 시 docx_md → docs 복사로 동기화 후 [System_Realignment_Checklist.md](./System_Realignment_Checklist.md) 실행.

**기타**: `Aegis-x_v3_Full_SE_Documentation.docx` (Word) 추출·분할 시에는 본 문서의 Full SE 절차를 사용할 수 있다.  
**SE 문서 세트**: `docs/` 내 00_~65_ (docx_md 동기본), SE_01~SE_64 (기존 모듈 스펙)

---

## 1. Full SE Documentation 수신 절차

| 단계 | 작업 | 담당/도구 |
|------|------|-----------|
| 1.1 | Word 문서를 프로젝트에 배치 | `docs/Aegis-x_v3_Full_SE_Documentation.docx` |
| 1.2 | 본 문서(통합 절차)에 따라 섹션별로 대응되는 SE_xx.md 매핑 확인 | 아래 매핑표 참조 |
| 1.3 | Docx 내용 추출 (선택: `python scripts/extract_docx_to_md.py` → `docs/Full_SE_Extracted.md`) | `pip install python-docx` 후 스크립트 또는 수동 복사 |
| 1.4 | 기존 `docs/SE_xx.md` 내용과 비교·병합 (덮어쓰기 시 버전 및 변경 이력 기록) | 수동/스크립트 |
| 1.5 | 반영 후 시스템 실라인 체크리스트 실행 | `docs/System_Realignment_Checklist.md` |

---

## 2. Full SE Documentation → 기존 SE 문서 매핑

Full SE 문서의 **구성 과정** 및 **섹션 구조**가 아래와 일치하거나 확장될 수 있도록 반영한다.

| Full SE Doc 섹션 (예상) | 대응 docs 파일 | 비고 |
|-------------------------|----------------|------|
| 시스템 비전·철학 | `SE_01_System_Vision_and_Philosophy.md` | DB-First, Follow-the-Sun 등 |
| 부대 구조(Force Organization) | `SE_02_Force_Organization_Structure.md` | |
| 레짐 분류 | `SE_03_Regime_Classification_Model.md` | |
| 자본 배분 프레임워크 | `SE_04_Capital_Allocation_Framework.md` | |
| 자본 스케일링 전략 | `SE_05_Capital_Scaling_Strategy.md` | |
| Strike 전략 엔진 | `SE_06_Strike_Strategy_Engine.md` | |
| Swing 전략 엔진 | `SE_07_Swing_Strategy_Engine.md` | |
| Core 복합 전략 | `SE_08_Core_Compound_Strategy.md` | |
| Reserve 관리 모델 | `SE_09_Reserve_Management_Model.md` | |
| Follow-the-Sun 아키텍처 | `SE_10_Follow_the_Sun_Architecture.md` | |
| 모듈 11 ~ 63 스펙 | `SE_11` ~ `SE_63_Module_xx_Specification.md` | DB 스키마, 스냅샷 계약, 게이트, 감사 로그 |
| 모듈 통합 스펙 | `SE_64_Module_64_Specification.md` | |
| 디렉터리/아키텍처 락 | `SE-65_Final_Directory_Architecture_Lock_Spec.md` | 폴더 구조 동결 |

- Full SE 문서에 **새 번호(예: SE_66)** 또는 **하위 항목**이 있으면, 이 표를 갱신하고 필요 시 새 파일을 추가한 뒤 **SE_Master_Index.md**를 수정한다.

---

## 3. 반영 시 준수 사항

- **버전 표기**: 각 SE_xx.md 상단에 `Version: v3.0 (Design Freeze)` 및 반영 일자(UTC) 유지 또는 갱신.
- **구조 동결**: `/backend/app/` 하위 디렉터리 구조는 SE-65에 따라 변경하지 않는다.
- **용어 통일**: DB-First, Snapshot, Gate, Engine, Execution 등 용어는 Full SE 문서와 동일하게 유지.
- **제약 반영**: 모든 시간은 TIMESTAMPTZ(UTC), JSON은 JSONB, 엔진 결과물은 `core/snapshot_repo.py` 경유만 허용.

---

## 4. 반영 후 시스템 실라인

Full SE 문서 반영이 끝나면 **System_Realignment_Checklist.md**에 따라 다음을 점검한다.

1. **DB 스키마**: `db/migrations/` DDL이 SE 문서의 테이블·컬럼 규격과 일치하는지.
2. **엔진**: `engines/` 각 모듈이 해당 SE_xx 스펙의 입출력·스냅샷 계약을 따르는지.
3. **게이트**: `gates/` 통제 로직이 모드·파일럿·리스크 게이트 규격을 따르는지.
4. **실행**: `execution/`이 명령·스냅샷·DB만 참조하고 직접 DB 쓰기를 하지 않는지.
5. **Dashboard/UI**: 모든 UI 데이터가 DB Snapshot을 통해서만 읽는지.

실라인 체크리스트는 `docs/System_Realignment_Checklist.md`를 참조한다.

---

## 5. 문서 이력

| 일자 | 변경 내용 |
|------|-----------|
| (최초) | Full SE Documentation 반영 절차 및 매핑표 정의. 실라인 절차 연결. |
