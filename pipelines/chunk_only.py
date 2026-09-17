#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""파싱 → 검증 게이트 → 청킹 (2회차).

그래프 없이 한 줄로 흐른다. LangGraph 는 3회차에 붙인다. 여기서는 파서가 무엇을
고르고 게이트가 무엇을 걸러내는지만 본다.

    python pipelines/chunk_only.py
    python pipelines/chunk_only.py --only nh_jangbyeong_2026 --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from finrag.parsing.chunk import chunk_document          # noqa: E402
from finrag.parsing.extract import extract, page_objects  # noqa: E402
from finrag.parsing.metadata import load_documents       # noqa: E402
from finrag.parsing.ocr import load_ocr                  # noqa: E402
from finrag.parsing.validate import validate             # noqa: E402
from finrag.settings import get_settings                 # noqa: E402


def read_text_like(path: Path, fmt: str) -> list[str]:
    raw = path.read_bytes().decode("utf-8", "replace")
    if fmt == "html":
        import html as h
        import re
        raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
        raw = re.sub(r"<br\s*/?>|</p>|</div>|</tr>|</li>|</h\d>", "\n", raw, flags=re.I)
        raw = h.unescape(re.sub(r"<[^>]+>", " ", raw))
        raw = "\n".join(" ".join(l.split()) for l in raw.splitlines() if l.strip())
    elif fmt == "xml":
        import xml.etree.ElementTree as ET
        raw = "\n".join(t.strip() for t in ET.fromstring(raw).itertext() if t.strip())
    return [raw]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    s = get_settings()
    docs = load_documents()
    targets = [d for d in docs.values() if not args.only or d.doc_id in set(args.only)]

    s.chunks_dir.mkdir(parents=True, exist_ok=True)
    all_chunks: list[dict] = []
    verdicts, parsers, skipped = Counter(), Counter(), []

    for meta in targets:
        path = ROOT / meta.path
        if not path.exists():
            continue
        head = path.open("rb").read(8)
        if head.startswith((b"PK\x03\x04", b"\xd0\xcf\x11\xe0")):
            # HWP/HWPX 는 지원하지 않는다. 이것이 "사람 검토 큐"의 실물이다.
            skipped.append((meta.doc_id, "지원하지 않는 형식"))
            verdicts["unsupported"] += 1
            continue

        if head.startswith(b"%PDF-"):
            ex = extract(path, meta.doc_id)
            rep = validate(ex, page_objects(path))
            pages, parser, verdict = ex.pages, ex.parser, rep.verdict
        else:
            pages = read_text_like(path, meta.format)
            parser, verdict = meta.format or "plain", "pass"

        ocr_pages, warns = ({}, [])
        if verdict == "ocr" or (head.startswith(b"%PDF-") and rep.bad_pages):
            ocr_pages, warns = load_ocr(meta.doc_id, path)
            ocr_pages = {k: v for k, v in ocr_pages.items() if v.strip()}

        chunks = chunk_document(pages, meta, ocr_pages=ocr_pages)
        for c in chunks:
            d = c.to_dict()
            d["meta"]["parser"] = parser
            d["meta"]["validation"] = verdict
            all_chunks.append(d)

        verdicts[verdict] += 1
        parsers[parser] += 1
        if args.verbose:
            print(f"{meta.doc_id:32} {verdict:8} {parser:11} 청크 {len(chunks):>4}"
                  + (f"  OCR {len(ocr_pages)}쪽" if ocr_pages else ""))

    out = s.chunks_dir / "chunks.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"\n문서 {len(targets)}건 → 청크 {len(all_chunks):,}개")
    print("  게이트:", ", ".join(f"{k} {v}" for k, v in sorted(verdicts.items())))
    print("  파서:", ", ".join(f"{k} {v}" for k, v in sorted(parsers.items())))
    if skipped:
        print(f"  사람 검토 큐 {len(skipped)}건: {', '.join(d for d, _ in skipped)}")
    print(f"\n→ {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
