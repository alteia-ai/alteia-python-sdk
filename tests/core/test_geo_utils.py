from alteia.core.errors import BoundingBoxError
from alteia.core.utils.geo_utils import compute_bbox, compute_bbox_as_polygon
from tests.alteiatest import AlteiaTestBase


class TestGeoUtils(AlteiaTestBase):
    def test_compute_bbox(self):
        with self.assertRaises(BoundingBoxError):
            compute_bbox([])

        coordinates = [
            [1.0177519166666666, 44.03104722222222],
            [1.017777222222222, 44.03101111111111],
            [1.0177857222222222, 44.030974916666665],
            [1.0177871944444445, 44.030924166666665],
            [1.017757388888889, 44.030880277777776],
        ]

        bbox = compute_bbox(coordinates)

        self.assertIsNotNone(bbox)

        self.assertEqual(len(bbox), 4)

        self.assertEqual(bbox[0], 1.0177519166666666)
        self.assertEqual(bbox[1], 1.0177871944444445)
        self.assertEqual(bbox[2], 44.030880277777776)
        self.assertEqual(bbox[3], 44.03104722222222)

    def test_compute_bbox_as_polygon(self):
        with self.assertRaises(BoundingBoxError):
            compute_bbox_as_polygon([])

        coordinates = [
            [1.0177519166666666, 44.03104722222222],
            [1.017777222222222, 44.03101111111111],
            [1.0177857222222222, 44.030974916666665],
            [1.0177871944444445, 44.030924166666665],
            [1.017757388888889, 44.030880277777776],
        ]

        bbox = compute_bbox_as_polygon(coordinates)

        self.assertIsNotNone(bbox)

        self.assertEqual(len(bbox), 5)

        self.assertEqual(bbox[0][0], 1.0177519166666666)
        self.assertEqual(bbox[0][1], 44.030880277777776)
        self.assertEqual(bbox[1][0], 1.0177871944444445)
        self.assertEqual(bbox[1][1], 44.030880277777776)
        self.assertEqual(bbox[2][0], 1.0177871944444445)
        self.assertEqual(bbox[2][1], 44.03104722222222)
        self.assertEqual(bbox[3][0], 1.0177519166666666)
        self.assertEqual(bbox[3][1], 44.03104722222222)
        self.assertEqual(bbox[4][0], 1.0177519166666666)
        self.assertEqual(bbox[4][1], 44.030880277777776)
