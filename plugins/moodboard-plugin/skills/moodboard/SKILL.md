---
name: moodboard
description: >
  Pinterest에서 키워드로 레퍼런스 이미지 10장을 자동 수집해 무드보드를 만드는 스킬.
  사용자가 /moodboard, "무드보드", "moodboard", "핀터레스트 레퍼런스", "pinterest reference",
  "레퍼런스 수집", "이미지 모아줘", "분위기 참고할 이미지", "레퍼런스 이미지 찾아줘" 등을
  언급할 때 반드시 이 스킬을 사용한다. 키워드가 주어지면 즉시 실행하고,
  없으면 먼저 키워드를 물어본다.
---

# Moodboard Skill

Pinterest에서 키워드를 검색해 레퍼런스 이미지 10장을 자동 수집하는 워크플로우.

## 실행 위치

```
~/pinterest_collector/main.py
```

저장 결과: `~/Downloads/pinterest_refs/<키워드>_<타임스탬프>/`  
중복 기록: `~/Downloads/pinterest_refs/.dedup_store.json`

---

## 워크플로우

### 1단계: 키워드 확인

- `/moodboard <키워드>` 형태로 인자가 있으면 바로 실행
- 키워드 없이 요청이 들어오면 한 줄로 물어본다:
  > "어떤 키워드로 수집할까요? (예: minimal interior, dark academia, y2k fashion)"

### 2단계: 실행

```bash
cd ~/pinterest_collector && python3 main.py "<키워드>"
```

실행 전 사용자에게 알린다:
> "**[SearchAgent]** Pinterest에서 '<키워드>' 검색을 시작합니다.  
> 브라우저 창이 열릴 수 있습니다 — 자동으로 진행되니 건드리지 않아도 됩니다."

### 3단계: 결과 보고

실행이 완료되면 아래 형식으로 보고한다.

```
수집 완료: 10장
저장 위치: ~/Downloads/pinterest_refs/<키워드>_<타임스탬프>/

파일 목록:
  01_<키워드>.jpg
  02_<키워드>.jpg
  ...

중복 방지: URL 레벨 + 콘텐츠 해시(SHA-256) 2중 체크
다음 실행 시 이미 받은 이미지는 자동으로 건너뜁니다.
```

---

## 에러 처리

| 상황 | 대응 |
|---|---|
| `python3 main.py`를 찾을 수 없음 | `cd ~/pinterest_collector`가 맞는지 확인 후 재시도. 없으면 셋업 필요 안내 |
| 10장 미달 | 실제 저장된 수를 알리고, 키워드를 다르게 시도할지 제안 |
| 브라우저 차단 / 로그인 요구 | 핀터레스트가 접근을 막았을 수 있음을 안내하고 `headless=False` 상태인지 확인 |
| playwright 미설치 | `pip3 install playwright && python3 -m playwright install chromium` 실행 안내 |

---

## 참고: 내부 구조

이 스킬은 두 에이전트의 파이프라인으로 동작한다:

- **SearchAgent** (`~/pinterest_collector/search_agent.py`): Playwright로 Pinterest 탐색 → 이미지 URL 목록 반환
- **CaptureAgent** (`~/pinterest_collector/capture_agent.py`): URL 다운로드 + 중복 방지(URL/해시 2단계)

셋업이 안 된 환경이라면:
```bash
pip3 install playwright httpx
python3 -m playwright install chromium
```
