from dataclasses import dataclass, field

from .LLMUsage import LLMUsage


# LLM 처리 결과: 텍스트 + 합산 usage + 호출별 usage 상세
@dataclass(frozen=True)
class TextResult:
    text: str
    usage: LLMUsage
    call_usages: list[LLMUsage] = field(default_factory=list)

    @classmethod
    def from_calls(cls, text: str, call_usages: list[LLMUsage]) -> 'TextResult':
        # 호출별 usage 목록에서 합산 usage를 계산하여 생성
        total = LLMUsage()
        for usage in call_usages:
            total = total + usage
        return cls(text=text, usage=total, call_usages=list(call_usages))
