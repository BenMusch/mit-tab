from unittest import TestCase

from mock import patch

from mittab.libs import errors, pairing_alg


class TestPerfectPairing(TestCase):
    def setUp(self):
        # Team identities suffice here: history and weights are independent
        # inputs, while the real matching algorithm is exercised below.
        self.teams = [object() for _ in range(4)]
        self.previous_matchups = set()
        self.history = patch.object(
            pairing_alg.tab_logic, 'hit_before',
            side_effect=lambda a, b: frozenset([a, b]) in self.previous_matchups)
        self.weight = patch.object(pairing_alg, 'calc_weight', return_value=0)
        self.sides = patch.object(pairing_alg, 'determine_gov_opp',
                                  side_effect=lambda pairs: pairs)
        for patcher in (self.history, self.weight, self.sides):
            patcher.start()
            self.addCleanup(patcher.stop)

    def assert_complete_legal_pairing(self, pairs, teams):
        paired_teams = [team for pair in pairs for team in pair]
        self.assertEqual(len(paired_teams), len(teams))
        self.assertEqual(set(paired_teams), set(teams))
        for pair in pairs:
            self.assertNotIn(frozenset(pair), self.previous_matchups)

    def test_empty_bracket(self):
        self.assertEqual(pairing_alg.perfect_pairing([]), [])

    def test_first_round(self):
        pairs = pairing_alg.perfect_pairing(self.teams)
        self.assert_complete_legal_pairing(pairs, self.teams)

    def test_repeat_is_excluded_even_when_it_would_have_best_weight(self):
        self.previous_matchups.add(frozenset(self.teams[:2]))
        pairing_alg.calc_weight.side_effect = (
            lambda a, b, *args: 1000000 if frozenset([a, b])
            in self.previous_matchups else -1000000)
        pairs = pairing_alg.perfect_pairing(self.teams)
        self.assert_complete_legal_pairing(pairs, self.teams)
        for call in pairing_alg.calc_weight.call_args_list:
            self.assertNotIn(frozenset(call[0][:2]), self.previous_matchups)

    def test_only_possible_matchup_is_a_repeat(self):
        self.previous_matchups.add(frozenset(self.teams[:2]))
        with self.assertRaises(errors.PairingError):
            pairing_alg.perfect_pairing(self.teams[:2])

    def test_isolated_trailing_team_is_not_silently_omitted(self):
        for team in self.teams[:-1]:
            self.previous_matchups.add(frozenset([team, self.teams[-1]]))
        with self.assertRaises(errors.PairingError):
            pairing_alg.perfect_pairing(self.teams)

    def test_full_length_matching_with_unmatched_teams_is_rejected(self):
        # Legal edges form a star: all vertices occur in the graph, but only
        # one edge can be chosen, leaving -1 mates in the matching result.
        for i in range(1, len(self.teams)):
            for j in range(1, i):
                self.previous_matchups.add(
                    frozenset([self.teams[i], self.teams[j]]))
        with self.assertRaises(errors.PairingError):
            pairing_alg.perfect_pairing(self.teams)
