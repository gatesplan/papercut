# translator

markdown 논문 번역. 섹션 단위로 분할하여 LLM 처리 후 재조립.

## Translator

### __init__
__init__(api_key: str, model: str = 'grok-4.5', base_url: str = 'https://api.x.ai/v1', max_chars: int = 12000)
    raise ValueError
    내부에 LLMClient와 Sectioner를 생성한다. api_key가 비어 있으면 ValueError.

### Methods

translate(markdown: str, translate_to: str) -> TextResult
    raise ValueError, openai.APIError 계열
    markdown 또는 translate_to가 비어 있으면 ValueError.
    Sectioner로 분할 후 섹션별 LLM 호출, '\n\n'으로 재조립.
    반환 TextResult에 합산 usage와 섹션별 call_usages 포함.
    번역 규칙 (시스템 프롬프트에 고정):
    - markdown 구조, 수식, 코드, 이미지 참조 보존
    - 고유명사는 원어 병기: olivine -> 감람석(olivine)
    - 비영어 원어는 발음 병기

## 설계 이유

- 섹션 분할 이유: 번역 출력 길이는 입력에 비례하여 LLM 최대 출력 한도를 초과할 수 있음.
- 대상 언어는 파라미터로만 받는다. 패키지가 임의로 정하지 않는다. [확정]
