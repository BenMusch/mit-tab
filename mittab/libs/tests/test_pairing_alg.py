from django.test import TestCase
from mock import patch

from mittab.apps.tab.models import TabSettings
from mittab.libs import pairing_alg


class PairingTeam(object):
    def __init__(self, seed, school):
        self.seed = seed
        self.school = school


class TestPowerPairingPenalty(TestCase):
    def setUp(self):
        TabSettings.objects.create(key='cur_round', value=1)
        TabSettings.objects.create(key='tot_rounds', value=5)

        self.patchers = [
            patch.object(pairing_alg.tab_logic, 'num_opps', return_value=0),
            patch.object(pairing_alg.tab_logic, 'num_govs', return_value=0),
            patch.object(pairing_alg.tab_logic, 'hit_pull_up', return_value=False),
            patch.object(pairing_alg.tab_logic, 'tot_wins', return_value=0),
            patch.object(pairing_alg.tab_logic, 'hit_before', return_value=False),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def calc_weight(self, current_round, team_a_seed, team_b_seed,
                    team_a_opt_seed, team_b_opt_seed, team_a_ind,
                    team_b_ind, team_a_opt_ind, team_b_opt_ind):
        TabSettings.objects.filter(key='cur_round').update(
            value=current_round)
        school_a, school_b = object(), object()
        team_a = PairingTeam(team_a_seed, school_a)
        team_b = PairingTeam(team_b_seed, school_b)
        team_a_opt = PairingTeam(team_a_opt_seed, school_a)
        team_b_opt = PairingTeam(team_b_opt_seed, school_b)
        return pairing_alg.calc_weight(
            team_a, team_b, team_a_ind, team_b_ind, team_a_opt, team_b_opt,
            team_a_opt_ind, team_b_opt_ind)

    def test_round_one_default_averages_seed_distance_and_scales_linearly(self):
        zero_deviation = self.calc_weight(1, 1, 5, 5, 1, 0, 4, 4, 0)
        one_unit = self.calc_weight(1, 1, 5, 4, 2, 0, 4, 0, 4)
        two_units = self.calc_weight(1, 1, 5, 3, 3, 0, 4, 0, 4)

        self.assertEqual(zero_deviation, 0)
        self.assertEqual(one_unit, -100)
        self.assertEqual(two_units, -200)

    def test_later_round_default_averages_position_distance_and_scales(self):
        zero_deviation = self.calc_weight(2, 1, 5, 0, 0, 1, 5, 5, 1)
        one_unit = self.calc_weight(2, 1, 5, 0, 0, 1, 5, 4, 2)
        two_units = self.calc_weight(2, 1, 5, 0, 0, 1, 7, 5, 3)

        self.assertEqual(zero_deviation, 0)
        self.assertEqual(one_unit, -100)
        self.assertEqual(two_units, -200)

    def test_configured_multiplier_overrides_default(self):
        TabSettings.objects.create(key='power_pairing_multiple', value=-7)

        weight = self.calc_weight(2, 1, 5, 0, 0, 1, 7, 5, 3)

        self.assertEqual(weight, -14)
