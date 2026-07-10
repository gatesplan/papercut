import importlib.util
import threading
import time

import pytest

from ff_papercut.l0.paperdoc import PaperDocument
from ff_papercut.l1.extractor import Extractor


@pytest.fixture
def extractor_cls(monkeypatch):
    # mineru 설치 여부와 무관하게 생성 가능하도록 find_spec 우회
    monkeypatch.setattr(importlib.util, 'find_spec', lambda name: object())
    return Extractor


def make_ready(extractor, parse_result=None, parse_hook=None):
    # 서버 기동/파싱을 mock으로 대체
    stopped = []

    def fake_ensure():
        extractor._base_url = 'http://fake'
        extractor._server = object()

    def fake_parse(pdf_bytes):
        if parse_hook:
            parse_hook()
        return parse_result or PaperDocument(markdown='# doc')

    def fake_stop():
        stopped.append(True)
        extractor._server = None
        extractor._base_url = None

    extractor._ensure_server = fake_ensure
    extractor._parse = fake_parse
    extractor._stop_server_locked = fake_stop
    return stopped


class TestConstructor:
    def test_mineru_missing_raises(self, monkeypatch):
        monkeypatch.setattr(importlib.util, 'find_spec', lambda name: None)
        with pytest.raises(ImportError):
            Extractor()


class TestReadInput:
    def test_bytes_passthrough(self, extractor_cls):
        e = extractor_cls()
        assert e._read_input(b'%PDF') == b'%PDF'

    def test_path_read(self, extractor_cls, tmp_path):
        f = tmp_path / 'a.pdf'
        f.write_bytes(b'%PDF-1.7')
        e = extractor_cls()
        assert e._read_input(str(f)) == b'%PDF-1.7'
        assert e._read_input(f) == b'%PDF-1.7'

    def test_missing_file_raises(self, extractor_cls):
        e = extractor_cls()
        with pytest.raises(FileNotFoundError):
            e._read_input('no-such-file.pdf')

    def test_wrong_type_raises(self, extractor_cls):
        e = extractor_cls()
        with pytest.raises(TypeError):
            e._read_input(123)


class TestLifecycle:
    def test_extract_returns_document(self, extractor_cls):
        e = extractor_cls()
        make_ready(e)
        doc = e.extract(b'%PDF')
        assert doc.markdown == '# doc'

    def test_no_auto_unload_keeps_server(self, extractor_cls):
        e = extractor_cls(auto_unload=False)
        stopped = make_ready(e)
        e.extract(b'%PDF')
        assert stopped == []
        assert e._server is not None

    def test_auto_unload_stops_after_drain(self, extractor_cls):
        e = extractor_cls(auto_unload=True)
        stopped = make_ready(e)
        e.extract(b'%PDF')
        assert stopped == [True]
        assert e._server is None

    def test_manual_unload_when_idle(self, extractor_cls):
        e = extractor_cls()
        stopped = make_ready(e)
        e.extract(b'%PDF')
        e.unload()
        assert stopped == [True]

    def test_unload_when_never_loaded_is_noop(self, extractor_cls):
        e = extractor_cls()
        stopped = make_ready(e)
        e.unload()
        assert stopped == [True]

    def test_unload_during_job_is_deferred(self, extractor_cls):
        e = extractor_cls()
        started = threading.Event()
        release = threading.Event()

        def hook():
            started.set()
            release.wait(timeout=5)

        stopped = make_ready(e, parse_hook=hook)
        worker = threading.Thread(target=e.extract, args=(b'%PDF',))
        worker.start()
        assert started.wait(timeout=5)
        e.unload()
        assert e._unload_requested is True
        assert stopped == []
        release.set()
        worker.join(timeout=5)
        assert stopped == [True]
        assert e._unload_requested is False

    def test_concurrent_extracts_serialized(self, extractor_cls):
        e = extractor_cls()
        running = []
        overlap = []

        def hook():
            running.append(1)
            if len(running) > 1:
                overlap.append(True)
            time.sleep(0.05)
            running.pop()

        make_ready(e, parse_hook=hook)
        threads = [threading.Thread(target=e.extract, args=(b'%PDF',)) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        assert overlap == []


class TestCollectResult:
    def test_collect_md_and_figures(self, extractor_cls, tmp_path):
        root = tmp_path / 'paper' / 'auto'
        (root / 'images').mkdir(parents=True)
        (root / 'paper.md').write_text('# T\n![](images/f1.png)', encoding='utf-8')
        (root / 'images' / 'f1.png').write_bytes(b'\x89PNG')
        e = extractor_cls()
        doc = e._collect_result(tmp_path)
        assert doc.markdown.startswith('# T')
        assert len(doc.figures) == 1
        assert doc.figures[0].name == 'images/f1.png'
        assert doc.figures[0].mime == 'image/png'

    def test_no_md_raises(self, extractor_cls, tmp_path):
        e = extractor_cls()
        with pytest.raises(RuntimeError):
            e._collect_result(tmp_path)
