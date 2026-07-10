from types import SimpleNamespace

import pytest

from ff_papercut.l0.llmresult import TextResult
from ff_papercut.l1.llmclient import LLMClient, DEFAULT_MODEL


def make_response(content, usage=None):
    message = SimpleNamespace(content=content)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage)


def make_usage():
    return SimpleNamespace(
        prompt_tokens=100, completion_tokens=50, total_tokens=150,
        prompt_tokens_details=SimpleNamespace(cached_tokens=30),
        completion_tokens_details=SimpleNamespace(reasoning_tokens=10),
    )


class FakeCompletions:
    def __init__(self, content, usage=None):
        self.content = content
        self.usage = usage
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return make_response(self.content, self.usage)


def make_client(content, usage=None):
    client = LLMClient(api_key='k')
    fake = FakeCompletions(content, usage)
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
    return client, fake


class TestLLMClient:
    def test_empty_api_key_raises(self):
        with pytest.raises(ValueError):
            LLMClient(api_key='')

    def test_default_model(self):
        client = LLMClient(api_key='k')
        assert client.model == DEFAULT_MODEL

    def test_complete_returns_text_result(self):
        client, fake = make_client('result text', make_usage())
        result = client.complete('hello')
        assert isinstance(result, TextResult)
        assert result.text == 'result text'
        assert fake.calls[0]['messages'] == [{'role': 'user', 'content': 'hello'}]

    def test_usage_extracted(self):
        client, _ = make_client('ok', make_usage())
        result = client.complete('hello')
        assert result.usage.prompt_tokens == 100
        assert result.usage.completion_tokens == 50
        assert result.usage.total_tokens == 150
        assert result.usage.cached_tokens == 30
        assert result.usage.reasoning_tokens == 10
        assert result.call_usages == [result.usage]

    def test_missing_usage_defaults_zero(self):
        client, _ = make_client('ok', usage=None)
        result = client.complete('hello')
        assert result.usage.total_tokens == 0

    def test_partial_usage_details(self):
        usage = SimpleNamespace(prompt_tokens=5, completion_tokens=3, total_tokens=8,
                                prompt_tokens_details=None, completion_tokens_details=None)
        client, _ = make_client('ok', usage)
        result = client.complete('hello')
        assert result.usage.prompt_tokens == 5
        assert result.usage.cached_tokens == 0

    def test_complete_with_system(self):
        client, fake = make_client('ok', make_usage())
        client.complete('hello', system='rule')
        assert fake.calls[0]['messages'][0] == {'role': 'system', 'content': 'rule'}

    def test_none_content_raises(self):
        client, _ = make_client(None, make_usage())
        with pytest.raises(RuntimeError):
            client.complete('hello')
