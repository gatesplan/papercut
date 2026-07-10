import re

HEADER_PATTERN = re.compile(r'^#{1,6}\s')
FENCE_PATTERN = re.compile(r'^(```|~~~)')


# markdown을 LLM 처리 단위(섹션)로 분할. 헤더 우선, 과대 섹션은 크기 기준 보조 분할.
class Sectioner:
    def __init__(self, max_chars: int = 12000):
        if max_chars <= 0:
            raise ValueError("max_chars는 양수여야 한다")
        self.max_chars = max_chars

    def split(self, markdown: str) -> list[str]:
        sections = self._split_by_headers(markdown)
        result = []
        for section in sections:
            if len(section) <= self.max_chars:
                result.append(section)
            else:
                result.extend(self._split_by_size(section))
        return [s for s in result if s.strip()]

    def _split_by_headers(self, markdown: str) -> list[str]:
        # 코드 펜스 내부의 # 줄은 헤더로 취급하지 않음
        sections = []
        current = []
        in_fence = False
        for line in markdown.splitlines(keepends=True):
            if FENCE_PATTERN.match(line):
                in_fence = not in_fence
            if not in_fence and HEADER_PATTERN.match(line) and current:
                sections.append(''.join(current))
                current = []
            current.append(line)
        if current:
            sections.append(''.join(current))
        return sections

    def _split_by_size(self, section: str) -> list[str]:
        # 빈 줄(문단) 경계로 누적 분할, 단일 문단이 한도 초과면 강제 절단
        chunks = []
        current = ''
        for paragraph in section.split('\n\n'):
            piece = paragraph if not current else current + '\n\n' + paragraph
            if len(piece) <= self.max_chars:
                current = piece
                continue
            if current:
                chunks.append(current)
            while len(paragraph) > self.max_chars:
                chunks.append(paragraph[:self.max_chars])
                paragraph = paragraph[self.max_chars:]
            current = paragraph
        if current:
            chunks.append(current)
        return chunks
