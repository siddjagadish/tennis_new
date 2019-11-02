import requests
import numpy as np
import pandas as pd
from lxml import html
from tennis_new.fetch.tennis_explorer import helpers


class TennisExplorerParser(object):

    numeric_columns = [
        'p1_odds',
        'p2_odds',
        'p1_sets_won',
        'p2_sets_won',
    ] + ['p1_set%d' % set_idx for set_idx in range(1, 6)] + [
        'p2_set%d' % set_idx for set_idx in range(1, 6)
    ]

    def __init__(self, year, month, day):
        self.url = "https://www.tennisexplorer.com/results/?type=atp-single&year={0}&month={1}&day={2}".format(
            year,
            month,
            day
        )
        self.date = '%s-%s-%s' % (year, month, day)
        self.tree = html.fromstring(requests.get(self.url).content)
        tables = self.tree.xpath(".//table[@class='result']")
        assert len(tables) == 2, "Expected two tables, found %d" % len(tables)
        self.result_table = tables[0]
        _children = self.result_table.getchildren()
        assert len(_children) == 1
        _tbody = _children[0]
        assert _tbody.tag == 'tbody'
        self.table_rows = _tbody.getchildren()
        self.results = []

    def _process_table_row(self, tr):
        assert tr.tag == 'tr'
        row_class = tr.attrib['class']
        if row_class == 'head flags':
            self.cur_tourney_info = helpers.parse_head_flags(tr)
        elif 'bott' in row_class:
            self.cur_result = helpers.parse_bott_row(tr)
            self.cur_result.update({
                'date': self.date
            })
            self.cur_result.update(self.cur_tourney_info)
        elif 'one' in row_class or 'two' in row_class:
            self.cur_result.update(helpers.parse_nonbott_row(tr))
            self.results.append(self.cur_result)

    def process(self):
        for row in self.table_rows:
            self._process_table_row(row)

    @staticmethod
    def validate_df(res_df):
        if not (res_df['p1_sets_won'] > res_df['p2_sets_won']).all():
            raise ValueError(
                "P1 should always have won more sets than P2, not the case in rows %s" % str(
                    np.where(res_df['p2_sets_won'] >= res_df['p1_sets_won'])
                )
            )
        if not res_df['p1_name'].notnull().all():
            raise ValueError(
                "Missing Some P1 Names"
            )
        if not res_df['p2_name'].notnull().all():
            raise ValueError(
                "Missing Some P2 Names"
            )
        if not res_df['p1_link'].notnull().all():
            raise ValueError(
                "Missing Some P1 Links"
            )
        if not res_df['p2_link'].notnull().all():
            raise ValueError(
                "Missing Some P2 Links"
            )

    def to_df(self):
        res_df = pd.DataFrame(self.results)
        res_df.replace({'': None}, inplace=True)
        for col in self.numeric_columns:
            res_df[col] = res_df[col].astype(float)
        self.validate_df(res_df)
        return res_df
