"""
Full_SE_Extracted.md 를 '📘 파일명' 구간별로 분할하여 docs/ 에 개별 파일로 저장.
출처: Aegis-x_v3_Full_SE_Documentation.docx → extract_docx_to_md.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "Full_SE_Extracted.md"
DOCS = ROOT / "docs"


def main() -> None:
    if not SRC.exists():
        print(f"Not found: {SRC}")
        return
    text = SRC.read_text(encoding="utf-8")
    # 구간 분할: '📘 ' 로 시작하는 줄을 문서 경계로 사용
    pattern = re.compile(r"\n(?=📘\s+\S+)", re.MULTILINE)
    parts = pattern.split(text)
    created = 0
    for i, block in enumerate(parts):
        block = block.strip()
        if not block or not block.startswith("📘"):
            if i == 0 and block:
                # 맨 앞 개요 부분은 그대로 두고, 첫 번째 📘 전까지는 건너뜀
                continue
            continue
        # 첫 줄에서 파일명 추출 (📘 00_System_Charter.md → 00_System_Charter.md)
        first_line = block.split("\n")[0].strip()
        if first_line.startswith("📘"):
            first_line = first_line[1:].strip()
        fname = first_line.split()[0] if first_line else f"doc_{i:02d}.md"
        if not fname.endswith(".md") and not fname.endswith(".sql"):
            fname = fname + ".md"
        # 본문: 첫 줄(제목) 포함 전체를 저장 (📘 제거하고 # 헤더로)
        body_lines = block.split("\n")
        if body_lines[0].strip().startswith("📘"):
            body_lines[0] = "# " + body_lines[0].replace("📘", "").strip()
        out_path = DOCS / fname
        out_path.write_text("\n".join(body_lines), encoding="utf-8")
        created += 1
        print(f"  {fname}")
    print(f"Created {created} files in {DOCS}")


if __name__ == "__main__":
    main()
