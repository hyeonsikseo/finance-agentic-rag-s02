# 설치와 문서 내려받기

1회차와 거의 같습니다. 1회차 때 설치했으면 1번은 건너뛰고 2번부터 합니다. 1회차 폴더에 내려받은 문서가 있으면 그것을 복사해 오니 이번에는 5분짜리 내려받기가 없습니다.

## 1. 준비물 두 가지, git 과 uv

1회차에 했으면 건너뜁니다.

uv 는 파이썬 패키지 도구입니다. 파이썬 3.12 도 uv 가 받아 주니 파이썬을 따로 설치하지 않아도 됩니다.

**Mac**

```bash
xcode-select --install
curl -LsSf https://astral.sh/uv/install.sh | sh
```

첫 줄은 git 을 설치합니다. 이미 있으면 "already installed"라고 나오고, 그러면 넘어갑니다.

**Windows (PowerShell)**

```powershell
winget install --id Git.Git -e
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치가 끝나면 터미널을 닫고 새로 엽니다. 새로 열어야 방금 설치한 명령이 잡힙니다. 확인은 이렇게 합니다.

```bash
git --version
uv --version
```

## 2. 저장소 받기

과제를 GitHub 로 내므로 이번에는 **Fork** 를 먼저 합니다.

1. 브라우저에서 https://github.com/hyeonsikseo/finance-agentic-rag-s02 를 열고 오른쪽 위 **Fork** 를 누릅니다. 자기 계정에 같은 이름의 저장소가 생깁니다.
2. 그 저장소를 받습니다. `<계정>` 자리에 자기 GitHub 계정을 넣습니다.

```bash
git clone https://github.com/<계정>/finance-agentic-rag-s02.git
cd finance-agentic-rag-s02
```

3. 원본 주소를 `upstream` 이라는 이름으로 한 번 등록해 둡니다. 강사가 수업 뒤 올리는 것(정답 브랜치, 산출물 예시)을 받을 때 씁니다.

```bash
git remote add upstream https://github.com/hyeonsikseo/finance-agentic-rag-s02.git
```

GitHub 계정이 없거나 Fork 가 막히면 아래처럼 그대로 받습니다. 과제는 zip 으로 냅니다.

```bash
git clone https://github.com/hyeonsikseo/finance-agentic-rag-s02.git
cd finance-agentic-rag-s02
```

Windows 에서도 같습니다.

## 3. 1회차 문서 가져오기

1회차 폴더(`finance-agentic-rag-s01`)가 옆에 있으면 내려받은 문서를 복사합니다. 폴더가 다른 곳에 있으면 경로만 바꿉니다.

**Mac**

```bash
cp -R ../finance-agentic-rag-s01/data/raw data/
```

**Windows (PowerShell)**

```powershell
Copy-Item -Recurse ..\finance-agentic-rag-s01\data\raw data\
```

1회차 폴더가 없으면 건너뜁니다. 5번에서 새로 내려받습니다.

**OCR 캐시도 넣습니다.** 디스코드에 올라온 `ocr_cache.zip` 을 받아 저장소의 `data` 폴더 **안에** 풉니다. 저장소 폴더에서 이렇게 합니다.

**Mac**

```bash
unzip -o ~/Downloads/ocr_cache.zip -d data
ls data/ocr_cache
```

**Windows (PowerShell)**

```powershell
Expand-Archive -Force $HOME\Downloads\ocr_cache.zip -DestinationPath data
dir data\ocr_cache
```

`data/ocr_cache/` 에 json 파일 3개가 보이면 됩니다. Finder 에서 더블클릭으로 풀었다면 다운로드 폴더에 `ocr_cache` 폴더가 생기니, 그 폴더째 저장소의 `data` 폴더로 옮깁니다. `data/ocr_cache/ocr_cache/` 처럼 두 겹이 되면 못 읽습니다.

스캔본 문서를 강사가 미리 OCR 한 결과인데, 문서 본문이 들어 있어 저장소에는 넣을 수 없어서 따로 나눕니다. 없어도 수업은 됩니다. 다만 노트북의 OCR 셀이 "캐시가 없습니다"라고 나오고, 스캔본 1건(`knia_3500_scan`)의 청크가 안 나옵니다.

## 4. 파이썬과 패키지 설치

**Mac**

```bash
make setup
```

**Windows (PowerShell)**

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

2~3분 걸립니다. 이번에는 노트북(jupyterlab)이 들어 있어 1회차보다 조금 더 걸립니다. 파이썬 3.12 가 없으면 uv 가 받아 옵니다.

## 5. 문서 내려받기

**Mac**

```bash
make download
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\python data\download_corpus.py
```

3번에서 복사했으면 이미 있는 파일은 건너뛰므로 몇 초면 끝납니다. 복사하지 않았으면 약 5분 걸립니다. 금융감독원, 법제처, 각 금융회사 사이트에서 공개 문서를 각자 내려받습니다. 원본이 저장소에 없는 이유는 저작권입니다. [data/README.md](../data/README.md) 에 적어 두었습니다. 사이트에 부담을 주지 않도록 사이트마다 간격을 두고 받게 돼 있습니다. 그 값은 줄이지 않습니다.

끝나면 `data/raw` 폴더에 파일이 40개 넘게 있어야 합니다. 몇 건 실패했으면 같은 명령을 한 번 더 돌립니다. 계속 실패하는 문서는 그것만 다시 받습니다.

```bash
.venv/bin/python data/download_corpus.py --only <doc_id>
```

## 6. 되는지 확인

**Mac**

```bash
make test
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\python -m pytest -q
```

지금은 **실패가 정상**입니다. 채울 함수 세 개가 비어 있어서 `NotImplementedError` 로 실패합니다. 마지막 줄에 `failed` 와 `skipped` 만 있고 `error` 가 없으면 설치는 된 것입니다.

## 막힐 때

| 증상 | 이유 | 이렇게 합니다 |
|---|---|---|
| `uv: command not found` | 설치 뒤 터미널을 새로 안 열었습니다 | 터미널을 닫고 새로 엽니다 |
| 파이썬 3.12 를 못 찾는다 | 아직 없는 것입니다 | uv 가 받아 오니 기다립니다. 인터넷이 필요합니다 |
| SSL 오류가 나거나 내려받기가 멈춘다 | 회사 네트워크의 보안 검사 | 휴대폰 핫스팟으로 바꿔 다시 돌립니다 |
| 회사 노트북이라 설치가 막힌다 | 관리자 권한 문제 | 오늘은 강사 화면으로 따라오고, 개인 노트북에서 다시 합니다 |
| Mac 에서 `make: command not found` | 1번 첫 줄 설치가 안 끝났습니다 | 첫 줄을 다시 하고 새 터미널을 엽니다 |
| Windows 에서 `make` 가 없다 | 원래 없습니다 | 위의 PowerShell 명령을 씁니다 |
| `make notebook` 을 해도 브라우저가 안 뜬다 | 터미널에 뜬 주소를 안 열었습니다 | 터미널의 `http://localhost:8888/...` 줄을 복사해 브라우저에 붙입니다 |
| Windows 에서 노트북을 열려면 | `make` 가 없습니다 | `.venv\Scripts\python -m jupyter lab notebooks\s02_parsers.ipynb` |
| VS Code 로 노트북을 열고 싶다 | 됩니다 | 파일을 열고 오른쪽 위 커널 선택에서 `.venv` 의 파이썬을 고릅니다 |
| `make test` 에 `error` 가 있다 | 패키지가 덜 깔렸습니다 | 4번을 다시 합니다. 그래도 그러면 오류 줄을 채팅에 붙입니다 |

## 오늘 못 받았으면

수업 1~3부는 강사 화면으로 따라오면 됩니다. 4~5부의 함수 채우기는 문서가 없어도 됩니다 — `make test` 의 앞부분 테스트는 코퍼스 없이 돕니다. `make chunk` 만 문서가 필요하니, 수업 뒤에 받아서 돌립니다.
