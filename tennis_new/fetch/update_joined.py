from datetime import datetime
from pathlib import Path
import pandas as pd
from tennis_new.fetch.atp_api.defs import API_RESULTS_DIR
from tennis_new.fetch.get_joined import (
    add_match_id,
    combine_files,
    filter_ineligible,
    read_joined,
    sort_joined,
    write_joined
)
from tennis_new.fetch.atp_api.scrapers.updated_scraper.updated_scraper import scrape_years


def scrape_current_year(year):
    scrape_years(str(year), str(year + 1))


def _read_current_year(year):
    current_year_file = Path.joinpath(
        API_RESULTS_DIR,
        'updated_api_results',
        'match_results_%s.csv' % str(year)
    )
    current_year_challenger_file = Path.joinpath(
        API_RESULTS_DIR,
        'updated_api_results',
        'match_results_challenger_%s.csv' % str(year)
    )
    return combine_files([current_year_file], [current_year_challenger_file])


def update_joined_with_year(cur_year):
    current_year = _read_current_year(cur_year)
    add_match_id(current_year)
    jd = read_joined()
    new_jd = pd.concat([jd, current_year], sort=True)
    sort_joined(new_jd)
    new_jd.drop_duplicates('match_id', keep='last', inplace=True)
    new_jd = filter_ineligible(new_jd)
    return new_jd


def update_joined():
    cur_year = datetime.today().year
    scrape_current_year(cur_year)
    jd = update_joined_with_year(cur_year)
    write_joined(jd)


if __name__ == '__main__':
    update_joined()
