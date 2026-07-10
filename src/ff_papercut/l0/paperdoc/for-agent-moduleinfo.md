# paperdoc

추출 결과 데이터 타입. 파일 관리 없이 메모리 상 데이터로만 존재.

## Figure

논문에서 추출된 그림 1개. frozen dataclass.

### Properties
name: str          # markdown 본문이 참조하는 상대 경로 (예: images/abc.jpg)
data: bytes        # 이미지 바이너리
mime: str          # MIME 타입 (예: image/jpeg)

### __init__
__init__(name: str, data: bytes, mime: str)
    raise ValueError, TypeError
    name이 비어 있으면 ValueError, data가 bytes가 아니면 TypeError.

## PaperDocument

추출 결과: markdown 본문 + 그림 목록. frozen dataclass.

### Properties
markdown: str            # 추출된 markdown 전문
figures: list[Figure]    # 본문이 참조하는 그림들

### __init__
__init__(markdown: str, figures: list[Figure] = [])
    기본 figures는 빈 리스트.

### Methods

get_figure(name: str) -> Figure | None
    markdown이 참조하는 상대 경로로 그림 조회. 없으면 None.
