# sectioner

markdown을 LLM 처리 단위(섹션)로 분할. 표준 라이브러리만 사용.

## Sectioner

헤더 우선 분할, 과대 섹션은 크기 기준 보조 분할.

### Properties
max_chars: int     # 섹션 최대 길이 (문자 수, 토큰의 근사치로 사용)

### __init__
__init__(max_chars: int = 12000)
    raise ValueError
    max_chars가 양수가 아니면 ValueError.

### Methods

split(markdown: str) -> list[str]
    ATX 헤더(#~######) 시작 줄에서 섹션 경계를 나눈다.
    코드 펜스(``` 또는 ~~~) 내부의 # 줄은 헤더로 취급하지 않는다.
    max_chars 초과 섹션은 빈 줄(문단) 경계로 누적 분할하고,
    단일 문단이 한도를 넘으면 강제 절단한다.
    공백뿐인 섹션은 결과에서 제외.
