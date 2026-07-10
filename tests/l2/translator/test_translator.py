import pytest

from ff_papercut.l2.translator import Translator


class FakeLLM:
    def __init__(self):
        self.calls = []

    def complete(self, prompt, system=None):
        self.calls.append({'prompt': prompt, 'system': system})
        return f'[T{len(self.calls)}]'


class TestTranslator:
    def make(self):
        t = Translator(api_key='k')
        t._llm = FakeLLM()
        return t

    def test_empty_markdown_raises(self):
        with pytest.raises(ValueError):
            self.make().translate('  ', '한국어')

    def test_empty_target_raises(self):
        with pytest.raises(ValueError):
            self.make().translate('# A', '')

    def test_sections_translated_and_joined(self):
        t = self.make()
        result = t.translate('# A\ntext\n# B\ntext', '한국어')
        assert result == '[T1]\n\n[T2]'
        assert len(t._llm.calls) == 2
        assert '한국어' in t._llm.calls[0]['prompt']

    def test_system_prompt_has_rules(self):
        t = self.make()
        t.translate('# A\ntext', '한국어')
        system = t._llm.calls[0]['system']
        assert '병기' in system
        assert 'markdown' in system
