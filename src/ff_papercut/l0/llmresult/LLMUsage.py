from dataclasses import dataclass


# LLM 호출 1회의 토큰 사용량. 합산은 + 연산자.
@dataclass(frozen=True)
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0

    def __add__(self, other):
        if not isinstance(other, LLMUsage):
            return NotImplemented
        return LLMUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cached_tokens=self.cached_tokens + other.cached_tokens,
            reasoning_tokens=self.reasoning_tokens + other.reasoning_tokens,
        )
