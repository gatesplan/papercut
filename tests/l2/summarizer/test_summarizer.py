import pytest

from ff_papercut.l2.summarizer import Summarizer


class FakeLLM:
    def __init__(self):
        self.calls = []

    def complete(self, prompt, system=None):
        self.calls.append({'prompt': prompt, 'system': system})
        return f'[S{len(self.calls)}]'


class TestSummarize:
    def make(self):
        s = Summarizer(api_key='k')
        s._llm = FakeLLM()
        return s

    def test_empty_markdown_raises(self):
        with pytest.raises(ValueError):
            self.make().summarize('', '한국어')

    def test_empty_language_raises(self):
        with pytest.raises(ValueError):
            self.make().summarize('# A', '')

    def test_single_call_whole_document(self):
        s = self.make()
        result = s.summarize('# A\ntext\n# B\ntext', '한국어')
        assert result == '[S1]'
        assert len(s._llm.calls) == 1
        assert 'TLDR' in s._llm.calls[0]['system']


class TestQuickRead:
    def make(self):
        s = Summarizer(api_key='k')
        s._llm = FakeLLM()
        return s

    def test_short_section_kept_verbatim(self):
        s = self.make()
        result = s.quick_read('# A\nshort', '한국어')
        assert result == '# A\nshort'
        assert s._llm.calls == []

    def test_long_sections_compressed(self):
        long_body = 'word ' * 200
        md = f'# A\n{long_body}\n# B\n{long_body}'
        s = self.make()
        result = s.quick_read(md, '한국어')
        assert result == '[S1]\n\n[S2]'
        assert len(s._llm.calls) == 2

    def test_mixed_sections(self):
        long_body = 'word ' * 200
        md = f'# A\nshort\n# B\n{long_body}'
        s = self.make()
        result = s.quick_read(md, '한국어')
        assert result.startswith('# A\nshort')
        assert result.endswith('[S1]')
        assert len(s._llm.calls) == 1
