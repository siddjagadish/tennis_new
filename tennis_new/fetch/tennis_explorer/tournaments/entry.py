import click
import os
import pandas as pd
from time import sleep
from tennis_new.fetch.tennis_explorer.tournaments.scraper import TennisExplorerTourneyParser
from tennis_new.fetch.tennis_explorer.defs import ALL_MATCH_PATH, ERROR_FILE


ERROR_SLEEP_SECONDS = 10


def scrape_tourneys(overwrite=False, verbose=True, wait_time=0):
    cur_matches = pd.read_csv(ALL_MATCH_PATH)
    if (not overwrite) and os.path.exists(TennisExplorerTourneyParser.path):
        cur_tourneys = pd.read_csv(
            TennisExplorerTourneyParser.path,
            names=TennisExplorerTourneyParser.column_names
        )['tourney_link']
        assert cur_tourneys.value_counts().max() == 1
        print("Found %d existing tournaments" % cur_tourneys.shape[0])
    else:
        cur_tourneys = []
    missing_tourneys = cur_matches['tourney_link'][~cur_matches['tourney_link'].isin(cur_tourneys)].dropna().unique()
    for tourney in missing_tourneys:
        if verbose:
            print("Processing tourney %s..." % tourney)
        try:
            tp = TennisExplorerTourneyParser(tourney)
            tp.write()
        except:
            with open(ERROR_FILE, 'a') as wr:
                wr.write("Could not parse tourney: %s\n" % tourney)
                print("Error on %s, sleeping for %d seconds..." % (tourney, ERROR_SLEEP_SECONDS))
            sleep(ERROR_SLEEP_SECONDS)
        print("Waiting %d seconds..." % wait_time)
        sleep(wait_time)


@click.command()
@click.option('--overwrite', default=False)
@click.option('--verbose', default=True)
@click.option('--wait-time', default=0, prompt='Wait Time(s)')
def _scrape_tourneys(overwrite, verbose, wait_time):
    scrape_tourneys(overwrite=overwrite, verbose=verbose, wait_time=wait_time)


if __name__ == '__main__':
    _scrape_tourneys()
