# llmresult

LLM 호출 결과 데이터 타입. 텍스트와 토큰 사용량을 함께 전달한다.

## LLMUsage

LLM 호출 1회(또는 합산)의 토큰 사용량. frozen dataclass.

### Properties
prompt_tokens: int       # 입력 토큰
completion_tokens: int   # 출력 토큰
total_tokens: int        # 합계
cached_tokens: int       # 캐시된 입력 토큰 (provider 미제공 시 0)
reasoning_tokens: int    # 추론 토큰 (provider 미제공 시 0)

### Methods

__add__(other: LLMUsage) -> LLMUsage
    필드별 합산. 여러 호출의 usage 누적에 사용.

## TextResult

LLM 처리 결과: 텍스트 + 합산 usage + 호출별 usage 상세. frozen dataclass.

### Properties
text: str                      # 결과 텍스트
usage: LLMUsage                # 전체 합산 사용량
call_usages: list[LLMUsage]    # 호출별 상세 (호출 순서대로)

### Methods

from_calls(text: str, call_usages: list[LLMUsage]) -> TextResult
    classmethod. 호출별 usage 목록에서 합산 usage를 계산하여 생성.
