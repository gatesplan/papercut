# for-agent-layerinfo.md

## l0
- paperdoc: 추출 결과 데이터 타입 (PaperDocument, Figure)
- sectioner: markdown 섹션 분할
- llmresult: LLM 결과 데이터 타입 (TextResult, LLMUsage)

## l1
- extractor: PDF -> PaperDocument 변환 (MinerU 로컬 API 서버 래퍼)
- llmclient: OpenAI 호환 LLM API 호출 (기본 xAI Grok 4.5)

## l2
- translator: markdown 번역 (섹션 단위 LLM 처리)
- summarizer: 압축 보고서(summarize) / 섹션별 요약(quick_read)
