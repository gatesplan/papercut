# l0

## paperdoc
Figure.__init__(name: str, data: bytes, mime: str)
PaperDocument.__init__(markdown: str, figures: list[Figure] = [])
PaperDocument.get_figure(name: str) -> Figure | None

## sectioner
Sectioner.__init__(max_chars: int = 12000)
Sectioner.split(markdown: str) -> list[str]

## llmresult
LLMUsage.__init__(prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0, cached_tokens: int = 0, reasoning_tokens: int = 0)
LLMUsage.__add__(other: LLMUsage) -> LLMUsage
TextResult.__init__(text: str, usage: LLMUsage, call_usages: list[LLMUsage] = [])
TextResult.from_calls(text: str, call_usages: list[LLMUsage]) -> TextResult
