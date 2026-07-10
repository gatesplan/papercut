# l1

## extractor
Extractor.__init__(backend: str = 'pipeline', auto_unload: bool = False, language: str = 'en', formula_enable: bool = True, table_enable: bool = True)
Extractor.extract(pdf: bytes | str | Path) -> PaperDocument
Extractor.unload() -> None

## llmclient
LLMClient.__init__(api_key: str, model: str = 'grok-4.5', base_url: str = 'https://api.x.ai/v1', max_retries: int = 3, timeout: float = 600.0)
LLMClient.complete(prompt: str, system: str | None = None) -> TextResult
