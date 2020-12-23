import cloudscraper
import pandas as pd
from datetime import datetime
from lxml import html


class BetOnlineScraper(object):
    # TODO: Sanity Checking
    # TODO: Get this to run at a cadence on a remote machine

    P1_COLUMN_NAME_MAPPING = {
        'col_time bdevtt': 'time',
        'col_rotno bdevtt': 'rotation_no',
        'col_teamname bdevtt': 'player_name',
        'odds bdevtt moneylineodds displayOdds': 'money_line'
    }
    P2_COLUMN_NAME_MAPPING = {k: v for k, v in P1_COLUMN_NAME_MAPPING.items() if
                              k != 'col_time bdevtt'}  # This key doesn't exist for p2

    def __init__(self, url):
        self.url = url
        self.scraper = cloudscraper.create_scraper()
        self.page_content = self.scraper.get(self.url).text
        self.tree = html.fromstring(self.page_content)

    def process_match(self, p1, p2):
        out_d = {}
        for k, v in self.P1_COLUMN_NAME_MAPPING.items():
            out_d['p1_%s' % v] = p1.xpath("./td[@class='%s']" % k)[0].text
        for k, v in self.P2_COLUMN_NAME_MAPPING.items():
            out_d['p2_%s' % v] = p2.xpath("./td[@class='%s']" % k)[0].text
        # Sanity Checks
        if pd.isnull(out_d['p1_rotation_no']) or pd.isnull(out_d['p2_rotation_no']):
            raise ValueError("Null rotation number")
        elif int(out_d['p1_rotation_no']) + 1 != int(out_d['p2_rotation_no']):
            raise ValueError("Nonconsecutive rotation numbers")
        return out_d

    def scrape(self):
        p1s = self.tree.xpath(".//tr[@class='h2hSeq firstline']")
        p2s = self.tree.xpath(".//tr[@class='otherline']")
        if len(p1s) != len(p2s):
            raise ValueError("At least one match does not have an opponent")
        if len(p1s) == 0:
            raise ValueError("No matches found")
        out = pd.DataFrame([self.process_match(p1, p2) for p1, p2 in zip(p1s, p2s)])
        out.rename(columns={'p1_time': 'scraped_match_time'}, inplace=True)
        for c in ['p1_money_line', 'p2_money_line']:
            out[c] = out[c].astype(int)
        out['date_scraped'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        return out
