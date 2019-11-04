import requests
import pandas as pd
from lxml import html
from pathlib import Path
from tennis_new.fetch.tennis_explorer import helpers
from tennis_new.fetch.tennis_explorer.defs import DATA_PATH


class TennisExplorerTourneyParser(object):

    prefix = "https://www.tennisexplorer.com/"
    path = Path.joinpath(
        DATA_PATH,
        'tourney_summary.csv',
    )
    column_names=['tourney_link', 'details']

    def __init__(self, url):
        self.url = url
        url_to_try = ('%s%s' % (self.prefix, self.url))
        self.tree = html.fromstring(requests.get(url_to_try).content)
        details_elems = self.tree.xpath(".//div[@class='box boxBasic lGray']")
        assert len(details_elems) == 3
        details_elem = details_elems[1]
        self.details = helpers._text(details_elem)  # TODO: Rename _text to public method

    def to_df(self):
        return pd.DataFrame({
            'tourney_link': [self.url],
            'details': [self.details]
        })

    def write(self):
        self.to_df().to_csv(self.path, mode='a', header=False, index=False)
