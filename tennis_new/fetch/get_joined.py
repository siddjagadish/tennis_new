# TODO: Augment data with manual fixes where necessary
# For example, Sydney tournament 1975-338 is missing the tournament month

import os
import pandas as pd
from tennis_new.fetch.defs import STORED_DATA_PATH


REL_MATCH_SCORE_COLUMNS = [
    'match_id',
    'tourney_year_id',
    'loser_player_id',
    'winner_player_id',
    'loser_games_won',
    'winner_games_won',
    'loser_sets_won',
    'winner_sets_won',
    'match_score_tiebreaks'
]
EXCEPTION_MATCH_SCORE_COLS = [  # Columns that are allowed to be null
    'match_score_tiebreaks'
]


REL_TOURNEY_COLUMNS = [
    'tourney_year',
    'tourney_month',
    'tourney_day',
    'tourney_surface',
]


def _fetch_data_for_type(dt):
    return pd.read_csv(
        os.path.join(
            STORED_DATA_PATH, dt, 'combined.csv'
        ),
        sep=',',
    )


def main():
    match_scores = _fetch_data_for_type('match_scores')
    for col in set(REL_MATCH_SCORE_COLUMNS) - set(EXCEPTION_MATCH_SCORE_COLS):
        if not match_scores[col].notnull().all():
            raise ValueError("Column %s has unallowable null values" % col)
    match_scores['tourney_year'] = match_scores['tourney_year_id'].astype('|S80').map(
        lambda x: x[:4]
    ).astype(int)

    # Remove some tournaments where vital information is missing
    tourney_data = _fetch_data_for_type('tournaments')
    for col in REL_TOURNEY_COLUMNS:
        _n_to_remove = tourney_data[col].isnull().sum()
        print("Removing %d rows with null values for %s" % (_n_to_remove, col))
        tourney_data = tourney_data[tourney_data[col].notnull()]

    # Join tournaments and match_scores
    non_tourney_columns = list(set(match_scores.columns) - set(tourney_data.columns)) + ['tourney_year', 'tourney_order']
    together = pd.merge(
        match_scores[non_tourney_columns],
        tourney_data,
        on=['tourney_year', 'tourney_order']
    )

    together.to_csv(
        os.path.join(STORED_DATA_PATH, 'joined.tsv'),
        sep='\t', index=False
    )


if __name__ == '__main__':
    main()
