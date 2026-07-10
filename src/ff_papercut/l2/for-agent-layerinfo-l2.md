# l2

## translator
Translator.__init__(api_key: str, model: str = 'grok-4.5', base_url: str = 'https://api.x.ai/v1', max_chars: int = 12000)
Translator.translate(markdown: str, translate_to: str) -> str

## summarizer
Summarizer.__init__(api_key: str, model: str = 'grok-4.5', base_url: str = 'https://api.x.ai/v1', max_chars: int = 12000)
Summarizer.summarize(markdown: str, language: str) -> str
Summarizer.quick_read(markdown: str, language: str) -> str
