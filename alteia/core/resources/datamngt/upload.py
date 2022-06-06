"""Files uploader.

"""

import concurrent.futures as cf
import functools
import hashlib
import json
import logging
import math
import os
import urllib
from typing import Optional, Tuple

from alteia.core.connection.abstract_connection import DEFAULT_REQUESTS_TIMEOUT
from alteia.core.errors import UploadError
from alteia.core.utils.typing import AnyPath
from alteia.core.utils.utils import human_bytes

LOGGER = logging.getLogger(__name__)

# Minimal chunk size for multipart upload on AWS S3 (in bytes),
# last part can be any size > 0
S3_CHUNK_MAX_PARTS = 10000
S3_CHUNK_MIN_SIZE = 5 * 1024 ** 2  # cannot be less than 5MB (S3)
S3_CHUNK_MAX_SIZE = 5 * 1024 ** 3  # cannot be more than 5GB (S3)
DM_CHUNK_MAX_SIZE = 50 * 1024 ** 2  # data-manager limit: 50MB max


def cfg_multipart_upload(file_size, multipart: bool = True, chunk_size: int = None) -> Tuple[bool, int]:
    """Configure multipart upload.

    Args:
        file_size: byte size of the file
        multipart: Optional bool to enable/disable multipart upload
        chunk_size: Optional target size in byte of each part for a multipart upload.
        Must stay within backend limitations (storage provider and Data-Manager).

    Returns:
        multipart
        chunk_size
    """
    chunk_size = max(chunk_size or math.ceil(file_size / S3_CHUNK_MAX_PARTS), S3_CHUNK_MIN_SIZE)
    chunk_size = min(chunk_size, S3_CHUNK_MAX_SIZE, DM_CHUNK_MAX_SIZE)

    # Only last chunk can have a size < to S3_CHUNK_MIN_SIZE, but > 0
    if file_size <= chunk_size:
        multipart = False
    return multipart, chunk_size


class Chunk:
    """Store the state of the upload of a file chunk.

    """
    def __init__(self, index, *, size, status='preupload'):
        self.index = index
        self.size = size
        self.status = status
        self.attempt = 0
        self.req = None

    def __str__(self):
        template = 'Chunk {index}: {size} {status} {attempt} {req}'
        req_maybe = self.req if self.req is not None else '<unknown>'
        return template.format(index=self.index,
                               size=self.size,
                               status=self.status,
                               attempt=self.attempt,
                               req=req_maybe)


def prepare_chunks(*, file_size: int, chunk_size: int) -> Tuple[list, int]:
    """Prepare chunks for upload of a file of given size.

    It raises a ``ValueError`` when ``chunk_size``
    or ``file_size`` is negative.

    Args:
        file_size: Size of the file to upload.

        chunk_size: Common size of the uploaded chunks.

    Returns:
        Array of ``Chunk`` instances.

    """
    if chunk_size <= 0:
        raise ValueError('Expecting a positive chunk size')

    if file_size <= 0:
        raise ValueError('Expecting a positive file size')

    chunk_count = max(0, math.ceil(file_size / chunk_size))
    if chunk_count > S3_CHUNK_MAX_PARTS:
        LOGGER.warning(f'Too many chunks with chunk size = {human_bytes(chunk_size)}, '
                       f'for file size = {human_bytes(file_size)}')
        chunk_size = math.ceil(file_size / S3_CHUNK_MAX_PARTS)
        chunk_count = math.ceil(file_size / chunk_size)
        LOGGER.info(f'New chunk size = {human_bytes(chunk_size)}, '
                    f'with {chunk_count} chunks')
    chunks = []
    if chunk_count > 0:
        for index in range(chunk_count):
            size = min(chunk_size, file_size - index * chunk_size)
            chunk = Chunk(index, size=size)
            chunks.append(chunk)
    return chunks, chunk_size


class MultipartUpload:
    """Send a given file in multiple requests.

    It raises a ``ValueError`` when ``chunk_size`` is < _S3_CHUNK_MIN_SIZE.

    """
    def __init__(self, connection, base_url, *, chunk_size=S3_CHUNK_MIN_SIZE):
        if chunk_size < S3_CHUNK_MIN_SIZE:
            raise ValueError(
                f'Chunk size must be >= {human_bytes(S3_CHUNK_MIN_SIZE)}; '
                f'received : {human_bytes(chunk_size)}'
            )
        max_size = min(DM_CHUNK_MAX_SIZE, S3_CHUNK_MAX_SIZE)
        if chunk_size > max_size:
            raise ValueError(
                f'Chunk size must be <= {human_bytes(max_size)}; '
                f'received : {human_bytes(chunk_size)}'
            )

        self._base_url = base_url
        self._chunk_size = chunk_size
        self._connection = connection

        # updated through send() calls
        self._chunks = []

    @property
    def creation_url(self):
        return f'{self._base_url}/create-multipart-upload'

    def get_upload_part_url(self, *, dataset: str,
                            component_name: str, part_number: int,
                            checksum: str) -> str:
        if part_number < 1:
            raise ValueError(
                f'part_number must be >=1; received : {part_number}'
            )

        url_template = '{}/upload-part?{}'
        qs = urllib.parse.urlencode({'dataset': dataset,
                                     'component': component_name,
                                     'part_number': part_number,
                                     'checksum': checksum})
        return url_template.format(self._base_url, qs)

    @property
    def completion_url(self):
        return f'{self._base_url}/complete-multipart-upload'

    @property
    def _ongoing_chunks(self):
        return [c for c in self._chunks
                if c.status == 'preupload' and c.req is not None
                and not c.req.done()]

    @property
    def _unfinished_chunks(self):
        return [c for c in self._chunks
                if c.status not in ('available', 'failed')]

    @property
    def _waiting_chunks(self):
        return [c for c in self._chunks
                if c.status not in ('available', 'failed') and c.req is None]

    def send(self, file_path: AnyPath, *,
             dataset: str, component_name: str, md5hash: Optional[str] = None):
        """Send a file in multiple requests.

        It raises ``UploadError`` in case of failure.

        Args:
            file_path: Path to the file to upload.

            dataset: Unique identifier of dataset.

            component_name: Name of component to upload to.

            md5hash: Optional MD5 hash of the file to upload read in
                binary mode and containing only hexadecimal digits.
                Will be computed when equal to None (the default).

        """
        file_path = str(file_path)
        if not os.path.exists(file_path):
            raise UploadError(f'File not found "{file_path}"')

        file_size = os.path.getsize(file_path)
        params = {'file_path': file_path,
                  'dataset': dataset,
                  'component_name': component_name}
        try:
            self._chunks, self._chunk_size = prepare_chunks(file_size=file_size,
                                                            chunk_size=self._chunk_size)

            self._create(md5hash=md5hash, **params)
            self._start(**params)
            self._complete(**params)
        except Exception as e:
            self._chunks = []
            raise e

    def _create(self, *, file_path: str, dataset: str, component_name: str,
                md5hash: Optional[str] = None):
        headers = {'Cache-Control': 'no-cache',
                   'Content-Type': 'application/json'}
        src_file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        creation_desc = {'dataset': dataset,
                         'component': component_name,
                         'filename': src_file_name,
                         'chunk_size': self._chunk_size,
                         'total_size': file_size}
        if md5hash is not None:
            creation_desc.update({'checksum': md5hash})

        self._connection.post(path=self.creation_url,
                              headers=headers,
                              data=json.dumps(creation_desc))

    def _start(self, *, file_path: str, dataset: str, component_name: str):
        async_conn = self._connection.asynchronous
        max_simultaneous = async_conn.max_request_workers

        def update_chunk(chunk, resp):
            if resp.status == 200:
                chunk.status = 'available'
            elif resp.status == 401 and chunk.attempt == 1:
                chunk.status = 'preupload'
            else:
                chunk.status = 'failed'
            chunk.req = None

        request_delay = DEFAULT_REQUESTS_TIMEOUT
        upload_part_headers = {'Cache-Control': 'no-cache',
                               'Content-Type': 'application/octet-stream'}
        with open(file_path, 'rb') as st:
            while len(self._unfinished_chunks) > 0:
                # limit the number of simultaneous enqueued requests
                queued_requests = async_conn.executor._work_queue.qsize()
                if queued_requests >= max_simultaneous:
                    reqs = [c.req for c in self._ongoing_chunks]
                    cf.wait(reqs, timeout=request_delay,
                            return_when=cf.FIRST_COMPLETED)
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
                algo = hashlib.md5()
                algo.update(blob)
                md5hash = algo.hexdigest()
                # chunk.index must start at 0 to get the proper file offset
                # however, part_number must start at 1 (S3 requirement)
                path = self.get_upload_part_url(dataset=dataset,
                                                component_name=component_name,
                                                part_number=chunk.index+1,
                                                checksum=md5hash)
                cb = functools.partial(update_chunk, chunk)
                chunk.req = async_conn.post(path=path,
                                            headers=upload_part_headers,
                                            data=blob,
                                            callback=cb)

            reqs = [c.req for c in self._ongoing_chunks]
            try:
                all(cf.as_completed(reqs, timeout=len(reqs) * request_delay))
            except cf.TimeoutError:
                LOGGER.warning('Timeout while waiting for chunk uploads '
                               'to end')

        if any(map(lambda ch: ch.status != 'available', self._chunks)):
            raise UploadError('Failed to upload some chunks')

    def _complete(self, *, file_path: str, dataset: str, component_name: str):
        headers = {'Cache-Control': 'no-cache',
                   'Content-Type': 'application/json'}
        completion_desc = {'dataset': dataset,
                           'component': component_name}
        self._connection.post(path=self.completion_url,
                              headers=headers,
                              data=json.dumps(completion_desc))
