from dataclasses import dataclass, field

from .Figure import Figure


# 추출 결과: markdown 본문 + 본문이 참조하는 그림들
@dataclass(frozen=True)
class PaperDocument:
    markdown: str
    figures: list[Figure] = field(default_factory=list)

    def get_figure(self, name: str) -> Figure | None:
        # markdown이 참조하는 상대 경로로 그림 조회
        for figure in self.figures:
            if figure.name == name:
                return figure
        return None
