"""
Full SE Documentation(.docx) → Markdown 추출.
업로드된 docs/Aegis-x_v3_Full_SE_Documentation.docx 를 docs/Full_SE_Extracted.md 로 변환하여
SE_Documentation_Integration_Process 에 따른 반영 시 비교·병합에 사용.

사용: python scripts/extract_docx_to_md.py
의존성: pip install python-docx (선택)
"""
from __future__ import annotations

import sys
from pathlib import Path

# 프로젝트 루트
ROOT = Path(__file__).resolve().parent.parent
DOCX_PATH = ROOT / "docs" / "Aegis-x_v3_Full_SE_Documentation.docx"
OUT_PATH = ROOT / "docs" / "Full_SE_Extracted.md"


def main() -> None:
    if not DOCX_PATH.exists():
        print(f"파일 없음: {DOCX_PATH}")
        print("Aegis-x_v3_Full_SE_Documentation.docx 를 docs/ 에 배치한 뒤 다시 실행하세요.")
        sys.exit(1)
    try:
        from docx import Document
    except ImportError:
        print("python-docx 가 필요합니다: pip install python-docx")
        sys.exit(2)
    doc = Document(DOCX_PATH)
    lines: list[str] = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            lines.append("")
            continue
        style = p.style.name if p.style else ""
        if "Heading" in style or "Title" in style:
            level = 1
            if "Heading" in style:
                try:
                    level = int(style.replace("Heading ", "").strip() or "1")
                except ValueError:
                    pass
            lines.append("#" * min(level, 6) + " " + text)
        else:
            lines.append(text)
    out_text = "\n".join(lines)
    OUT_PATH.write_text(out_text, encoding="utf-8")
    print(f"추출 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
