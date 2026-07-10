from loguru import logger
from openai import OpenAI

from ...l0.llmresult import LLMUsage, TextResult

DEFAULT_MODEL = 'grok-4.5'
DEFAULT_BASE_URL = 'https://api.x.ai/v1'


# OpenAI 호환 LLM API 호출. 기본값은 xAI Grok 4.5. 재시도는 SDK에 위임, 소진 시 예외 전파.
class LLMClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL,
                 base_url: str = DEFAULT_BASE_URL,
                 max_retries: int = 3, timeout: float = 600.0):
        if not api_key:
            raise ValueError("api_key가 비어 있다")
        self.model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url,
                              max_retries=max_retries, timeout=timeout)

    def complete(self, prompt: str, system: str | None = None) -> TextResult:
        messages = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': prompt})
        logger.debug(f"LLM 호출: model={self.model}, prompt {len(prompt)}자")
        response = self._client.chat.completions.create(model=self.model, messages=messages)
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("LLM 응답에 텍스트가 없다")
        usage = self._extract_usage(response)
        logger.debug(f"LLM 응답: prompt {usage.prompt_tokens} / completion {usage.completion_tokens} 토큰")
        return TextResult(text=content, usage=usage, call_usages=[usage])

    def _extract_usage(self, response) -> LLMUsage:
        # usage 필드가 없거나 세부 구조가 다른 provider도 있어 방어적으로 추출
        usage = getattr(response, 'usage', None)
        if usage is None:
            return LLMUsage()
        prompt_details = getattr(usage, 'prompt_tokens_details', None)
        completion_details = getattr(usage, 'completion_tokens_details', None)
        return LLMUsage(
            prompt_tokens=getattr(usage, 'prompt_tokens', 0) or 0,
            completion_tokens=getattr(usage, 'completion_tokens', 0) or 0,
            total_tokens=getattr(usage, 'total_tokens', 0) or 0,
            cached_tokens=getattr(prompt_details, 'cached_tokens', 0) or 0,
            reasoning_tokens=getattr(completion_details, 'reasoning_tokens', 0) or 0,
        )
