# 새턴 봄버맨 (세가 새턴 일본판) 한글 패치

- 원본: `Saturn Bomberman (Japan)` (30트랙, 트랙 01 에만 패치, 트랙 02~30·cue 그대로)
- 배포 파일은 릴리즈의 zip(xdelta + 적용 bat + readme)을 쓰세요.
- 그림 글자: 압축 해독·압축기 `tools/bcomp.py`, 판 그리기 `tools/gfx_plates.py`·`tools/gfx_custom_menu.py`
- 스프라이트 조합 문장: 저장 안내문 `tools/save_msgs.py`(data/save_msgs_ko.txt) · 대사창 `tools/dialogue.py`(data/dialogue_ko.txt) · 세로쓰기 `tools/story_vert.py` · 게임 오버 `tools/gameover.py`
- 오프닝 동영상 자막: `tools/moviesub.py`(data/voice.tsv)
- 빌드 `tools/build.py` → 배포 `tools/make_dist.py`
- 조사·결정 기록: `docs/00_초기조사.md`
