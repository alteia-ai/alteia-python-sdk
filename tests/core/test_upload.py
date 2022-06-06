"""Test utilities related to upload.

"""

from unittest import TestCase

from alteia.core.resources.datamngt.upload import cfg_multipart_upload, S3_CHUNK_MIN_SIZE, S3_CHUNK_MAX_PARTS, \
    S3_CHUNK_MAX_SIZE, DM_CHUNK_MAX_SIZE


class UploadTest(TestCase):
    """Test Upload related utilities.

    """
    def test_cfg_multipart_upload(self):
        """Test configure multipart upload."""
        multipart, chunk_size = cfg_multipart_upload(1024)
        self.assertFalse(multipart)

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MIN_SIZE/1024**2*1000**2)
        self.assertFalse(multipart)

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MIN_SIZE)
        self.assertFalse(multipart)

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MIN_SIZE + 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, S3_CHUNK_MIN_SIZE)

        multipart, chunk_size = cfg_multipart_upload(10 * S3_CHUNK_MIN_SIZE + 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, S3_CHUNK_MIN_SIZE)

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MAX_PARTS * S3_CHUNK_MIN_SIZE + 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, 5242881)

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MAX_PARTS * DM_CHUNK_MAX_SIZE + 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, min(S3_CHUNK_MAX_SIZE, DM_CHUNK_MAX_SIZE))

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MAX_PARTS * S3_CHUNK_MAX_SIZE + 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, min(S3_CHUNK_MAX_SIZE, DM_CHUNK_MAX_SIZE))

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MAX_PARTS * DM_CHUNK_MAX_SIZE - 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, min(S3_CHUNK_MAX_SIZE, DM_CHUNK_MAX_SIZE))

        multipart, chunk_size = cfg_multipart_upload(S3_CHUNK_MAX_PARTS * S3_CHUNK_MAX_SIZE - 1)
        self.assertTrue(multipart)
        self.assertEqual(chunk_size, min(S3_CHUNK_MAX_SIZE, DM_CHUNK_MAX_SIZE))