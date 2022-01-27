from unittest import TestCase

from alteia.core.utils.requests import (extract_filename_from_headers,
                                        generate_raster_tiles_url,
                                        generate_vector_tiles_url)

RASTER_TILES_URL_TEMPLATE = 'https://app.alteia.com/' \
    'tileserver/tiles/5d0b9952e8d1d25df4c1dd62/{z}/{x}/{y}.png' \
    '?access_token=FAKE_ACCESS_TOKEN'

VECTOR_TILES_URL_TEMPLATE = 'https://app.alteia.com/' \
    'map-service/features/collection-mvt/' \
    '5d0b9952e8d1d25df4c1dd62/{z}/{x}/{y}.pbf' \
    '?access_token=FAKE_ACCESS_TOKEN'


class RequestsUtilsTests(TestCase):
    def test_extract_filename_from_headers(self):
        headers = {'content-disposition': 'attachment; filename=Raster1'}
        self.assertEqual('Raster1', extract_filename_from_headers(headers))

        headers = {
            'content-disposition': 'attachment; filename="Theta__NFC.csv";  filename*=UTF-8\'\'Theta_%CE%98_NFC.csv'
        }
        self.assertEqual('Theta_Θ_NFC.csv', extract_filename_from_headers(headers))

        with self.assertRaises(KeyError):
            self.assertIsNone(extract_filename_from_headers({}))

        with self.assertRaises(TypeError):
            self.assertIsNone(extract_filename_from_headers(None))

        with self.assertRaises(TypeError):
            self.assertIsNone(extract_filename_from_headers('filename=myfile'))

    def test_generate_raster_tiles_url(self):
        url = generate_raster_tiles_url('https://app.alteia.com',
                                        'FAKE_ACCESS_TOKEN',
                                        '5d0b9952e8d1d25df4c1dd62',
                                        'png')
        self.assertEqual(url, RASTER_TILES_URL_TEMPLATE)

    def test_generate_vector_tiles_url(self):
        url = generate_vector_tiles_url('https://app.alteia.com',
                                        'FAKE_ACCESS_TOKEN',
                                        '5d0b9952e8d1d25df4c1dd62',
                                        'pbf')
        self.assertEqual(url, VECTOR_TILES_URL_TEMPLATE)
