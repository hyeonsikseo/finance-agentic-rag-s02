# 약관부터 답변까지 — 2회차

금융 문서 특화 Agentic RAG 수업의 2회차 저장소입니다. 1회차 저장소(finance-agentic-rag-s01)와는 별개이고 새로 받습니다. 1회차 내용(설치, 문서 카탈로그, 문제지, 산출물 예시)은 그대로 들어 있고, 그 위에 2회차 코드가 얹혀 있습니다.

## 2회차에 할 일

1. 설치합니다. 1회차 폴더가 옆에 있으면 내려받은 문서를 복사해 오니 몇 분이면 끝납니다. → [docs/install.md](docs/install.md)
2. 수업 1~3부는 노트북으로 같은 PDF 가 파서에 따라 어떻게 다르게 나오는지 봅니다. → `make notebook`
3. 수업 4~5부는 함수 세 개를 채우고 문서 51건을 청크로 만듭니다. → [docs/session2/lab.md](docs/session2/lab.md)
4. 과제는 필수 둘(청크 파일, 질문 3개)에 선택 하나이고, `make check-s02` 가 6/6 이면 끝입니다. → [docs/session2/homework.md](docs/session2/homework.md)

## 폴더

| 폴더 | 무엇 |
|---|---|
| `docs/install.md` | 설치. 1회차와 같고, 문서 복사 단계가 추가됐습니다 |
| `docs/session2/` | 실습 순서(lab.md)와 과제(homework.md) |
| `docs/templates/` | 선택 과제에 쓰는 피드백 메모 템플릿. ADR 템플릿은 3회차부터 씁니다 |
| `docs/session1/` | 1회차 문서. 산출물 예시가 `examples/` 에 있습니다 |
| `notebooks/s02_parsers.ipynb` | 파서 3종 비교. 수업 1~3부 |
| `src/finrag/parsing/` | 파싱 → 검증 게이트 → 청킹. 채울 함수 세 개가 여기 있습니다 |
| `pipelines/chunk_only.py` | 문서 51건을 파싱 → 검사 → 청킹으로 돌려 `data/chunks/chunks.jsonl` 을 만듭니다 |
| `tests/test_parsing.py` | 채운 함수가 맞는지 보는 테스트 |
| `scripts/check_session.py` | 2회차 확인. 결과 파일이 제출물입니다 |
| `data/` | 문서 카탈로그와 골든셋. 원본 문서는 각자 내려받습니다 |

## 명령

```bash
make setup       # 파이썬 3.12 와 패키지 설치. 2~3분
make download    # 문서 내려받기. 1회차 폴더에서 복사했으면 몇 초
make notebook    # 파서 비교 노트북 열기
make test        # 자동 채점. 검사 21개. 채우기 전에는 실패가 정상입니다
make chunk-sample  # 문서 6건만 돌려 본다. 7초. 수업 중 확인용
make chunk       # 문서 51건 전부 → data/chunks/chunks.jsonl. 4~5분. 과제
make check-s02   # 결과물이 조건 6개를 만족하는지 확인 → results/check_s02.json
```

Windows 에서는 `make` 가 없으니 [docs/install.md](docs/install.md) 의 PowerShell 명령을 씁니다.

## 원본 문서가 저장소에 없는 이유

약관과 상품설명서는 각 금융회사의 저작물이라 다시 나눠 줄 수 없습니다. 저장소에는 "무엇을 어디서 받는지"만 있고, 각자 원 출처에서 받습니다. 자세한 것은 [data/README.md](data/README.md) 에 있습니다. 같은 이유로 문서 본문이 들어 있는 `data/chunks/` 도 저장소에 올리지 않습니다(`.gitignore` 에 있습니다).
