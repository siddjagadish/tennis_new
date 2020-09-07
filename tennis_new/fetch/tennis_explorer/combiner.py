import glob
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from tennis_new.fetch.tennis_explorer.tournaments.scraper import  TennisExplorerTourneyParser
from tennis_new.fetch.tennis_explorer.defs import DATA_PATH, ALL_MATCH_PATH, DATE_FORMAT
from tennis_new.fetch.tennis_explorer.tournaments.entry import scrape_tourneys
from tennis_new.fetch.tennis_explorer.matches.iterator import scrape_dates


JD_PATH = Path.joinpath(DATA_PATH, 'joined.csv')


def get_match_file_from_dailies():
    # Combines daily match result csvs into one big csv
    match_results_path = Path.joinpath(DATA_PATH, 'match_results')
    # TODO: Why am I getting Pandas FutureWarning in the line below?
    all_match = pd.concat([pd.read_csv(x) for x in glob.glob('%s/*.csv' % match_results_path)], axis=0)
    all_match.to_csv(ALL_MATCH_PATH, index=False)
    return all_match


def parse_details(d):
    l = d.strip('\(\)').split(',')
    [surface, sex] = map(lambda x: x.strip(), l[-2:])
    prize_money = int(''.join(l[:-2]).strip('€$').strip())  # Note we don't treat different currencies differently
    return {
        'tourney_prize_money': prize_money,
        'surface': surface,
        'sex': sex
    }


def add_derived_signals(jd):
    odds_p1_raw = 1. / jd['p1_odds']
    odds_p2_raw = 1. / jd['p2_odds']
    jd['odds_implied_probability'] = odds_p1_raw / (odds_p1_raw + odds_p2_raw)


def get_joined(rewrite_match_file=False):
    if rewrite_match_file:
        print("Writing match file from dailies...")
        matches = get_match_file_from_dailies()
    else:
        matches = pd.read_csv(ALL_MATCH_PATH)
    print("Scraping tournaments...")
    scrape_tourneys(overwrite=False, verbose=True)  # Tourney scraping uses match tourney links to know what to scrape
    tourneys = pd.read_csv(TennisExplorerTourneyParser.path, names=TennisExplorerTourneyParser.column_names)
    print("Parsing tourney details...")
    details_df = pd.DataFrame(tourneys['details'].map(parse_details).tolist())
    prior_len = tourneys.shape[0]
    tourneys = pd.concat([tourneys, details_df], axis=1)
    assert (tourneys['sex'] == 'men').all()
    assert tourneys['surface'].notnull().all()
    assert tourneys.shape[0] == prior_len
    print("Merging...")
    jd = pd.merge(matches, tourneys, on='tourney_link', how='left')
    add_derived_signals(jd)  # TODO: This is inefficient: Derives all signals on all data everyday
    print("Writing...")
    jd.to_csv(JD_PATH, index=False)


def read_joined():
    return pd.read_csv(JD_PATH)


def update_joined():
    print("Reading existing joined...")
    jd = read_joined()
    max_date = jd['date'].max()  # NOTE: This means we overwrite the last day
    print("Found max date is %s..." % max_date)
    scrape_dates(datetime.today().strftime(DATE_FORMAT), max_date, wait_time=3)
    get_joined(rewrite_match_file=True)
