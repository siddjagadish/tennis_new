import os
import pandas as pd
from pathlib import Path
from tennis_new.fetch.atp_api.defs import API_RESULTS_DIR
from tennis_new.fetch.defs import STORED_DATA_PATH


JD_PATH = Path.joinpath(STORED_DATA_PATH, 'joined.tsv')


def filter_ineligible(jd):
    print("Filtering Ineligible Matches...")
    return jd[jd['loser_id'].notnull()]


def add_derived_signals(jd):
    pass


def combine_files(atp_files, challenger_files):
    print("Reading files...")
    atp_dfs = []
    challenger_dfs = []
    for f in atp_files:
        cur_df = pd.read_csv(f)
        cur_df['year'] = int(str(f)[-8:-4])  # TODO: Move to def rather than hardcode
        atp_dfs.append(cur_df)
    for f in challenger_files:
        cur_df = pd.read_csv(f)
        cur_df['year'] = int(str(f)[-8:-4])  # TODO: Move to def rather than hardcode
        challenger_dfs.append(cur_df)
    atp_df = pd.concat(atp_dfs)
    challenger_df = pd.concat(challenger_dfs)
    atp_df['tour_type'] = 'atp'
    challenger_df['tour_type'] = 'challenger'
    print("Concatenation...")
    return pd.concat([atp_df, challenger_df])


def amalgamate_years():
    print("Getting File Names...")
    res_path = Path.joinpath(API_RESULTS_DIR, 'updated_api_results')
    files = os.listdir(res_path)
    atp = [Path.joinpath(res_path, x) for x in files if 'challenger' not in x]
    challenger = [Path.joinpath(res_path, x) for x in files if 'challenger' in x]
    return combine_files(atp, challenger)


def add_match_id(jd):
    jd['match_id'] = (
        jd['winner_name'].fillna('W') + '*' +
        jd['loser_name'].fillna('L') + '*' +
        jd['tourney_year_id'].fillna('tourney_year_id') + '*' +
        jd['round'].fillna('round')
    )


def write_joined(jd):
    print("Writing out...")
    jd.to_csv(JD_PATH, index=False, sep='\t')


def sort_joined(jd):
    jd.sort_values(
        ['tourney_dates', 'round_order'],
        ascending=[True, False],
        inplace=True
    )


def get_joined_from_yearly_files():
    jd = amalgamate_years()
    add_match_id(jd)
    sort_joined(jd)
    jd.drop_duplicates('match_id', keep='last', inplace=True)
    add_derived_signals(jd)
    jd = filter_ineligible(jd)
    write_joined(jd)


def read_joined():
    return pd.read_csv(JD_PATH, sep='\t')
