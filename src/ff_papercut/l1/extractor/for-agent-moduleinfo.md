# extractor

PDF -> PaperDocument 변환. MinerU 3.x 로컬 API 서버(mineru-api 서브프로세스)를 관리한다.

## Extractor

객체 하나 = 직렬 처리 1워커. 병렬화는 객체 다중 생성 + 상위 서비스 분배.

### Properties
backend: str           # MinerU 백엔드 (pipeline, vlm-engine, hybrid-engine 등)
auto_unload: bool      # 큐 소진 시 자동 unload 여부
language: str          # OCR 언어 힌트
formula_enable: bool   # 수식 인식
table_enable: bool     # 표 인식

### __init__
__init__(backend: str = 'pipeline', auto_unload: bool = False, language: str = 'en', formula_enable: bool = True, table_enable: bool = True)
    raise ImportError
    mineru 미설치면 ImportError. 서버는 기동하지 않는다 (lazy).

### Methods

extract(pdf: bytes | str | Path) -> PaperDocument
    raise FileNotFoundError, TypeError, RuntimeError
    첫 호출 시 mineru-api 서브프로세스 기동 (lazy 로드).
    동시 호출은 내부 락으로 직렬화된다.
    경로 입력이 존재하지 않으면 FileNotFoundError, bytes/경로 외 타입은 TypeError.
    결과 zip에서 markdown이 없으면 RuntimeError.
    figure의 name은 markdown이 참조하는 상대 경로와 일치한다.

unload() -> None
    서브프로세스 종료로 VRAM/RAM을 OS 수준에서 확실히 반납.
    진행 중 작업이 있으면 예약되어 마지막 작업 완료 시 수행된다.
    unload 후에도 객체는 유효하며 다음 extract()에서 재기동된다.

## 설계 이유

- 서브프로세스 방식 채택 이유: in-process(do_parse)는 mineru 내부 전역 모델 캐시 때문에
  파이썬에서 VRAM 확실 해제가 불가능. 프로세스 종료만이 반납을 보장한다.
  [근거, .meta/260710-미네루3.4API조사.md]
- 모델 가중치는 서버측 첫 파싱 시 자동 다운로드된다. 서버 배포 시
  mineru-models-download로 사전 다운로드 권장.
- 상태 전이(_ensure_server/unload)는 _state_lock, 작업 직렬화는 _job_lock으로 보호.
- 결과 zip 내부 구조는 버전에 따라 다를 수 있어 재귀 탐색으로 md/이미지를 수집한다.
