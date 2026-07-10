# summarizer

markdown 논문 요약. 두 모드 제공: 압축 보고서(summarize), 섹션별 요약(quick_read).

## Summarizer

### __init__
__init__(api_key: str, model: str = 'grok-4.5', base_url: str = 'https://api.x.ai/v1', max_chars: int = 12000)
    raise ValueError
    내부에 LLMClient와 Sectioner를 생성한다. api_key가 비어 있으면 ValueError.

### Methods

summarize(markdown: str, language: str) -> TextResult
    raise ValueError, openai.APIError 계열
    논문 전체를 한 번의 LLM 호출로 압축 보고서 생성.
    고정 템플릿: TLDR / 연구 질문·목적 / 방법 / 핵심 결과 / 한계 / 의의.
    분량은 논문 길이와 무관하게 일정.
    Grok 컨텍스트 500K 토큰 기준 일반 논문은 단일 호출로 충분.

quick_read(markdown: str, language: str) -> TextResult
    raise ValueError, openai.APIError 계열
    섹션별 압축 (빨리읽기). 원문 구조(헤더) 보존.
    300자 미만 섹션은 LLM 호출 없이 원문 유지 (usage 미발생).
    '\n\n'으로 재조립. 합산 usage와 호출별 call_usages 포함.

## 설계 이유

- summarize와 quick_read를 분리한 이유: 호출 패턴(전체 1회 vs 섹션 순회)과
  출력 분량 특성(일정 vs 논문 길이 비례)이 다름. [근거, Architecture.md 요약 형식]
- 요약 언어는 language 파라미터로 지정. 용어 원어 병기 규칙은 번역과 동일 적용. [확정]
