from loguru import logger

from ...l0.llmresult import TextResult
from ...l0.sectioner import Sectioner
from ...l1.llmclient import LLMClient, DEFAULT_MODEL, DEFAULT_BASE_URL

SYSTEM_PROMPT = (
    "당신은 학술 논문 전문 번역가다. 다음 규칙을 반드시 지킨다.\n"
    "1. markdown 구조(헤더, 표, 목록, 이미지 참조, 링크)를 그대로 보존한다. "
    "단, 보존 대상은 구조이지 줄바꿈 위치가 아니다. 문장 중간에서 깨진 줄바꿈이나 "
    "잘못 나뉜 줄은 완결된 문장과 문단으로 재구성한다.\n"
    "2. 섹션 헤더의 텍스트도 본문과 동일하게 번역한다. 헤더를 원문 그대로 남기지 않는다.\n"
    "3. 수식(LaTeX), 코드 블록, 이미지 경로는 번역하지 않고 원형 유지한다.\n"
    "4. 원문의 문자 표기를 임의로 바꾸지 않는다. 예: H2O를 H₂O로, cm-1을 cm⁻¹로 변환 금지.\n"
    "5. 고유명사(물질명, 학술용어 등)는 번역어 뒤에 원어를 괄호로 병기한다. 예: olivine -> 감람석(olivine)\n"
    "6. 원어가 영어가 아닌 용어는 발음도 함께 병기한다. 예: 원어(원어표기;발음)\n"
    "7. 번역 결과만 출력한다. 설명이나 주석을 덧붙이지 않는다."
)


# markdown 논문을 지정 언어로 번역. 섹션 단위로 분할하여 LLM 호출.
class Translator:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL,
                 base_url: str = DEFAULT_BASE_URL, max_chars: int = 12000):
        self._llm = LLMClient(api_key=api_key, model=model, base_url=base_url)
        self._sectioner = Sectioner(max_chars=max_chars)

    def translate(self, markdown: str, translate_to: str) -> TextResult:
        if not markdown.strip():
            raise ValueError("markdown이 비어 있다")
        if not translate_to:
            raise ValueError("translate_to가 비어 있다")
        sections = self._sectioner.split(markdown)
        logger.info(f"번역 시작: {len(sections)}개 섹션, 대상 언어 {translate_to}")
        texts = []
        call_usages = []
        for index, section in enumerate(sections, start=1):
            prompt = f"다음 학술 논문 markdown 조각을 {translate_to}(으)로 번역하라.\n\n{section}"
            result = self._llm.complete(prompt, system=SYSTEM_PROMPT)
            texts.append(result.text)
            call_usages.append(result.usage)
            logger.debug(f"섹션 번역 완료 {index}/{len(sections)}")
        return TextResult.from_calls('\n\n'.join(texts), call_usages)
