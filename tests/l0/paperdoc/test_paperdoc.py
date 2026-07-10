import pytest

from ff_papercut.l0.paperdoc import Figure, PaperDocument


class TestFigure:
    def test_create(self):
        f = Figure(name='images/a.jpg', data=b'\xff\xd8', mime='image/jpeg')
        assert f.name == 'images/a.jpg'
        assert f.data == b'\xff\xd8'

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Figure(name='', data=b'x', mime='image/png')

    def test_non_bytes_data_raises(self):
        with pytest.raises(TypeError):
            Figure(name='a.png', data='not-bytes', mime='image/png')


class TestPaperDocument:
    def test_default_figures_empty(self):
        doc = PaperDocument(markdown='# Title')
        assert doc.figures == []

    def test_get_figure(self):
        f = Figure(name='images/a.jpg', data=b'x', mime='image/jpeg')
        doc = PaperDocument(markdown='![](images/a.jpg)', figures=[f])
        assert doc.get_figure('images/a.jpg') is f
        assert doc.get_figure('images/none.jpg') is None
