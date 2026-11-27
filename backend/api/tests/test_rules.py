from unittest import TestCase

from api import geo, ranking, risk


class RiskTests(TestCase):
    def test_wind_boundaries(self):
        cases = [(24.9, 0), (25, 1), (34.9, 1), (35, 2), (44.9, 2), (45, 3), (54.9, 3), (55, 4)]
        for value, level in cases:
            self.assertEqual(risk.wind_level(value), level, value)

    def test_rain_boundaries(self):
        cases = [(0.099, 0), (0.10, 1), (0.25, 2), (0.50, 3), (1.00, 3), (1.01, 4)]
        for value, level in cases:
            self.assertEqual(risk.rain_level(value), level, value)

    def test_snow_boundaries(self):
        cases = [(0.49, 0), (0.5, 1), (1.0, 2), (2.0, 3), (3.0, 3), (3.01, 4)]
        for value, level in cases:
            self.assertEqual(risk.snow_level(value), level, value)

    def test_load_rules(self):
        self.assertEqual(risk.classify(45, 0, 0, 30_000), risk.SEVERE)
        self.assertEqual(risk.classify(45, 0, 0, 30_001), risk.NO_TRAVEL)
        self.assertEqual(risk.classify(35, 0, 0, 40_000), risk.HIGH)
        self.assertEqual(risk.classify(35, 0, 0, 40_001), risk.SEVERE)
        self.assertEqual(risk.classify(55, 0, 0, 0), risk.NO_TRAVEL)


class RankingTests(TestCase):
    def test_segment_miles_add_up_to_length(self):
        self.assertEqual(ranking.segment_miles([0, 50, 80]), [25, 40, 15])

    def test_severe_miles_outrank_travel_time(self):
        fast = ranking.score([0, 50], [risk.SEVERE, risk.LOW], 1)
        safe = ranking.score([0, 50], [risk.HIGH, risk.HIGH], 9)
        self.assertEqual(ranking.rank([fast, safe]), [1, 0])

    def test_travel_time_breaks_ties(self):
        slow = ranking.score([0, 50], [0, 0], 2)
        quick = ranking.score([0, 50], [0, 0], 1)
        self.assertEqual(ranking.rank([slow, quick]), [1, 0])


class GeoTests(TestCase):
    def test_sample_includes_both_ends(self):
        samples = geo.sample([(0, 0), (0, 2)], 50)  # about 138 miles
        self.assertEqual([round(m) for m, _ in samples], [0, 50, 100, 138])

    def test_duplicates(self):
        line = [(0, 0), (0, 2)]
        self.assertTrue(geo.is_duplicate(line, line))
        self.assertFalse(geo.is_duplicate(line, [(0, 0), (1, 1), (0, 2)]))
