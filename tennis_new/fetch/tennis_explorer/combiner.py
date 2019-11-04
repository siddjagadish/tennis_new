import glob
import pandas as pd
from pathlib import Path
# from tennis_new.fetch.tennis_explorer.tournaments.scraper import  TennisExplorerTourneyParser
from tennis_new.fetch.tennis_explorer.defs import DATA_PATH, ALL_MATCH_PATH
from tennis_new.fetch.tennis_explorer.tournaments.entry import scrape_tourneys


def get_match_file_from_dailies():
    # TODO: Incorporate Tournament Information
    match_results_path = Path.joinpath(DATA_PATH, 'match_results')
    all_match = pd.concat([pd.read_csv(x) for x in glob.glob('%s/*.csv' % match_results_path)])
    all_match.to_csv(ALL_MATCH_PATH, index=False)


def get_joined(rewrite_match_file=False):
    if rewrite_match_file:
        get_match_file_from_dailies()
    else:
        matches = pd.read_csv(ALL_MATCH_PATH)
    scrape_tourneys(overwrite=False, verbose=True)  # Tourney scraping uses match tourney links to know what to scrape
    # TODO: Parse Tourneys
    # TODO: Join Tourneys to match data
