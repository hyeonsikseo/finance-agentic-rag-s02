.PHONY: help setup download profile notebook chunk chunk-sample test
PY := .venv/bin/python

help:
	@echo "make setup      파이썬 3.12 와 패키지 설치 (2~3분)"
	@echo "make download   문서 내려받기 (약 5분. 1회차 폴더에서 복사했으면 몇 초)"
	@echo "make notebook   파서 비교 노트북 열기 (수업 1~3부)"
	@echo "make test       채운 함수 확인 (채우기 전에는 실패가 정상)"
	@echo "make chunk-sample  문서 6건만 돌려 본다 (7초. 수업 중 확인용)"
	@echo "make chunk      문서 51건 전부 → data/chunks/chunks.jsonl (4~5분. 과제)"
	@echo "make check-s02  2회차 확인 → results/check_s02.json (이 파일을 제출)"
	@echo "make profile    문서 실태 다시 재기 (선택)"

setup:
	uv venv --python 3.12 .venv
	uv pip install --python $(PY) -r requirements.txt

download:
	$(PY) data/download_corpus.py

profile:
	$(PY) scripts/profile_docs.py

notebook:
	$(PY) -m jupyter lab notebooks/s02_parsers.ipynb

chunk-sample:
	$(PY) pipelines/chunk_only.py --verbose --only hana_credit_terms_2009 --only fss_deposit_terms_2024_pdf --only knia_3500_scan --only kakao_deposit_terms_2024 --only hanacard_std_2017 --only law_silson_std_hwp

chunk:
	$(PY) pipelines/chunk_only.py --verbose

test:
	$(PY) -m pytest -q

check-s%:
	$(PY) scripts/check_session.py $*
