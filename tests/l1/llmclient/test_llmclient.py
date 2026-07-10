from types import SimpleNamespace

import pytest

from ff_papercut.l1.llmclient import LLMClient, DEFAULT_MODEL


def make_response(content):
    message = SimpleNamespace(content=content)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeCompletions:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return make_response(self.content)


class TestLLMClient:
    def test_empty_api_key_raises(self):
        with pytest.raises(ValueError):
            LLMClient(api_key='')

    def test_default_model(self):
        client = LLMClient(api_key='k')
        assert client.model == DEFAULT_MODEL

    def test_complete(self):
        client = LLMClient(api_key='k')
        fake = FakeCompletions('result text')
        client._client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
        assert client.complete('hello') == 'result text'
        assert fake.calls[0]['messages'] == [{'role': 'user', 'content': 'hello'}]

    def test_complete_with_system(self):
        client = LLMClient(api_key='k')
        fake = FakeCompletions('ok')
        client._client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
        client.complete('hello', system='rule')
        assert fake.calls[0]['messages'][0] == {'role': 'system', 'content': 'rule'}

    def test_none_content_raises(self):
        client = LLMClient(api_key='k')
        fake = FakeCompletions(None)
        client._client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
        with pytest.raises(RuntimeError):
            client.complete('hello')
