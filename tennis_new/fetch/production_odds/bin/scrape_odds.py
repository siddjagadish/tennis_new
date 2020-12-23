import os
import pandas as pd
from datetime import datetime
from tennis_new.fetch.production_odds.bet_online_scraper import BetOnlineScraper
from tennis_new.infra.defs import REPO_DIR
from time import sleep

WRITE_PREFIX = os.path.join(REPO_DIR, 'fetch/production_odds/stored_data/')
ITF_URL = 'https://betonline.ag/sportsbook/tennis/itf'
EXHIBITION_URL = 'https://betonline.ag/sportsbook/tennis/exhibition'

SLEEP_INTERVAL = 10  # Wait 10 seconds between attempts
MAX_ATTEMPTS = 10


def main():
    itf_success = False
    itf_n_attempts = 0
    while not itf_success and itf_n_attempts <= MAX_ATTEMPTS:
        try:
            print("Sleeping %d seconds between attempts at ITF Scraping..." % SLEEP_INTERVAL)
            sleep(SLEEP_INTERVAL)
            itf_scraper = BetOnlineScraper(ITF_URL)
            itf_data = itf_scraper.scrape()
            itf_data['data_type'] = 'itf'
            itf_success = True
            itf_n_attempts += 1
        except:
            pass

    exhibition_success = False
    exhibition_n_attempts = 0
    while not exhibition_success and exhibition_n_attempts <= MAX_ATTEMPTS:
        try:
            print("Sleeping %d seconds between attempts at Exhibition Scraping..." % SLEEP_INTERVAL)
            sleep(SLEEP_INTERVAL)
            exhibition_scraper = BetOnlineScraper(EXHIBITION_URL)
            exhibition_data = exhibition_scraper.scrape()
            exhibition_data['data_type'] = 'exhibition'
            exhibition_success = True
            exhibition_n_attempts += 1
        except:
            pass

    all_data = pd.concat([itf_data, exhibition_data])
    assert all_data.shape[0] == itf_data.shape[0] + exhibition_data.shape[0]
    assert all_data.shape[1] == itf_data.shape[1] == exhibition_data.shape[1]
    all_data.to_csv(
        os.path.join(WRITE_PREFIX, 'bet_online_odds_%s.csv' % datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S")),
        index=False
    )


if __name__ == '__main__':
    main()
