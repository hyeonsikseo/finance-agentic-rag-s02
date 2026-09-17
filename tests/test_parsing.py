# -*- coding: utf-8 -*-
"""2회차 자기 확인.

    make test        (Windows: .venv\\Scripts\\python -m pytest -q)

세 묶음입니다. 앞의 둘은 코퍼스 없이 돌고, 마지막은 문서와 청크가 있어야 돕니다(없으면 건너뜁니다).
채우기 전에는 앞의 두 묶음이 NotImplementedError 로 실패합니다. 그게 정상입니다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


# ── metadata.normalize_article ─────────────────────────────────────────
@pytest.mark.parametrize("raw, want", [
    ("제31조", "제31조"),
    ("제 31 조", "제31조"),
    ("제31 조(정의)", "제31조"),
    ("제4조의2", "제4조의2"),
    ("제 15 조의 2", "제15조의2"),
    ("제007조", "제7조"),
])
def test_normalize_article(raw, want):
    from finrag.parsing.metadata import normalize_article
    assert normalize_article(raw) == want


def test_normalize_article_returns_none_without_article():
    from finrag.parsing.metadata import normalize_article
    assert normalize_article("가입금액 1백만원 이상") is None


# ── validate.judge_page ────────────────────────────────────────────────
def _m(**kw) -> dict:
    """정상 페이지의 지표. 키워드로 하나씩 나쁘게 만든다."""
    base = {"chars": 800, "hangul_ratio": 0.68, "broken_ratio": 0.0,
            "space_ratio": 0.18, "single_char_token_ratio": 0.10}
    base.update(kw)
    return base


def test_blank_page_with_image_goes_to_ocr():
    from finrag.parsing.validate import judge_page
    verdict, _ = judge_page(_m(chars=7), has_image=True)
    assert verdict == "ocr", "텍스트가 없고 이미지가 있으면 스캔본이다"


def test_blank_page_without_image_passes():
    from finrag.parsing.validate import judge_page
    verdict, _ = judge_page(_m(chars=0), has_image=False)
    assert verdict == "pass", "텍스트도 이미지도 없으면 그냥 빈 페이지다"


def test_normal_page_passes_without_reasons():
    from finrag.parsing.validate import judge_page
    verdict, reasons = judge_page(_m(), has_image=False)
    assert verdict == "pass" and not reasons


def test_broken_font_goes_to_reparse():
    # 하나은행 2009 를 pdfplumber 로 뽑으면 이렇게 나온다: 한글 0, 깨진 문자 0.099
    from finrag.parsing.validate import judge_page
    verdict, reasons = judge_page(_m(hangul_ratio=0.0, broken_ratio=0.099), has_image=False)
    assert verdict == "reparse"
    assert reasons, "왜 걸렸는지 이유를 남겨야 로그만 보고 알 수 있다"


def test_lost_spaces_go_to_reparse_unless_page_was_swapped_for_tables():
    from finrag.parsing.validate import judge_page
    assert judge_page(_m(space_ratio=0.005), has_image=False)[0] == "reparse"
    # 표 때문에 일부러 PyMuPDF 로 바꿔 끼운 페이지는 공백 검사에서 빼 준다
    assert judge_page(_m(space_ratio=0.005), has_image=False, skip_space=True)[0] == "pass"


def test_letter_spacing_goes_to_reparse():
    from finrag.parsing.validate import judge_page
    assert judge_page(_m(single_char_token_ratio=0.9), has_image=False)[0] == "reparse"


# ── chunk.split_articles ───────────────────────────────────────────────
PAGES = [
    "여신거래기본약관\n"
    "제1조(적용범위) 이 약관은 은행과 채무자 사이의 여신거래에 적용된다.\n"
    "제2조(정의) 이 약관에서 쓰는 말의 뜻은 다음과 같다.\n",
    "1. 여신이란 대출을 말한다.\n"
    "제 3 조 (이자) 이자는 약정한 이율에 따른다.\n"
    "- 2 -\n",
]


def test_split_articles_opens_a_block_at_each_article_head():
    from finrag.parsing.chunk import split_articles
    arts = [b["article"] for b in split_articles(PAGES)]
    assert arts == ["", "제1조", "제2조", "제3조"], arts


def test_split_articles_records_pages_and_titles():
    from finrag.parsing.chunk import split_articles
    blocks = {b["article"]: b for b in split_articles(PAGES)}
    assert blocks["제2조"]["page_start"] == 1 and blocks["제2조"]["page_end"] == 2
    assert blocks["제3조"]["page_start"] == 2
    assert blocks["제1조"]["title"] == "적용범위"


def test_split_articles_drops_page_number_marks():
    from finrag.parsing.chunk import split_articles
    lines = [l for b in split_articles(PAGES) for l in b["lines"]]
    assert not any("- 2 -" in l for l in lines)
    assert not any(not l.strip() for l in lines), "빈 줄은 블록에 넣지 않는다"


def test_document_without_articles_is_one_block():
    from finrag.parsing.chunk import split_articles
    blocks = split_articles(["첫 줄\n둘째 줄", "셋째 줄"])
    assert len(blocks) == 1
    assert blocks[0]["article"] == "" and blocks[0]["page_start"] == 1 and blocks[0]["page_end"] == 2


# ── 코퍼스가 있어야 도는 것 ──────────────────────────────────────────
def _raw(name: str) -> Path:
    p = ROOT / "data" / "raw" / name
    if not p.exists():
        pytest.skip(f"코퍼스 없음: {name} (make download)")
    return p


def test_router_prefers_the_parser_that_reads_korean():
    from finrag.parsing.extract import extract
    e = extract(_raw("hana_credit_terms_2009.pdf"), "hana_credit_terms_2009")
    assert e.parser == "pymupdf", "pdfplumber 로 한글 0자가 나오는 문서는 다른 파서로 가야 한다"
    assert sum(len(x) for x in e.pages) > 1000


def test_gate_routes_scan_to_ocr():
    from finrag.parsing.extract import extract, page_objects
    from finrag.parsing.validate import validate
    p = _raw("knia_3500_scan.pdf")
    rep = validate(extract(p, "knia_3500_scan"), page_objects(p))
    assert rep.verdict == "ocr", "이미지 전용 문서는 OCR 로 가야 한다"


# ── make chunk 뒤에 도는 것 ──────────────────────────────────────────
def _chunks() -> list[dict]:
    path = ROOT / "data" / "chunks" / "chunks.jsonl"
    if not path.exists():
        pytest.skip("청크 없음 (make chunk)")
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def test_chunk_ids_are_unique_and_well_formed():
    ids = [c["chunk_id"] for c in _chunks()]
    assert len(ids) == len(set(ids)), "같은 ID 가 두 번 나왔다"
    assert all(i.count("#") == 2 for i in ids), "형식은 {doc_id}#{조항}#{seq} 다"


def test_short_articles_survive_chunking():
    """짧다고 조항을 버리면 '가입금액은 얼마' 같은 질문의 답이 사라진다."""
    arts = {c["chunk_id"] for c in _chunks() if c["doc_id"] == "kakao_deposit_terms_2024"}
    assert any("#제4조#" in a for a in arts), "제4조(가입금액)가 사라졌다"
