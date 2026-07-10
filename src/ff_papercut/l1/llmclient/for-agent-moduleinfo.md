# llmclient

OpenAI 호환 LLM API 호출. 번역/요약이 공유하는 단일 호출 창구.

## LLMClient

기본값은 xAI Grok 4.5. base_url/model 교체로 OpenAI 호환 API 어디든 사용 가능.

### Properties
model: str     # 사용 모델 ID

### __init__
__init__(api_key: str, model: str = 'grok-4.5', base_url: str = 'https://api.x.ai/v1', max_retries: int = 3, timeout: float = 600.0)
    raise ValueError
    api_key가 비어 있으면 ValueError.
    재시도는 openai SDK에 위임 (max_retries). 소진 시 SDK 예외가 상위로 전파된다.
    패키지는 .env를 읽지 않는다. 키 관리는 호출측 책임.

### Methods

complete(prompt: str, system: str | None = None) -> str
    raise RuntimeError, openai.APIError 계열
    chat.completions 호출 후 응답 텍스트 반환.
    응답에 텍스트가 없으면 RuntimeError.

## 설계 이유

- 모델 ID 'grok-4.5'는 실호출로 확인 완료 (2026-07-10 통합 테스트). [근거, .meta/260709-그록4.5가격조사.md]
