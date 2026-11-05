import unittest

from mock import Mock, patch

from mittab.libs import errors, pairing_alg


class TestSchoolPairings(unittest.TestCase):
    def setUp(self):
        self.school = Mock()
        self.school.__str__ = Mock(return_value='School A')
        self.teams = [Mock(name='team_a'), Mock(name='team_b')]
        for index, team in enumerate(self.teams):
            team.name = 'Team %s' % index
            team.school = self.school
            team.seed = 0

    @patch.object(pairing_alg, 'calc_weight', return_value=0)
    def test_same_school_pair_raises(self, calc_weight):
        with self.assertRaises(errors.SameSchoolPairingError) as caught:
            pairing_alg.perfect_pairing(self.teams)
        self.assertIn('Team 0', str(caught.exception))
        self.assertIn('Team 1', str(caught.exception))
        self.assertIn('School A', str(caught.exception))

    @patch.object(pairing_alg.tab_logic, 'num_govs', return_value=0)
    @patch.object(pairing_alg.tab_logic, 'num_opps', return_value=0)
    @patch.object(pairing_alg, 'calc_weight', return_value=0)
    def test_different_schools_still_pair(self, *mocks):
        self.teams[1].school = Mock()
        pairs = pairing_alg.perfect_pairing(self.teams)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(set(pairs[0]), set(self.teams))

    @patch.object(pairing_alg, 'calc_weight', return_value=0)
    def test_empty_bracket_still_pairs(self, calc_weight):
        self.assertEqual(pairing_alg.perfect_pairing([]), [])

    @patch.object(pairing_alg.TabSettings.objects, 'all', return_value=[])
    @patch.object(pairing_alg.tab_logic, 'hit_before', return_value=False)
    @patch.object(pairing_alg.tab_logic, 'hit_pull_up', return_value=False)
    @patch.object(pairing_alg.tab_logic, 'num_govs', return_value=0)
    @patch.object(pairing_alg.tab_logic, 'num_opps', return_value=0)
    def test_conflict_is_not_silently_repaired(self, *mocks):
        other_school = Mock()
        teams = [Mock(), Mock(), Mock(), Mock()]
        for index, team in enumerate(teams):
            team.name = 'Team %s' % index
            team.seed = 3 - index
            team.school = self.school if index in (0, 3) else other_school
        # Both ideal power pairings have conflicts, but cross-school swaps
        # exist. Report the conflict instead of silently choosing those swaps.
        with self.assertRaises(errors.SameSchoolPairingError):
            pairing_alg.perfect_pairing(teams)

    @patch.object(pairing_alg.TabSettings.objects, 'all', return_value=[])
    @patch.object(pairing_alg.tab_logic, 'hit_before', return_value=False)
    @patch.object(pairing_alg.tab_logic, 'hit_pull_up', return_value=False)
    @patch.object(pairing_alg.tab_logic, 'num_govs', return_value=0)
    @patch.object(pairing_alg.tab_logic, 'num_opps', return_value=0)
    def test_school_does_not_change_pairing_weight(self, *mocks):
        team_a, team_b = self.teams
        same_school_weight = pairing_alg.calc_weight(
            team_a, team_b, 0, 1, team_b, team_a, 1, 0)
        team_b.school = Mock()
        other_school_weight = pairing_alg.calc_weight(
            team_a, team_b, 0, 1, team_b, team_a, 1, 0)
        self.assertEqual(same_school_weight, other_school_weight)
