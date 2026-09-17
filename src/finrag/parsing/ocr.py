# -*- coding: utf-8 -*-
"""OCR 캐시 소비.

수업 중에는 OCR 을 돌리지 않는다. 강사(또는 0회차의 학생 본인)가 미리 만들어 둔
`data/ocr_cache/<doc_id>.json` 을 읽기만 한다. 캐시가 원본과 어긋나면 조용히 쓰지
않고 경고한다 — 낡은 OCR 결과로 인덱스를 만드는 것이 가장 찾기 어려운 오류다.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..settings import get_settings


def cache_path(doc_id: str) -> Path:
    return get_settings().data / "ocr_cache" / f"{doc_id}.json"


def load_ocr(doc_id: str, source: Path | None = None) -> tuple[dict[int, str], list[str]]:
    """(페이지번호 → 텍스트, 경고 목록)."""
    p = cache_path(doc_id)
    if not p.exists():
        return {}, [f"OCR 캐시 없음: {p.name}. data/ocr_cache/ 에 캐시를 넣으세요 (수강생은 디스코드의 ocr_cache.zip, 강사는 scripts/make_ocr_cache.py)."]

    data = json.loads(p.read_text(encoding="utf-8"))
    warnings: list[str] = []
    if source and source.exists() and data.get("source_sha256"):
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != data["source_sha256"]:
            warnings.append(f"OCR 캐시가 낡았습니다({doc_id}): 원본이 바뀌었습니다. --force 로 다시 만드세요.")
    pages = {int(k): v.get("text", "") for k, v in data.get("pages", {}).items()}
    if data.get("low_yield_pages"):
        warnings.append(f"OCR 결과가 빈약한 페이지: {data['low_yield_pages']}")
    return pages, warnings
