from ff_papercut.l0.llmresult import LLMUsage, TextResult


class TestLLMUsage:
    def test_defaults_zero(self):
        u = LLMUsage()
        assert u.prompt_tokens == 0
        assert u.total_tokens == 0

    def test_add(self):
        a = LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15,
                     cached_tokens=3, reasoning_tokens=2)
        b = LLMUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2,
                     cached_tokens=1, reasoning_tokens=1)
        c = a + b
        assert c.prompt_tokens == 11
        assert c.completion_tokens == 6
        assert c.total_tokens == 17
        assert c.cached_tokens == 4
        assert c.reasoning_tokens == 3


class TestTextResult:
    def test_from_calls_sums_usage(self):
        calls = [LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                 LLMUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)]
        r = TextResult.from_calls('text', calls)
        assert r.text == 'text'
        assert r.usage.prompt_tokens == 30
        assert r.usage.total_tokens == 45
        assert len(r.call_usages) == 2

    def test_from_calls_empty(self):
        r = TextResult.from_calls('text', [])
        assert r.usage == LLMUsage()
        assert r.call_usages == []
