# seoro-audio — SEORO CLASSICS 음원 저장소

0505.co.kr(home2 저장소)의 교재 페이지가 쓰는 음원만 모아 둔 저장소. GitHub Pages로 공개되며,
교재 HTML은 `https://nmyway77.github.io/seoro-audio/audio/<파일>.mp3` 주소로 음원을 불러온다.
(home2 저장소의 1GB 한도와 별개로 이 저장소가 1GB를 따로 쓴다. 다 차면 `seoro-audio2`를 만들어 같은 방식으로 잇는다.)

## 폴더
- `audio/` — 교재 페이지가 실제로 재생하는 완성 음원 (48kbps 모노). 이름: `SEORO-CLASSICS_GR<레벨>_<제목>_p<쪽>_<fen|cen|ckr|...>.mp3`
  - `fen` 영어 문장 원어민 녹음, `cen` 영어 어구 더빙, `ckr` 한국어 어구 더빙
- `_tts_jobs/` — ElevenLabs 녹음 요청(JSON). 여기에 `*.json`이 푸시되면 Actions가 녹음한다.
  - `_tts_jobs/pending/` — 아직 녹음하지 않을 요청(크레딧 확인 뒤 상위 폴더로 옮기면 녹음 시작)
  - `_tts_jobs/done/` — 처리 끝난 요청
- `_tts_out/` — Actions가 받아 온 원본 mp3(128k) + 글자별 시각(json). home2의 `_seoro_tools/autotts.py attach`가 이걸 읽어 `audio/`에 완성 음원을 만든다.
- `tools/tts_gh.py` — Actions에서 실행되는 녹음 스크립트. 키는 저장소 Secrets `ELEVENLABS_API_KEY`.

## 흐름
1. home2: `python3 _seoro_tools/autotts.py make <mod>` → 이 저장소 `_tts_jobs/<mod>.json` 생성
2. 이 저장소 커밋·푸시 → Actions 녹음 → `_tts_out/`에 결과 커밋 (https://github.com/nmyway77/seoro-audio/actions)
3. home2: `python3 _seoro_tools/autotts.py attach <mod>` → 이 저장소 `audio/`에 완성 음원, home2 쪽 HTML에 주소·시각 반영
4. 두 저장소 모두 커밋·푸시
