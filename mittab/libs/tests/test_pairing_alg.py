import unittest

from mittab.libs import pairing_alg


class TestPerfectPairing(unittest.TestCase):
    def setUp(self):
        self.original_weight = pairing_alg.calc_weight
        self.original_sides = pairing_alg.determine_gov_opp
        self.original_matching = pairing_alg.mwmatching.maxWeightMatching
        pairing_alg.calc_weight = lambda *args: 0
        pairing_alg.determine_gov_opp = lambda pairs: pairs

    def tearDown(self):
        pairing_alg.calc_weight = self.original_weight
        pairing_alg.determine_gov_opp = self.original_sides
        pairing_alg.mwmatching.maxWeightMatching = self.original_matching

    def test_odd_team_counts_are_rejected_before_matching(self):
        def unexpected_matching(*args, **kwargs):
            self.fail('Odd team counts should be rejected before matching')
        pairing_alg.mwmatching.maxWeightMatching = unexpected_matching
        for count in (1, 3, 5):
            self.assertRaises(ValueError, pairing_alg.perfect_pairing,
                              [object() for _ in range(count)])

    def test_empty_pairing(self):
        self.assertEqual(pairing_alg.perfect_pairing([]), [])

    def test_every_team_is_paired_exactly_once(self):
        for count in (2, 4, 6):
            teams = [object() for _ in range(count)]
            pairs = pairing_alg.perfect_pairing(teams)
            paired_teams = [team for pair in pairs for team in pair]
            self.assertEqual(len(paired_teams), count)
            for team in teams:
                self.assertEqual(paired_teams.count(team), 1)

    def test_unmatched_team_is_rejected(self):
        pairing_alg.mwmatching.maxWeightMatching = lambda *a, **kw: [1, 0, -1, -1]
        self.assertRaises(ValueError, pairing_alg.perfect_pairing,
                          [object() for _ in range(4)])

    def test_truncated_matching_is_rejected(self):
        pairing_alg.mwmatching.maxWeightMatching = lambda *a, **kw: [1, 0]
        self.assertRaises(ValueError, pairing_alg.perfect_pairing,
                          [object() for _ in range(4)])
