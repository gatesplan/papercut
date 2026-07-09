# 프로젝트 프로토콜

## 구조 및 코딩 규칙

- Ln 구조: `.claude/for-agent-codingprotocol-ln-structure.md` 참조
- Python 코딩: `.claude/for-agent-codingprotocol-python.md` 참조
- 연구 프로토콜: `.claude/for-agent-research.md` 참조

## 사실관리 규칙

[확정] 유저가 확정한 사항에 대한 내용 기록시 시작 부분에 [확정] 태그를 쓴다.
[추측] 에이전트가 유저의 구체적 명시 없이 추측한 모든 내용은 시작 부분에 [추측] 태그를 쓴다.
각 설명 내용 등 모든 경우 근거가 있을 때에는 해당 지점의 문장을 마칠 때 [근거, {주소}] 형식으로 작성한다.
[추적필요] 장기적 조사가 필요한 내용에 대하여 특별히 기록하는 태그. 아직 발생하지 않았으나 예정된 이벤트에 대한 조사이다.

## 조사 기록 규칙

조사한 사항은 발생일 기준으로 `.meta/yymmdd-{한글이름띄어쓰기없이}.md`에 저장한다. 내용은 출처와 함께 조사결과로 확인한 사항만 기록한다.

## 프로젝트 설명

ff-papercut: 외부 논문(PDF) 처리 파이프라인 패키지. Python 라이브러리 API로 제공되어 상위 대형 프로젝트의 서버측 서비스 구축에 사용된다.

[확정] 파일 저장/관리는 책임지지 않는다. 데이터 변환(출력 데이터 획득)까지만 책임진다.

1. pdf -> markdown data 추출 [확정] (MinerU 사용)
2. markdown data -> translated markdown data [확정] (Grok 4.5 API)
3. markdown data -> condensed report (TLDR + 구조화 요약) [확정] (Grok 4.5 API)
4. markdown data -> 섹션별 요약 (빨리읽기) [확정] (Grok 4.5 API)

## 추가 규칙

[프로젝트 특수 규칙이 있다면 여기에 작성]
