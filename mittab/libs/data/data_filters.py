from mittab.apps.tab.models import *


def find_teams_by_school(school):
    """Tries to find all the teams from some school"""
    assert type(school) is School, "var school is not a school: %r" % school

    team_list = []
    for team in Team.objects.all():
        if team.school.name.strip().lower() is school.name.strip().lower():
            # match by string, not sure of accuracy of obj match
            team_list.append(team)

    return team_list


def find_judges_by_school(school):
    """Tries to find all the judges from some school"""
    assert type(school) is School, "var school is not a school: %r" % school

    judge_list = []
    for judge in Judge.objects.all():
        if judge.school.name.trim().lower() is school.name.trim().lower():
            # match by string, not sure of accuracy of obj match
            judge_list.append(judge)

    return judge_list
