"""
Dataset File uploader.
"""
import concurrent.futures as cf
import functools
import logging
import math
import os

from enum import Enum
from types import SimpleNamespace
from typing import List, Optional, Tuple
from urllib.parse import urlencode
from urllib3.response import HTTPResponse

from alteia.apis.provider import Provider
from alteia.core.connection.connection import Connection
from alteia.core.errors import UploadError
from alteia.core.utils.typing import AnyPath, DictAny, ResourceId, DictStr
from alteia.core.utils.utils import human_bytes, md5, md5_from_blob
from alteia.core.resources.datamngt.upload import (
    S3_CHUNK_MAX_PARTS,
    S3_CHUNK_MIN_SIZE,
    S3_CHUNK_MAX_SIZE,
    DM_CHUNK_MAX_SIZE,
    MultipartUpload as LegacyMultipartUpload,
)

DEFAULT_CHUNK_SIZE = 10 * 1024 ** 2  # 10MiB
USE_LEGACY_UPLOADER = os.getenv('USE_LEGACY_UPLOADER', 'no').lower() in ('yes', 'true', '1')

LOGGER = logging.getLogger(__name__)


def assert_chunk_size(chunk_size: int, use_legacy_uploader: bool = USE_LEGACY_UPLOADER):
    """Assert that the wanted chunk_size is in the good range.

    Args:
         chunk_size: Size of the uploaded parts.

         use_legacy_uploader: Boolean to specify if the assertion should
            check range of legacy uploader (default: False).

    Raises:
        ValueError: when chunk_size is outside the authorized range
    """
    if chunk_size < S3_CHUNK_MIN_SIZE:
        raise ValueError(
            f'Chunk size must be >= {human_bytes(S3_CHUNK_MIN_SIZE)}; '
            f'received : {human_bytes(chunk_size)}'
        )
    if chunk_size > S3_CHUNK_MAX_SIZE:
        raise ValueError(
            f'Chunk size must be <= {human_bytes(S3_CHUNK_MAX_SIZE)}; '
            f'received : {human_bytes(chunk_size)}'
        )
    if use_legacy_uploader and chunk_size > DM_CHUNK_MAX_SIZE:
        raise ValueError(
            f'Chunk size must be <= {human_bytes(DM_CHUNK_MAX_SIZE)}; '
            f'received : {human_bytes(chunk_size)}'
        )


class PartStatus(Enum):
    PENDING = 'pending'
    PREUPLOAD = 'preupload'
    AVAILABLE = 'available'
    FAILED = 'failed'


class UploadPart:
    """Store the state of the upload of a file part (it's a chunk of the file)
    Mainly taken from legacy Chunk class
    """
    def __init__(self, index: int, *, part_number: int, size: int,
                 status: PartStatus = PartStatus.PENDING):
        self.index: int = index
        self.part_number: int = part_number
        self.size: int = size
        self.status: PartStatus = status
        self.attempt = 0
        self.req: Optional[cf.Future] = None
        self.error: Optional[str] = None
        self.put_url: Optional[str] = None
        self.put_headers: Optional[str] = None
        self.md5hash: Optional[str] = None

    def __str__(self):
        req = self.req if self.req is not None else '<unknown>'
        return f'UploadPart {self.part_number}: {self.size} {self.status} {self.attempt} {req}'


class DatasetUploadElement(SimpleNamespace):
    """Abstract class to store the Key of a dataset element to upload,
    and the routes needed to upload this kind of element.
    """
    # routes for single-part upload
    CREATE_ROUTE = ''
    COMPLETE_ROUTE = ''
    DM_UPLOAD_ROUTE = ''  # for legacy upload

    # routes for multi-part upload
    CREATE_MULTIPART_ROUTE = 'create-multipart-upload'
    GET_PART_ROUTE = 'get-upload-part-url'
    COMPLETE_MULTIPART_ROUTE = 'complete-multipart-upload'

    dataset: ResourceId

    def __init__(self, *, dataset: ResourceId, **kwargs):
        if not self.CREATE_ROUTE:
            raise RuntimeError(f'{self.__class__} must have a valid CREATE_ROUTE')
        if not self.DM_UPLOAD_ROUTE:
            raise RuntimeError(f'{self.__class__} must have a valid legacy DM_UPLOAD_ROUTE')
        if len(kwargs) == 0:
            raise RuntimeError(f'{self.__class__} must have another information than dataset')

        super().__init__(dataset=dataset, **kwargs)

    def value(self) -> DictStr:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def legacy_value(self, for_multipart=False) -> DictStr:
        """To reimplement in each inherited class if needed"""
        return self.value()


class DatasetUploadComponent(DatasetUploadElement):
    """Class to store the Key of a dataset component to upload,
    and the routes needed to upload components.
    """
    CREATE_ROUTE = 'init-upload-component'
    COMPLETE_ROUTE = 'complete-upload-component'
    DM_UPLOAD_ROUTE = 'upload-component'

    component: str

    def __init__(self, *, dataset: ResourceId, component: str):
        super().__init__(dataset=dataset, component=component)

    def legacy_value(self, for_multipart=False) -> DictStr:
        if for_multipart:
            return {'dataset': self.dataset, 'component_name': self.component}
        return self.value()


class DatasetUploader:
    """Main entry class to upload a dataset file.
    This class can use direct-upload method or legacy upload method.
    The legacy upload method uploads through the data-manager.

    For both methods, it can be a single-part upload or a multipart,
    depending on the provided chunk_size.
    """
    LegacyMultipartUploadClass = LegacyMultipartUpload

    _provider: Provider
    _connection: Connection
    _chunks: List[UploadPart]
    _chunk_size: int

    use_legacy_uploader: bool
    use_multipart: bool
    chunk_size: int

    upload_element: DatasetUploadElement
    filename: str
    file_path: AnyPath
    file_size: int
    md5hash: str

    def __init__(self, provider: Provider,
                 use_multipart: bool = True,
                 chunk_size: int = None,
                 use_legacy_uploader: bool = None):
        """
        Args:
            provider: DataManagement provider

            use_multipart: Set ``True`` if you allow to use multipart upload. Note that it can
                be automatically set to ``True`` or ``False`` depending on file size.
                Less than ``S3_CHUNK_MIN_SIZE`` or ``chunk_size``: ``False``.
                Greater than ``S3_CHUNK_MAX_SIZE``: ``True``. (Default: ``True``)

            chunk_size: Size of the future uploaded parts
                (Default: value of ``DEFAULT_CHUNK_SIZE``).

            use_legacy_uploader: Set to ``True`` to upload through the legacy uploader.
                (Default: ``False``). Using ``True`` will reduce the authorized range
                of the chunk_size. Legacy upload method is limited to ``DM_CHUNK_MAX_SIZE``.

        Raises:
            ValueError: when chunk_size is outside the authorized range
        """
        self._provider = provider
        self._connection = provider._connection  # shortcut

        if isinstance(use_legacy_uploader, bool):
            self.use_legacy_uploader = use_legacy_uploader
        else:
            self.use_legacy_uploader = USE_LEGACY_UPLOADER

        self.use_multipart = use_multipart
        chunk_size = chunk_size or DEFAULT_CHUNK_SIZE
        assert_chunk_size(chunk_size, self.use_legacy_uploader)
        self.chunk_size = chunk_size  # wanted
        self._chunks = []

    def check_for_multipart(self, file_path: AnyPath) -> bool:
        """Calculate and prepare all data required to perform multipart or not.
        Mainly taken from both prepare_chunks() and cfg_multipart_upload() legacy methods.

        Args:
            file_path: The path of the file to upload.

        Raises:
            ValueError: when chunk_size is outside the authorized range
        """
        file_path = str(file_path)
        if not os.path.exists(file_path):
            raise UploadError(f'File not found "{file_path}"')

        file_size = os.path.getsize(file_path)
        if file_size <= 0:
            raise UploadError('Expecting a positive file size')

        self.file_path = file_path
        self.file_size = file_size

        if self.use_multipart is False:
            # no multipart required if not wanted and file size is less than the max allowed
            max_allowed = DM_CHUNK_MAX_SIZE if self.use_legacy_uploader else S3_CHUNK_MAX_SIZE
            if file_size < max_allowed:
                return self.use_multipart  # here is False

        chunk_size = self.chunk_size or DEFAULT_CHUNK_SIZE
        chunk_size = max(chunk_size, S3_CHUNK_MIN_SIZE)
        chunk_size = min(chunk_size, S3_CHUNK_MAX_SIZE)
        if self.use_legacy_uploader:
            chunk_size = min(chunk_size, DM_CHUNK_MAX_SIZE)

        nb_parts = max(0, math.ceil(file_size / chunk_size))
        if nb_parts > S3_CHUNK_MAX_PARTS:
            # too many parts: adapt the chunk size and recheck it.
            LOGGER.warning(f'Too many chunks with chunk size = {human_bytes(chunk_size)}, '
                           f'for file size = {human_bytes(file_size)}')
            chunk_size = math.ceil(file_size / S3_CHUNK_MAX_PARTS)
            nb_parts = math.ceil(file_size / chunk_size)
            LOGGER.info(f'New chunk size = {human_bytes(chunk_size)}, '
                        f'with {nb_parts} chunks')
            assert_chunk_size(chunk_size, self.use_legacy_uploader)

        self._chunk_size = chunk_size

        if nb_parts == 1 or file_size <= chunk_size:
            self.use_multipart = False
        else:
            self.use_multipart = True
            parts = []
            for index in range(nb_parts):
                size = min(chunk_size, file_size - index * chunk_size)
                part_number = index + 1
                chunk = UploadPart(index, part_number=part_number, size=size)
                parts.append(chunk)
            self._chunks = parts

        return self.use_multipart

    def send(self, file_path: AnyPath, *,
             dataset: ResourceId, component: str, md5hash: str = None):
        """Entrypoint to upload a component file.

        Args:
            file_path: The path of the file to upload.

            dataset: Identifier of the dataset to upload to.

            component: Name of component to upload to.

            md5hash: Optional MD5 hash of the file to upload, read in
                binary mode and containing only 32 hexadecimal digits.
                Will be computed when equal to None (the default).
        """
        # creating the element key for the component, this key will be used on every call
        element = DatasetUploadComponent(dataset=dataset, component=component)
        self._send(file_path, element=element, md5hash=md5hash)

    def _send(self, file_path: AnyPath, *, element: DatasetUploadElement, md5hash: str = None):
        self.upload_element = element
        self.check_for_multipart(file_path)
        self.filename = os.path.basename(file_path)
        self.md5hash = md5hash or md5(self.file_path)

        # 4 choices here: (legacy or not) x (multipart or not)
        if self.use_legacy_uploader:
            if self.use_multipart:
                self._do_legacy_multipart_upload()
            else:
                self._do_legacy_singlepart_upload()
        else:
            if self.use_multipart:
                self._do_multipart_upload()
            else:
                self._do_singlepart_upload()

    # ########################################################## #
    # Legacy uploads                                             #
    # ########################################################## #

    def _do_legacy_singlepart_upload(self):
        """legacy upload for singlepart.
        """
        LOGGER.debug(f'Perform singlepart legacy upload for {self.upload_element}')

        query_str = urlencode({
            'filename': self.filename,
            'checksum': self.md5hash,
            **self.upload_element.legacy_value(for_multipart=False),
        })
        with open(self.file_path, 'rb') as f:
            self._provider.post(
                f'{self.upload_element.DM_UPLOAD_ROUTE}?{query_str}',
                data=f.read(),
                as_json=False, sanitize=False, serialize=False,
            )

    def _do_legacy_multipart_upload(self):
        """legacy upload for multipart.
        It uses the LegacyMultipartUploadClass.

        Some parameters must be renamed to work with legacy methods.
        """
        LOGGER.debug(f'Perform multipart legacy upload for {self.upload_element}')

        conn = self._connection
        url = self._provider._root_path
        MultipartUploadClass = self.LegacyMultipartUploadClass
        MultipartUploadClass(conn, url, chunk_size=self._chunk_size).send(
            self.file_path,
            md5hash=self.md5hash,
            **self.upload_element.legacy_value(for_multipart=True),
        )

    # ########################################################## #
    # New single-part upload                                     #
    # ########################################################## #

    def _do_singlepart_upload(self):
        LOGGER.debug(f'Perform singlepart upload for {self.upload_element}')
        if self.upload_element.CREATE_ROUTE is None:
            raise UploadError(f'Missing routes on upload element: {self.upload_element}')

        # 1. retrieve the signed upload url
        result: DictAny = self._provider.post(self.upload_element.CREATE_ROUTE, data={
            'filename': self.filename,
            'checksum': self.md5hash,
            **self.upload_element.value(),  # exploding the key
        })
        put_url: str = result.get('put_url')
        put_headers: DictStr = result.get('headers') or {}

        # 2. Perform direct upload through the signed url, with PUT method
        with open(self.file_path, 'rb') as f:
            self._connection.external_request(
                'PUT', put_url, body=f.read(), headers=put_headers,
            )

        # 3. mark the element as upload if needed (if a complete_route exists)
        if self.upload_element.COMPLETE_ROUTE:
            self._provider.post(self.upload_element.COMPLETE_ROUTE, data={
                **self.upload_element.value(),
            })

    # ########################################################## #
    # New multipart upload: main steps                           #
    # ########################################################## #

    def _do_multipart_upload(self):
        LOGGER.debug(f'Perform multipart upload for {self.upload_element}')

        # 1. initialized the multipart upload for the element
        create_body = {
            'filename': self.filename,
            'chunk_size': self._chunk_size,
            'total_size': self.file_size,
            'direct_upload': True,
            **self.upload_element.value(),  # exploding the key
        }
        if self.md5hash:
            create_body['checksum'] = self.md5hash
        resp: DictAny = self._provider.post(self.upload_element.CREATE_MULTIPART_ROUTE,
                                            data=create_body)
        LOGGER.debug(f'Multipart upload initialized with total parts of {resp["total_parts"]}')

        # 2. upload all parts
        self._do_upload_parts()

        # 3. complete the multipart upload for the element
        complete_body = {
            **self.upload_element.value(),
        }
        self._provider.post(self.upload_element.COMPLETE_MULTIPART_ROUTE, data=complete_body)

    # ####################################################################### #
    # New multipart upload: loop on chunks. Mainly taken from legacy class.   #
    # ####################################################################### #

    @property
    def _ongoing_chunks(self) -> List[UploadPart]:
        return [c for c in self._chunks
                if c.status == PartStatus.PENDING and c.req is not None and not c.req.done()]

    @property
    def _unfinished_chunks(self) -> List[UploadPart]:
        return [c for c in self._chunks
                if c.status not in (PartStatus.AVAILABLE, PartStatus.FAILED)]

    @property
    def _waiting_chunks(self) -> List[UploadPart]:
        return [c for c in self._chunks
                if c.status not in (PartStatus.AVAILABLE, PartStatus.FAILED) and c.req is None]

    def _get_upload_part_data(self, part_number: int, md5hash: str = None) -> Tuple[str, dict]:
        """Call the provider to get an upload signed URL (+ headers) for a part"""
        data: DictAny = {
            **self.upload_element.value(),
            'part_number': part_number,
        }
        if md5hash:
            data['checksum'] = str(md5hash)
        result = self._provider.post(self.upload_element.GET_PART_ROUTE, data=data)
        put_url = result['put_url']
        put_headers = result.get('headers', {})
        return put_url, put_headers

    def _do_upload_parts(self):
        async_conn = self._connection.asynchronous
        max_simultaneous = async_conn.max_request_workers

        def update_part(part: UploadPart, resp: HTTPResponse):
            if resp.status in (200, 204):
                part.status = PartStatus.AVAILABLE
            elif resp.status == 401 and part.attempt == 1:
                part.status = PartStatus.PREUPLOAD if part.put_url else PartStatus.PENDING
            else:
                part.status = PartStatus.FAILED
                part.error = resp.data
            part.req = None

        request_delay = self._connection.request_timeout

        with open(self.file_path, 'rb') as st:
            while len(self._unfinished_chunks) > 0:
                # limit the number of simultaneous enqueued requests, use the max of:
                # - Queue.qsize() is the "approximate size" of the queue (not reliable!)"
                # - self._ongoing_chunks must be all the unfinished requests
                queued_requests = async_conn.executor._work_queue.qsize()
                if max(queued_requests, len(self._ongoing_chunks)) >= max_simultaneous:
                    reqs = [c.req for c in self._ongoing_chunks]
                    cf.wait(reqs, timeout=request_delay, return_when=cf.FIRST_COMPLETED)
                    continue

                # check whether all chunks have been sent
                candidates = self._waiting_chunks
                if len(candidates) == 0:
                    break

                # send first candidate
                chunk = candidates[0]
                chunk.attempt += 1

                offset = chunk.index * self._chunk_size
                st.seek(offset)
                blob = st.read(chunk.size)
                if not chunk.md5hash:
                    chunk.md5hash = md5_from_blob(blob)
                if not chunk.put_url:
                    put_url, put_headers = self._get_upload_part_data(
                        part_number=chunk.part_number,
                        md5hash=chunk.md5hash,
                    )
                    chunk.put_url = put_url
                    chunk.put_headers = put_headers

                cb = functools.partial(update_part, chunk)
                chunk.req = async_conn.external_request(
                    'PUT', chunk.put_url, body=blob, headers=put_headers, callback=cb,
                )

            reqs = [c.req for c in self._ongoing_chunks]
            try:
                all(cf.as_completed(reqs, timeout=len(reqs) * request_delay))
            except cf.TimeoutError:
                LOGGER.warning('Timeout while waiting for chunk uploads to end')

        if any(map(lambda ch: ch.status != PartStatus.AVAILABLE, self._chunks)):
            raise UploadError('Failed to upload some chunks')
