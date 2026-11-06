import unittest

from mittab.libs import pairing_alg


class TestPerfectPairing(unittest.TestCase):
    def setUp(self):
        self.calc_weight = pairing_alg.calc_weight
        self.determine_gov_opp = pairing_alg.determine_gov_opp
        self.matching = pairing_alg.mwmatching.maxWeightMatching
        pairing_alg.calc_weight = lambda *args: 0
        pairing_alg.determine_gov_opp = lambda pairs: pairs

    def tearDown(self):
        pairing_alg.calc_weight = self.calc_weight
        pairing_alg.determine_gov_opp = self.determine_gov_opp
        pairing_alg.mwmatching.maxWeightMatching = self.matching

    def test_unmatched_team_raises(self):
        pairing_alg.mwmatching.maxWeightMatching = lambda *args, **kwargs: [1, 0, -1]
        with self.assertRaises(ValueError):
            pairing_alg.perfect_pairing(['A', 'B', 'C'])

    def test_missing_team_raises(self):
        pairing_alg.mwmatching.maxWeightMatching = lambda *args, **kwargs: [1, 0]
        with self.assertRaises(ValueError):
            pairing_alg.perfect_pairing(['A', 'B', 'C', 'D'])

    def test_single_team_raises(self):
        # An edgeless graph returns no vertices, not an unmatched sentinel.
        self.assertEqual(self.matching([]), [])
        with self.assertRaises(ValueError):
            pairing_alg.perfect_pairing(['A'])

    def test_empty_bracket_is_valid(self):
        self.assertEqual(pairing_alg.perfect_pairing([]), [])

    def test_complete_matching_pairs_each_team_once(self):
        pairing_alg.mwmatching.maxWeightMatching = lambda *args, **kwargs: [2, 3, 0, 1]
        pairs = pairing_alg.perfect_pairing(['A', 'B', 'C', 'D'])
        self.assertEqual(pairs, [['A', 'C'], ['B', 'D']])
        self.assertEqual(sorted(team for pair in pairs for team in pair),
                         ['A', 'B', 'C', 'D'])
