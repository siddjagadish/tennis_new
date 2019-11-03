import glob
import pandas as pd
from pathlib import Path
# from tennis_new.fetch.tennis_explorer.tournaments.scraper import  TennisExplorerTourneyParser
from tennis_new.fetch.tennis_explorer.defs import DATA_PATH, JD_PATH


def get_joined_from_dailies():
    # TODO: Incorporate Tournament Information
    match_results_path = Path.joinpath(DATA_PATH, 'match_results')
    all_match = pd.concat([pd.read_csv(x) for x in glob.glob('%s/*.csv' % match_results_path)])
    all_match.to_csv(JD_PATH, index=False)
