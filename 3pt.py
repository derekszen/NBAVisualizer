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
print(__version__)


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

def get_eFG(playerid, season = 'all'):
    shotTracking = nba_py.player.PlayerShotTracking(playerid, season)
    efG = (shotTracking['FGM'].sum() + (0.5 * shotTracking['FG3M'].sum()))/shotTracking['FGA'].sum()
    return eFG

def get_custom_boxscore(roster_id):
    game_logs  = nba_py.team.TeamGameLogs(roster_id)

    df_game_logs = game_logs.info()

    df_game_logs['GAME_DATE'] =  pd.to_datetime(df_game_logs['GAME_DATE'])
    df_game_logs['days_rest'] =  df_game_logs['GAME_DATE'] - df_game_logs['GAME_DATE'].shift(-1)
    df_game_logs['days_rest'] =  df_game_logs['days_rest'].astype('timedelta64[D]')

    ##Just like before, that should get us the gamelogs we need and the rest days column

    ##Now to loop through the list of dates for our other stats

    ##Build up a  dataframe of our custom stats and join that to the gamelogs instead of joining  each individual row

    df_all =pd.DataFrame() ##blank dataframe

    dates = df_game_logs['GAME_DATE']

    for date in dates:

        game_info = nba_py.team.TeamPassTracking(roster_id,  date_from=date, date_to=date).passes_made()
        game_info['GAME_DATE'] = date ## We need to append the date to this so we can  join back

        temp_df = game_info.groupby(['GAME_DATE']).sum()
        temp_df.reset_index(level =  0,  inplace =  True)

        ##now to get the shot info. For the most part, we're just reusing code we've already written
        open_info = nba_py.team.TeamShotTracking(roster_id,date_from =date,  date_to =  date).closest_defender_shooting()
        open_info['OPEN'] = open_info['CLOSE_DEF_DIST_RANGE'].map(lambda x: True if 'Open' in x else False)

        temp_df['OPEN_SHOTS'] = open_info.loc[open_info['OPEN'] == True, 'FGA'].sum()
        temp_df['COVERED_SHOTS'] = open_info.loc[open_info['OPEN'] == False, 'FGA'].sum()

        if open_info.loc[open_info['OPEN']== True, 'FGA'].sum() > 0:
            temp_df['OPEN_EFG']= (open_info.loc[open_info['OPEN']== True, 'FGM'].sum() + (.5 * open_info.loc[open_info['OPEN']== True, 'FG3M'].sum()))/(open_info.loc[open_info['OPEN']== True, 'FGA'].sum())
        else:
            temp_df['OPEN_EFG'] = 0

        if open_info.loc[open_info['OPEN']== False, 'FGA'].sum() > 0:
             temp_df['COVER_EFG']= (open_info.loc[open_info['OPEN']== False, 'FGM'].sum() + (.5 * open_info.loc[open_info['OPEN']== False, 'FG3M'].sum()))/(open_info.loc[open_info['OPEN']== False, 'FGA'].sum())
        else:
            temp_df['COVER_EFG'] = 0
        ##append this to our bigger dataframe

        df_all = df_all.append(temp_df)

    df_boxscore =  pd.merge(df_game_logs, df_all[['PASS', 'FG2M', 'FG2_PCT', 'OPEN_SHOTS','COVERED_SHOTS', 'OPEN_EFG', 'COVER_EFG']], how = 'left', left_on = df_game_logs['GAME_DATE'], right_on = df_all['GAME_DATE'])
    df_boxscore['PASS_ASSIST'] = df_boxscore['PASS'] /  df_boxscore['AST']
    df_boxscore['RESULT'] = df_boxscore['WL'].map(lambda x: 1 if 'W' in x else 0 )

    return df_boxscore


def main(qux, foo=1, bar=2):
    print("Foo: {}\nBar: {}\nQux: {}".format(foo, bar, qux))
    pp = pprint.PrettyPrinter(indent=4)

    name = foo.split()
    playerID = nba_py.player.get_player(name[0], last_name = name[-1])
    rockets_shots = nba_py.team.TeamShotTracking(rockets_id, last_n_games = 82)

    player_playoff_performance = get_player_playoff_performance(playerID)
    player_reg_performance = get_player_regular_performance(playerID)
    print("---------Playoff player---------")
    pp.pprint(player_playoff_performance)

    print("---------Regular Season player---------")
    pp.pprint(player_reg_performance)

    # How many open shots?
    print("---------Total Open team_shots---------")
    custom_boxscore = get_custom_boxscore(rockets_id)
    custom_boxscore.head()
    print("---------Playoff-reg diff shooting---------")


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
