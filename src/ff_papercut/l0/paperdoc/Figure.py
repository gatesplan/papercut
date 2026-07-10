from dataclasses import dataclass


# 논문에서 추출된 그림 1개. name은 markdown 본문이 참조하는 상대 경로.
@dataclass(frozen=True)
class Figure:
    name: str
    data: bytes
    mime: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("name이 비어 있다")
        if not isinstance(self.data, bytes):
            raise TypeError("data는 bytes여야 한다")
