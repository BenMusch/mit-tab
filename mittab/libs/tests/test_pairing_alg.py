import unittest

from mock import Mock, patch

from mittab.libs import pairing_alg


class TestPairingWeights(unittest.TestCase):
    def setUp(self):
        settings = patch.object(pairing_alg, 'TabSettings')
        self.settings = settings.start()
        self.addCleanup(settings.stop)
        self.settings.objects.all.return_value = []
        logic = patch.object(pairing_alg, 'tab_logic')
        self.logic = logic.start()
        self.addCleanup(logic.stop)
        self.logic.num_opps.return_value = 0
        self.logic.num_govs.return_value = 0
        self.logic.hit_pull_up.return_value = False
        self.logic.hit_before.return_value = False
        self.logic.tot_wins.side_effect = lambda team: team.wins
        self.a = Mock(seed=1, school='A', wins=2)
        self.b = Mock(seed=1, school='B', wins=1)

    def weight(self):
        return pairing_alg.calc_weight(
            self.a, self.b, 0, 1, self.b, self.a, 1, 0)

    def test_default_reason_penalties(self):
        self.assertEqual(self.weight(), 0)
        self.logic.num_opps.return_value = 3
        self.assertEqual(self.weight(), 0)  # Ten times zero remains zero.
        self.logic.num_opps.return_value = 4
        self.assertEqual(self.weight(), -100)
        self.logic.num_opps.return_value = 0
        self.logic.num_govs.return_value = 3
        self.assertEqual(self.weight(), -1000)
        self.logic.num_govs.return_value = 0
        self.b.school = self.a.school
        self.assertEqual(self.weight(), -10000)
        self.b.school = 'B'
        self.logic.hit_pull_up.return_value = True
        self.assertEqual(self.weight(), -100000)
        self.logic.hit_pull_up.return_value = False
        self.logic.hit_before.return_value = True
        self.assertEqual(self.weight(), -1000000)

    def test_explicit_settings_override_defaults(self):
        for key, expected in [('high_opp_penalty', -7),
                              ('higher_opp_penalty', -11),
                              ('high_gov_penalty', -13),
                              ('same_school_penalty', -17),
                              ('hit_pull_up_before', -19),
                              ('hit_team_before', -23)]:
            self.settings.objects.all.return_value = [Mock(key=key, value=expected)]
            self.logic.num_opps.return_value = 4
            self.logic.num_govs.return_value = 3
            self.b.school = self.a.school
            self.logic.hit_pull_up.return_value = True
            self.logic.hit_before.return_value = True
            defaults = -100 - 1000 - 10000 - 100000 - 1000000
            old_default = dict(high_opp_penalty=0, higher_opp_penalty=-100,
                               high_gov_penalty=-1000, same_school_penalty=-10000,
                               hit_pull_up_before=-100000, hit_team_before=-1000000)
            self.assertEqual(self.weight(), defaults - old_default[key] + expected)

    def test_invalid_setting_uses_default(self):
        self.settings.objects.all.return_value = [
            Mock(key='hit_team_before', value='invalid')]
        self.logic.hit_before.return_value = True
        self.assertEqual(self.weight(), -1000000)

    def test_power_pairing_distance_is_unchanged(self):
        self.a.seed = 5
        self.assertEqual(pairing_alg.calc_weight(
            self.a, self.b, 0, 3, self.a, self.b, 0, 3), -4)
        self.settings.objects.all.return_value = [Mock(key='cur_round', value=2)]
        self.assertEqual(pairing_alg.calc_weight(
            self.a, self.b, 0, 3, self.a, self.b, 0, 3), -3)
