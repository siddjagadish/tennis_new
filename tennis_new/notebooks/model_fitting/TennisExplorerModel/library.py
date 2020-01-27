import pandas as pd


# Filters
def missing_score_error(df):
    return (
        df['p1_sets_won'].isnull() |
        df['p2_sets_won'].isnull()
    )

def possible_walkover(df):
    return (
        (df['p1_sets_won'] == 1) &
        df['p1_set1'].isnull()
    )

def retirement(df):
    return (
        (df['p1_sets_won'] == 1) &
        df['p1_set1'].notnull()
    )

def missing_pids(df):
    return (
        df['p1_link'].isnull() |
        df['p2_link'].isnull()
    )


def get_test_set(df, test_min='2011-01-01', test_max='2015-01-01', test_surface=None, filter_walkovers=True):
    date_cond = (
        (df['date'] >= test_min) &
        (df['date'] < test_max)
    )
    if test_surface is None:
        surface_cond = True
    else:
        surface_cond = df['surface'] == test_surface
    cond = date_cond & surface_cond
    if filter_walkovers:
        cond &= (~possible_walkover(df))
    return df[cond]


def eval_mod(mod, df, test_min='2011-01-01', test_max='2015-01-01', test_surface=None, filter_walkovers=False):
    history_df = pd.DataFrame(mod.history)
    test_set = get_test_set(
        df,
        test_min=test_min,
        test_max=test_max,
        test_surface=test_surface,
        filter_walkovers=filter_walkovers
    )
    test_set = pd.merge(test_set, history_df, left_on='match_link', right_on='match_id')

    accuracy = (test_set['elo_match_prediction'] > 0.5).mean()
    w_odds = test_set[
        test_set['p1_odds'].notnull() &
        test_set['p2_odds'].notnull() &
        (test_set['p1_odds'] != test_set['p2_odds'])
    ]
    n_w_odds = w_odds.shape[0]
    odds_accuracy = (w_odds['p1_odds'] < w_odds['p2_odds']).mean()
    mod_odds_accuracy = (w_odds['elo_match_prediction'] > 0.5).mean()
    return {
        'overall_accuracy': accuracy,
        'odds_accuracy': odds_accuracy,
        'model_odds_accuracy': mod_odds_accuracy,
        'n_w_odds': n_w_odds
    }
