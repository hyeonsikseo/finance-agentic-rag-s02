#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""회차 확인.

    python scripts/check_session.py 2        →  results/check_s02.json

회차 끝에 이걸 돌려서 나온 JSON 을 커밋합니다. 그 파일이 제출물입니다.
강사는 그 파일들을 모아 표로 보고 빨간 칸만 확인합니다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def ok(cond: bool, detail: str = "") -> dict:
    return {"ok": bool(cond), "detail": detail}


CHUNK_ID = re.compile(r"^[^#]+#[^#]*#\d+$")
GATE_VERDICTS = {"pass", "reparse", "ocr"}


def check_s02() -> dict:
    from finrag.settings import get_settings
    s = get_settings()
    path = s.chunks_dir / "chunks.jsonl"
    chunks = [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()] if path.exists() else []
    sample = chunks[:500]

    required = {"chunk_id", "doc_id", "text", "article", "page_start"}
    missing_fields = [c.get("chunk_id", "?") for c in sample if not required <= set(c)]
    meta_required = {"doc_type", "issuer", "effective_from", "parser", "validation"}
    missing_meta = [c.get("chunk_id", "?") for c in sample
                    if not meta_required <= set(c.get("meta", {}))]
    bad_verdict = [c.get("chunk_id", "?") for c in sample
                   if c.get("meta", {}).get("validation") not in GATE_VERDICTS]

    ids = [c["chunk_id"] for c in chunks if "chunk_id" in c]
    dup = len(ids) - len(set(ids))
    bad_id = [i for i in ids if not CHUNK_ID.match(i)]

    # 1회차 질문에 근거 청크를 붙였는가. 붙였다면 그 ID 가 실제로 존재해야 한다.
    q = s.golden_dir / "student_q.jsonl"
    qs = []
    if q.exists():
        for line in q.open(encoding="utf-8"):
            if line.strip():
                try:
                    qs.append(json.loads(line))
                except json.JSONDecodeError:
                    qs.append({})
    id_set = set(ids)
    with_gold = [r for r in qs if r.get("gold_chunk_ids")]
    dangling = [g for r in with_gold for g in r["gold_chunk_ids"] if g not in id_set]

    return {
        "청크 생성": ok(len(chunks) >= 1000, f"{len(chunks):,}개"),
        "청크 필수 필드": ok(not missing_fields,
                      f"누락 {len(missing_fields)}건: {', '.join(missing_fields[:2])}"
                      if missing_fields else f"{sorted(required)}"),
        "메타데이터 부착": ok(not missing_meta,
                       f"누락 {len(missing_meta)}건: {', '.join(missing_meta[:2])}"
                       if missing_meta else f"{sorted(meta_required)}"),
        "게이트 판정 기록": ok(bool(sample) and not bad_verdict,
                        f"판정 없는 청크 {len(bad_verdict)}건" if bad_verdict else
                        # 분포는 표본이 아니라 전체로 센다. 앞 500개는 대개 한 문서에서
                        # 나와 "reparse 500" 처럼 한쪽으로 쏠려 보인다.
                        ", ".join(f"{k} {v:,}" for k, v in sorted(
                            Counter(c.get("meta", {}).get("validation") for c in chunks).items()
                            if chunks else []))),
        "청크 ID 유일·형식": ok(dup == 0 and not bad_id,
                          f"중복 {dup}건 · 형식 위반 {len(bad_id)}건"),
        "질문에 근거 청크": ok(len(with_gold) >= 3 and not dangling,
                        f"{len(with_gold)}/{len(qs)}문항에 gold_chunk_ids"
                        + (f" · 없는 ID {len(dangling)}건" if dangling else "")),
    }


CHECKS = {2: check_s02}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("session", type=int, choices=sorted(CHECKS))
    args = ap.parse_args()

    try:
        checks = CHECKS[args.session]()
    except Exception as e:
        checks = {"실행 실패": ok(False, f"{type(e).__name__}: {e}")}

    passed = sum(1 for v in checks.values() if v["ok"])
    print(f"\ncheck-s{args.session:02d}   {passed}/{len(checks)} 통과")
    for k, v in checks.items():
        print(f"  {'O' if v['ok'] else 'X'}  {k:28} {v['detail']}")

    out = ROOT / "results" / f"check_s{args.session:02d}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "session": args.session,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "passed": passed, "total": len(checks), "checks": checks},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {out.relative_to(ROOT)}  (이 파일을 커밋하세요)")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
