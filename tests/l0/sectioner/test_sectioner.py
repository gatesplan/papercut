import pytest

from ff_papercut.l0.sectioner import Sectioner


class TestSectioner:
    def test_invalid_max_chars(self):
        with pytest.raises(ValueError):
            Sectioner(max_chars=0)

    def test_split_by_headers(self):
        md = '# A\ntext a\n## B\ntext b\n# C\ntext c\n'
        sections = Sectioner().split(md)
        assert len(sections) == 3
        assert sections[0].startswith('# A')
        assert sections[1].startswith('## B')
        assert sections[2].startswith('# C')

    def test_header_inside_code_fence_ignored(self):
        md = '# A\n```\n# not a header\n```\nmore\n# B\nend\n'
        sections = Sectioner().split(md)
        assert len(sections) == 2
        assert '# not a header' in sections[0]

    def test_oversized_section_split_by_paragraph(self):
        paragraphs = '\n\n'.join(['word ' * 50 for _ in range(10)])
        md = '# Big\n' + paragraphs
        sections = Sectioner(max_chars=600).split(md)
        assert len(sections) > 1
        assert all(len(s) <= 600 for s in sections)

    def test_single_huge_paragraph_hard_cut(self):
        md = 'x' * 25000
        sections = Sectioner(max_chars=10000).split(md)
        assert len(sections) == 3
        assert ''.join(sections) == md

    def test_no_header_document(self):
        md = 'just plain text\n\nwith paragraphs'
        sections = Sectioner().split(md)
        assert sections == [md]

    def test_blank_input(self):
        assert Sectioner().split('   \n  ') == []
