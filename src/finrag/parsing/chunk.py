# -*- coding: utf-8 -*-
"""청킹.

약관은 조항이 의미 단위다. 고정 길이로 자르면 "제7조 제2항"의 답이 두 청크에 걸쳐
반으로 잘린다. 그래서 조항 경계로 먼저 자르고, 너무 긴 조항만 문단으로 나눈다.

청크 ID 는 `{doc_id}#{조항}#{seq}` 로 결정적이다. 같은 문서를 다시 인제스천해도
같은 ID 가 나와야 골든셋의 gold chunk 가 계속 유효하다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

from .metadata import ARTICLE_HEAD, DocMeta, normalize_article

MAX_CHARS = 1200      # arctic-embed-l-v2.0-ko 학습 max 1300 토큰을 넘지 않도록 잡은 상한
OVERLAP = 150
# 조항 블록은 짧아도 버리지 않는다. "제4조 가입금액: 1백만원 이상" 은 38자지만
# 가장 답하기 쉬운 조항이다. 길이로 거르면 이런 조항이 통째로 사라진다.
MIN_CHARS_ARTICLE = 12      # 조항 머리글이 있는 블록
MIN_CHARS_PLAIN = 40        # 조항이 없는 본문 조각(머리말·꼬리말 잡음 거르기용)

PAGE_MARK = re.compile(r"^\s*-\s*\d+\s*-\s*$")


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    article: str = ""
    article_title: str = ""
    seq: int = 0
    page_start: int = 0
    page_end: int = 0
    n_chars: int = 0
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def _clean(line: str) -> str:
    return "" if PAGE_MARK.match(line) else line


def split_articles(pages: list[str]) -> list[dict]:
    """조항 머리글을 만나면 새 구간을 연다. 조항이 없는 문서는 통째로 한 구간.

    블록 하나는 {"article", "title", "lines", "page_start", "page_end"} 다.
    첫 조항 머리글 앞의 본문은 article 이 "" 인 블록이 된다.
    """
    blocks: list[dict] = []
    cur = {"article": "", "title": "", "lines": [], "page_start": 1, "page_end": 1}
    for pno, page in enumerate(pages, start=1):
        for line in page.splitlines():
            line = _clean(line)          # 쪽 번호 표시("- 2 -")는 빈 줄이 된다
            if not line.strip():
                continue
            m = ARTICLE_HEAD.match(line)
            # ── TODO: 여기를 채우세요 ──────────────────────────────
            # m 이 있으면 조항 머리글이다. 지금까지 모은 cur 를 blocks 에 넣고(줄이 있을 때만)
            # 새 cur 를 연다 — article 은 normalize_article(m.group(0)) (None 이면 ""),
            # title 은 m.group(3) 의 양끝 공백을 지운 것, lines 는 [line], page_start 와 page_end 는 pno.
            # m 이 없으면 cur["lines"] 에 line 을 붙이고 cur["page_end"] 를 pno 로 갱신한다.
            # page_start / page_end 가 있어야 나중에 근거로 쪽수를 인용할 수 있다.
            raise NotImplementedError("TODO: split_articles 를 구현하세요")
    if cur["lines"]:
        blocks.append(cur)
    return blocks


def _split_long(text: str) -> list[str]:
    """긴 조항을 문단 경계로 나눈다. 겹침을 둬서 경계에 걸친 문장을 잃지 않는다."""
    if len(text) <= MAX_CHARS:
        return [text]
    parts, buf = [], ""
    for para in re.split(r"(?<=[.。］\)])\s*\n|\n{2,}", text):
        if not para:
            continue
        if len(buf) + len(para) + 1 > MAX_CHARS and buf:
            parts.append(buf.strip())
            buf = buf[-OVERLAP:] + "\n" + para
        else:
            buf = f"{buf}\n{para}" if buf else para
    if buf.strip():
        parts.append(buf.strip())
    # 문단 경계가 없는 표 페이지 등은 그래도 길다. 마지막 수단으로 잘라 낸다.
    out: list[str] = []
    for p in parts:
        while len(p) > MAX_CHARS:
            out.append(p[:MAX_CHARS])
            p = p[MAX_CHARS - OVERLAP:]
        out.append(p)
    return out


def chunk_document(pages: list[str], meta: DocMeta, *, ocr_pages: dict[int, str] | None = None) -> list[Chunk]:
    """조항 구조로 자른다. OCR 캐시가 있으면 그 페이지 본문을 끼워 넣는다."""
    ocr_pages = ocr_pages or {}
    merged = [ocr_pages.get(i, p) if len(p.strip()) < 30 else p for i, p in enumerate(pages, start=1)]

    chunks: list[Chunk] = []
    counter: dict[str, int] = {}
    for block in split_articles(merged):
        body = "\n".join(block["lines"]).strip()
        article = block["article"]
        floor = MIN_CHARS_ARTICLE if article else MIN_CHARS_PLAIN
        if len(body) < floor:
            continue
        for piece in _split_long(body):
            if len(piece.strip()) < floor:
                continue
            key = article or "본문"
            counter[key] = counter.get(key, 0) + 1
            seq = counter[key]
            chunks.append(Chunk(
                chunk_id=f"{meta.doc_id}#{key}#{seq}",
                doc_id=meta.doc_id, text=piece.strip(), article=article,
                article_title=block["title"], seq=seq,
                page_start=block["page_start"], page_end=block["page_end"],
                n_chars=len(piece.strip()), meta=meta.payload(),
            ))
    return chunks
