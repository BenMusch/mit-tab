from django.test import TestCase
from mock import Mock, patch

from mittab.apps.tab.models import TabSettings
from mittab.libs import pairing_alg


class TestPairingPenalties(TestCase):
    def setUp(self):
        self.team_a = Mock(seed=0, school='a')
        self.team_b = Mock(seed=0, school='b')
        self.logic_patch = patch.object(pairing_alg, 'tab_logic')
        self.logic = self.logic_patch.start()
        self.addCleanup(self.logic_patch.stop)
        self.logic.num_opps.return_value = 0
        self.logic.num_govs.return_value = 0
        self.logic.hit_pull_up.return_value = False
        self.logic.hit_before.return_value = False

    def weight(self):
        return pairing_alg.calc_weight(
            self.team_a, self.team_b, 0, 1,
            self.team_b, self.team_a, 1, 0)

    def test_default_penalties(self):
        self.assertEqual(self.weight(), 0)
        self.logic.num_opps.return_value = 3
        self.assertEqual(self.weight(), 0)
        self.logic.num_opps.return_value = 4
        self.assertEqual(self.weight(), -1000)
        self.logic.num_opps.return_value = 0
        self.logic.num_govs.return_value = 3
        self.assertEqual(self.weight(), -10000)
        self.logic.num_govs.return_value = 0
        self.team_b.school = 'a'
        self.assertEqual(self.weight(), -100000)
        self.team_b.school = 'b'
        self.logic.hit_pull_up.return_value = True
        self.logic.tot_wins.side_effect = lambda team: 1 if team is self.team_a else 0
        self.assertEqual(self.weight(), -1000000)
        self.logic.hit_pull_up.return_value = False
        self.logic.hit_before.return_value = True
        self.assertEqual(self.weight(), -10000000)

    def test_explicit_settings_override_defaults(self):
        self.logic.hit_before.return_value = True
        TabSettings.objects.create(key='hit_team_before', value=-17)
        self.assertEqual(self.weight(), -17)

    def test_power_pairing_baseline_is_unchanged(self):
        self.team_a.seed = 10
        self.assertEqual(pairing_alg.calc_weight(
            self.team_a, self.team_b, 0, 1,
            self.team_a, self.team_b, 0, 1), -10)
