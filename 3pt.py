import argparse
from functools import reduce
import pprint
import nba_py.player
import nba_py.team
import requests
import pandas as pd
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout

#Print plotly version
print __version__


rockets_id = 1610612745
# Current player, CP3 planned
player_stats = {'name':None,'avg_dribbles':None,'avg_touch_time':None,'avg_shot_distance':None,'avg_defender_distance':None}


def get_player_playoff_performance(playerid):
    score_diff = nba_py.player.PlayerPerformanceSplits(playerid, season_type = 'Playoffs').score_differential()
    passing = nba_py.player.PlayerPassTracking(playerid, season_type = 'Playoffs')
    shooting =  nba_py.player.PlayerShotTracking(playerid, season_type = 'Playoffs').general_shooting()
    defense = nba_py.player.PlayerDefenseTracking(playerid, season_type = 'Playoffs')
    return [score_diff, passing, shooting, defense]

def get_player_regular_performance(playerid):
    score_diff = nba_py.player.PlayerPerformanceSplits(playerid, season_type = 'Regular Season').score_differential()
    passing = nba_py.player.PlayerPassTracking(playerid, season_type = 'Regular Season')
    shooting =  nba_py.player.PlayerShotTracking(playerid, season_type = 'Regular Season').general_shooting()
    defense = nba_py.player.PlayerDefenseTracking(playerid, season_type = 'Regular Season')
    return [score_diff, passing, shooting, defense]

def main(qux, foo=1, bar=2):
    print("Foo: {}\nBar: {}\nQux: {}".format(foo, bar, qux))
    pp = pprint.PrettyPrinter(indent=4)
    name = foo.split()
    playerID = nba_py.player.get_player(name[0], last_name = name[-1])
    rockets_shots = nba_py.team.TeamShotTracking(rockets_id, last_n_games = 82)
    pp.pprint(rockets_shots.dribble_shooting())
    player_playoff_performance = get_player_playoff_performance(playerID)
    player_reg_performance = get_player_regular_performance(playerID)
    print("---------Playoff player---------")
    pp.pprint(player_playoff_performance)

    print("---------Regular Season player---------")
    pp.pprint(player_reg_performance)

    # How many open shots?
    print("---------Total Open team_shots---------")
    defended = rockets_shots.closest_defender_shooting()
    # Create new column
    defended['OPEN'] = defended['CLOSE_DEF_DIST_RANGE'].map(lambda x: True if 'Open' in x else False)
    open_shots = defended.loc[defended['OPEN'] == True, 'FGA'].sum()
    print('Open shots: %s', open_shots)

    covered_shots = defended['FGA'].sum() - open_shots
    #covered_shots = defended.loc[defended['OPEN'] == False, 'FGA'].sum()
    print('Covered shots: %s', covered_shots)

    print("---------Playoff-reg diff score-diff---------")


    return



def _cli():
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            argument_default=argparse.SUPPRESS)
    parser.add_argument('-n', '--foo', help="This is the playername argument")
    parser.add_argument('-b', '--bar', help="This is the bar argument")
    qux_help = ("This argument will show its default in the help due to "
                "ArgumentDefaultsHelpFormatter")
    parser.add_argument('-q', '--qux', default=3, help=qux_help)
    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    main(**_cli())
