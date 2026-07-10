from loguru import logger

from ...l0.sectioner import Sectioner
from ...l1.llmclient import LLMClient, DEFAULT_MODEL, DEFAULT_BASE_URL

TERM_RULES = (
    "고유명사(물질명, 학술용어 등)는 번역어 뒤에 원어를 괄호로 병기한다. "
    "원어가 영어가 아닌 용어는 발음도 함께 병기한다. "
    "원문의 문자 표기를 임의로 바꾸지 않는다 (예: H2O를 H₂O로, cm-1을 cm⁻¹로 변환 금지)."
)

REPORT_SYSTEM = (
    "당신은 학술 논문 분석가다. 논문 전체를 읽고 지정된 언어로 압축 보고서를 작성한다.\n"
    f"{TERM_RULES}\n"
    "다음 markdown 템플릿을 정확히 따르고, 템플릿 외 내용은 출력하지 않는다.\n\n"
    "# TLDR\n(1~2문장)\n\n"
    "# 연구 질문/목적\n\n# 방법\n\n# 핵심 결과\n\n# 한계\n\n# 의의\n"
)

QUICK_READ_SYSTEM = (
    "당신은 학술 논문 요약가다. 주어진 논문 섹션을 지정된 언어로 몇 문장으로 압축한다.\n"
    f"{TERM_RULES}\n"
    "섹션의 헤더는 그대로 유지하고 본문만 압축한다. 수식/표는 핵심 의미만 서술한다.\n"
    "압축 결과만 출력한다. 설명이나 주석을 덧붙이지 않는다."
)

# 이 길이 미만 섹션은 LLM 호출 없이 원문 유지
QUICK_READ_MIN_CHARS = 300


# markdown 논문 요약. summarize()는 논문 전체 압축 보고서, quick_read()는 섹션별 요약.
class Summarizer:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL,
                 base_url: str = DEFAULT_BASE_URL, max_chars: int = 12000):
        self._llm = LLMClient(api_key=api_key, model=model, base_url=base_url)
        self._sectioner = Sectioner(max_chars=max_chars)

    def summarize(self, markdown: str, language: str) -> str:
        # 논문 전체를 한 번에 요약 (Grok 컨텍스트 500K 토큰이면 일반 논문 충분)
        self._validate(markdown, language)
        logger.info(f"압축 보고서 생성 시작: {len(markdown)}자, 언어 {language}")
        prompt = f"다음 논문을 {language}(으)로 요약하라.\n\n{markdown}"
        return self._llm.complete(prompt, system=REPORT_SYSTEM)

    def quick_read(self, markdown: str, language: str) -> str:
        # 원문 구조를 보존한 섹션별 압축 (빨리읽기)
        self._validate(markdown, language)
        sections = self._sectioner.split(markdown)
        logger.info(f"빨리읽기 생성 시작: {len(sections)}개 섹션, 언어 {language}")
        compressed = []
        for index, section in enumerate(sections, start=1):
            if len(section.strip()) < QUICK_READ_MIN_CHARS:
                compressed.append(section.strip())
                continue
            prompt = f"다음 논문 섹션을 {language}(으)로 압축하라.\n\n{section}"
            compressed.append(self._llm.complete(prompt, system=QUICK_READ_SYSTEM))
            logger.debug(f"섹션 압축 완료 {index}/{len(sections)}")
        return '\n\n'.join(compressed)

    def _validate(self, markdown: str, language: str) -> None:
        if not markdown.strip():
            raise ValueError("markdown이 비어 있다")
        if not language:
            raise ValueError("language가 비어 있다")
