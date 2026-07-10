# l0

## paperdoc
Figure.__init__(name: str, data: bytes, mime: str)
PaperDocument.__init__(markdown: str, figures: list[Figure] = [])
PaperDocument.get_figure(name: str) -> Figure | None

## sectioner
Sectioner.__init__(max_chars: int = 12000)
Sectioner.split(markdown: str) -> list[str]
