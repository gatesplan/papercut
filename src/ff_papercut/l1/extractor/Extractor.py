import asyncio
import importlib.util
import shutil
import tempfile
import threading
from pathlib import Path

from loguru import logger

from ...l0.paperdoc import Figure, PaperDocument

MIME_MAP = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
}


# PDF -> PaperDocument 변환. MinerU 로컬 API 서버를 서브프로세스로 관리.
# 직렬 처리(객체당 동시 1건), lazy 로드, unload()=서브프로세스 종료로 VRAM/RAM 반납 보장.
class Extractor:
    def __init__(self, backend: str = 'pipeline', auto_unload: bool = False,
                 language: str = 'en', formula_enable: bool = True,
                 table_enable: bool = True):
        if importlib.util.find_spec('mineru') is None:
            raise ImportError(
                "mineru가 설치되어 있지 않다. pip install 'ff-papercut[extract]' 또는 pip install mineru")
        self.backend = backend
        self.auto_unload = auto_unload
        self.language = language
        self.formula_enable = formula_enable
        self.table_enable = table_enable
        # _job_lock: 추출 직렬화(작업 큐 역할), _state_lock: 서버/카운터 상태 전이 보호
        self._job_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._server = None
        self._base_url = None
        self._active = 0
        self._unload_requested = False
        logger.info(f"Extractor 생성: backend={backend}, auto_unload={auto_unload}")

    def extract(self, pdf: bytes | str | Path) -> PaperDocument:
        pdf_bytes = self._read_input(pdf)
        with self._state_lock:
            self._active += 1
        try:
            with self._job_lock:
                self._ensure_server()
                return self._parse(pdf_bytes)
        finally:
            with self._state_lock:
                self._active -= 1
                if self._active == 0 and (self.auto_unload or self._unload_requested):
                    self._stop_server_locked()
                    self._unload_requested = False

    def unload(self) -> None:
        # 진행 중 작업이 있으면 예약, 없으면 즉시 서버 종료
        with self._state_lock:
            if self._active > 0:
                self._unload_requested = True
                logger.info("작업 진행 중이라 unload를 예약했다")
                return
            self._stop_server_locked()

    def _read_input(self, pdf: bytes | str | Path) -> bytes:
        if isinstance(pdf, bytes):
            return pdf
        if isinstance(pdf, (str, Path)):
            path = Path(pdf)
            if not path.is_file():
                raise FileNotFoundError(f"파일이 없다: {path}")
            return path.read_bytes()
        raise TypeError("pdf는 bytes 또는 경로여야 한다")

    def _ensure_server(self) -> None:
        # lazy 로드: 첫 extract 시 mineru-api 서브프로세스 기동
        with self._state_lock:
            if self._base_url is not None:
                return
        from mineru.cli import api_client
        logger.info("MinerU 로컬 API 서버 기동 중")
        server = api_client.LocalAPIServer()
        server.start()
        base_url = asyncio.run(self._wait_ready(api_client, server))
        with self._state_lock:
            self._server = server
            self._base_url = base_url
        logger.info(f"MinerU 서버 준비 완료: {base_url}")

    async def _wait_ready(self, api_client, server):
        import httpx
        async with httpx.AsyncClient(timeout=api_client.build_http_timeout(),
                                     follow_redirects=True) as client:
            health = await api_client.wait_for_local_api_ready(client, server)
            return health.base_url

    def _parse(self, pdf_bytes: bytes) -> PaperDocument:
        from mineru.cli import api_client
        work_dir = Path(tempfile.mkdtemp(prefix='ff-papercut-'))
        try:
            pdf_path = work_dir / 'paper.pdf'
            pdf_path.write_bytes(pdf_bytes)
            form_data = api_client.build_parse_request_form_data(
                lang_list=[self.language],
                backend=self.backend,
                parse_method='auto',
                formula_enable=self.formula_enable,
                table_enable=self.table_enable,
                server_url=None,
                start_page_id=0,
                end_page_id=None,
                return_md=True,
                return_middle_json=False,
                return_model_output=False,
                return_content_list=False,
                return_images=True,
                response_format_zip=True,
                return_original_file=False,
            )
            assets = [api_client.UploadAsset(path=pdf_path, upload_name='paper.pdf')]
            submit = api_client.submit_parse_task_sync(self._base_url, assets, form_data)
            logger.info(f"추출 작업 제출: task_id={submit.task_id}")
            zip_path = asyncio.run(self._wait_and_download(api_client, submit))
            out_dir = work_dir / 'result'
            out_dir.mkdir()
            api_client.safe_extract_zip(zip_path, out_dir)
            return self._collect_result(out_dir)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    async def _wait_and_download(self, api_client, submit) -> Path:
        import httpx
        async with httpx.AsyncClient(timeout=api_client.build_http_timeout(),
                                     follow_redirects=True) as client:
            await api_client.wait_for_task_result(
                client=client, submit_response=submit, task_label='paper.pdf')
            return await api_client.download_result_zip(
                client=client, submit_response=submit, task_label='paper.pdf')

    def _collect_result(self, out_dir: Path) -> PaperDocument:
        # zip 내부 구조가 버전에 따라 다를 수 있어 재귀 탐색으로 방어
        md_files = sorted(out_dir.rglob('*.md'))
        if not md_files:
            raise RuntimeError("추출 결과에 markdown이 없다")
        md_file = md_files[0]
        markdown = md_file.read_text(encoding='utf-8')
        figures = []
        for path in sorted(md_file.parent.rglob('*')):
            suffix = path.suffix.lower()
            if path.is_file() and suffix in MIME_MAP:
                name = path.relative_to(md_file.parent).as_posix()
                figures.append(Figure(name=name, data=path.read_bytes(), mime=MIME_MAP[suffix]))
        logger.info(f"추출 완료: markdown {len(markdown)}자, figure {len(figures)}개")
        return PaperDocument(markdown=markdown, figures=figures)

    def _stop_server_locked(self) -> None:
        # 호출측이 _state_lock을 잡은 상태여야 한다
        if self._server is None:
            return
        logger.info("MinerU 서버 종료, 자원 반납")
        self._server.stop()
        self._server = None
        self._base_url = None
