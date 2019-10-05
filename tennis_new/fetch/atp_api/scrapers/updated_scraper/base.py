import pandas as pd
import re
import requests

from tqdm import tqdm
from lxml import html
from pathlib import Path

from tennis_new.fetch.atp_api.defs import API_RESULTS_DIR

WEIRD_RESULTS = Path.joinpath(API_RESULTS_DIR, 'weird_results.log')


def regex_strip_string(string):
    string = re.sub('\n', '', string).strip()
    string = re.sub('\r', '', string).strip()
    string = re.sub('\t', '', string).strip()
    return string


def regex_strip_array(array):
    for i in range(0, len(array)):
        array[i] = regex_strip_string(array[i]).strip()
    return array


def clean_text(to_parse, xpath_expr, unique=True):
    _x = to_parse.xpath(xpath_expr)
    if len(_x) > 1:
        raise ValueError("Expected singleton, received array of length %d" % len(_x))
    return regex_strip_string(_x[0])


class MatchResultsParser(object):
    URL_PREFIX = 'https://www.atptour.com/'

    def __init__(self, url):
        self.url = url
        self.match_result_list = []
        self._cur_round_name = None
        self._cur_round_order = -1
        self.parse_scores()

    def _parse_header_row(self, header_row):
        self._cur_round_name = clean_text(
            header_row,
            "./th/text()"
        )
        self._cur_round_order += 1

    @staticmethod
    def _get_id_from_link(player_url):
        if 'en/players' in player_url:
            return player_url.split('/')[-2]
        else:
            return None

    def _get_link_name_from_dt(self, dt):
        # Gets the player name and player url from a data-table element
        link = dt.xpath("./a")
        if len(link) > 1:
            raise ValueError("Expecting max one player, found %s" % [html.tostring(x) for x in link])
        elif len(link) == 1:
            player_name = clean_text(link[0], './text()')
            player_url = link[0].get('href')
            player_id = self._get_id_from_link(player_url)
        else:
            with open(WEIRD_RESULTS, 'a') as wr:
                wr.write(
                    "Could not find player link here in tournament %s: %s\n" %
                    (self.url, html.tostring(dt))
                )
            player_name = None
            player_url = None
            player_id = None
        return player_name, player_url, player_id

    def _parse_result_row(self, result_row):
        # TODO: Get match-stats URL
        winner_dt, loser_dt = result_row.xpath("./td[@class='day-table-name']")  # Data tables
        winner_name, winner_url, winner_id = self._get_link_name_from_dt(winner_dt)
        loser_name, loser_url, loser_id = self._get_link_name_from_dt(loser_dt)
        score_elems = result_row.xpath("./td[@class='day-table-score']/a")
        if len(score_elems) == 0:
            score = None
            match_stats_url = None
        else:
            score_elem = score_elems[0]
            score = regex_strip_array(score_elem.xpath('./text()'))
            score = [s for s in score if s != '']
            score = ';'.join(score)
            if 'href' in score_elem.attrib:
                match_stats_url = score_elem.attrib['href']
            else:
                match_stats_url = None
        self.match_result_list.append({
            'winner_name': winner_name,
            'loser_name': loser_name,
            'winner_url': winner_url,
            'loser_url': loser_url,
            'winner_id': winner_id,
            'loser_id': loser_id,
            'round': self._cur_round_name,
            'round_order': self._cur_round_order,
            'score': score,
            'match_stats_url': match_stats_url
        })

    def _parse_row(self, table_row):
        player_names = table_row.xpath(".//td[@class='day-table-name']")
        if len(player_names) != 2:  # If this is the case, probably a header
            assert len(table_row.xpath("./th")) == 1
            self._parse_header_row(table_row)
        else:
            assert len(table_row.xpath("./th")) == 0
            self._parse_result_row(table_row)

    def parse_scores(self):
        self.tree = html.fromstring(requests.get(self.url).content)
        score_table_elems = self.tree.xpath(".//table[@class='day-table']")
        assert len(score_table_elems) <= 1
        if len(score_table_elems) != 0:
            score_table_elem = score_table_elems[0]
            table_rows = score_table_elem.xpath('.//tr')
            for table_row in table_rows:
                self._parse_row(table_row)


class TournamentScraper(object):
    EXPECTED_ELEMS = 8  # We expect 8 elements per tournament row
    ELIGIBLE_SURFACES = [
        'Hard',
        'Carpet',
        'Clay',
        'Grass'
    ]

    def _check_xpath_validity(self):
        _n = len(self.tr_elem.xpath('.//td'))
        if _n != self.EXPECTED_ELEMS:
            raise ValueError("Expected {0} elements per tournament, received {1}").format(
                self.EXPECTED_ELEMS, _n
            )

    def _process_title_location_date(self, elem):
        self.tourney_title = clean_text(elem, ".//span[@class='tourney-title']/text()")
        self.tourney_location = clean_text(elem, ".//span[@class='tourney-location']/text()")
        self.tourney_dates = clean_text(elem, ".//span[@class='tourney-dates']/text()")
        tqdm.write("Parsing %s: %s" % (self.tourney_title, self.tourney_dates))

    def _process_draw_sizes(self, elem):
        sgd_dbl = regex_strip_array(elem.xpath(".//div[@class='item-details']/text()"))
        assert sgd_dbl == ['SGL', 'DBL', '']
        draw_sizes = regex_strip_array(elem.xpath(".//span[@class='item-value']/text()"))
        if len(draw_sizes) != 2:
            raise ValueError("Expected two draw sizes, found %d instead" % draw_sizes)
        self.singles_draw_size = int(draw_sizes[0])
        self.doubles_draw_size = int(draw_sizes[1])

    def _process_surface(self, elem):
        in_out = regex_strip_string(elem.xpath(".//div[@class='item-details']/text()[1]")[0])
        if in_out not in ['Indoor', 'Outdoor']:
            raise ValueError('Expected to see "Indoor" or "Outdoor", instead saw "%s"' % in_out)
        self.in_out = in_out
        surface = regex_strip_string(elem.xpath(".//span[@class='item-value']/text()[1]")[0])
        if surface not in self.ELIGIBLE_SURFACES:
            raise ValueError("Unrecognized Surface %s" % surface)
        self.surface = surface

    @staticmethod
    def _first_if_present(to_parse, expr, default=None):
        # Parses the first element if present, otherwise returns default value
        xpath_res = to_parse.xpath(expr)
        if len(xpath_res) > 0:
            return regex_strip_string(xpath_res[0])
        else:
            return default

    def _process_fin_commit(self, elem):
        # TODO: Make a function to process if present...
        self.fin_commit = self._first_if_present(elem, ".//span[@class='item-value']/text()[1]")

    def _process_tourney_winners(self, elem):
        elems = elem.xpath(".//div[@class='tourney-detail-winner']")
        if len(elems) != 2:
            raise ValueError("Expected two winners, instead found %d" % len(elems))
        singles, doubles = elems
        assert regex_strip_string(singles.xpath("./text()[1]")[0]) == 'SGL:'
        assert regex_strip_string(doubles.xpath("./text()[1]")[0]) == 'DBL:'

        singles_winner_html = singles.xpath(
            "./a"
        )
        doubles_winner_html = doubles.xpath(
            "./a"
        )
        if len(singles_winner_html) == 0:
            self.singles_winner_name = None
            self.singles_winner_link = None
        else:
            self.singles_winner_name = self._first_if_present(
                singles_winner_html[0], "./text()"
            )
            self.singles_winner_link = singles_winner_html[0].get('href')

        if len(doubles_winner_html) != 2:
            self.doubles_winner_first_name = None
            self.doubles_winner_first_link = None
            self.doubles_winner_second_name = None
            self.doubles_winner_second_link = None
        else:
            self.doubles_winner_first_name = self._first_if_present(
                doubles_winner_html[0], "./text()"
            )
            self.doubles_winner_second_name = self._first_if_present(
                doubles_winner_html[1], "./text()"
            )
            self.doubles_winner_first_link = doubles_winner_html[0].get('href')
            self.doubles_winner_second_link = doubles_winner_html[1].get('href')

    def _process_results_link(self, elem):
        tourney_url_elem = elem.xpath("./a")
        if len(tourney_url_elem) > 0:
            self.tourney_url_suffix = tourney_url_elem[0].get('href')
        else:
            self.tourney_url_suffix = None

    def _parse_year_id(self):
        if self.tourney_url_suffix is None:
            self.year_id = None
        else:
            split = self.tourney_url_suffix.split('/')
            assert split[0] == ''
            assert split[1] == 'en'
            assert split[2] == 'scores'
            assert split[3] in ('archive', 'current')
            self.tourney_id = split[5]
            url_year = split[6]
            self.year_id = '_'.join([url_year, self.tourney_id])

    def _parse_results(self):
        if self.tourney_url_suffix is not None:
            mp = MatchResultsParser(MatchResultsParser.URL_PREFIX + self.tourney_url_suffix)
            self.match_results = mp.match_result_list
        else:
            self.match_results = []

    def state_to_dict(self):
        return {
            'tourney_title': self.tourney_title,
            'tourney_location': self.tourney_location,
            'tourney_dates': self.tourney_dates,
            'tourney_singles_draw_size': self.singles_draw_size,
            'tourney_doubles_draw_size': self.doubles_draw_size,
            'tourney_in_out': self.in_out,
            'tourney_surface': self.surface,
            'tourney_singles_winner_name': self.singles_winner_name,
            'tourney_singles_winner_link': self.singles_winner_link,
            'tourney_doubles_winner_first_name': self.doubles_winner_first_name,
            'tourney_doubles_winner_second_name': self.doubles_winner_second_name,
            'tourney_doubles_winner_first_link': self.doubles_winner_first_link,
            'tourney_doubles_winner_second_link': self.doubles_winner_second_link,
            'tourney_url_suffix': self.tourney_url_suffix,
            'tourney_year_id': self.year_id
        }

    def __init__(self, tr_elem):
        self.tr_elem = tr_elem
        self._check_xpath_validity()
        self.table_entries = self.tr_elem.xpath('.//td')
        self._process_title_location_date(self.table_entries[2])
        self._process_draw_sizes(self.table_entries[3])
        self._process_surface(self.table_entries[4])
        self._process_fin_commit(self.table_entries[5])
        self._process_tourney_winners(self.table_entries[6])
        self._process_results_link(self.table_entries[7])
        self._parse_year_id()
        self._parse_results()

    def result_df(self):
        if len(self.match_results) == 0:
            return None
        else:
            match_result_df = pd.DataFrame(self.match_results)
            for k, v in self.state_to_dict().items():
                match_result_df[k] = v
            return match_result_df


class TennisScraper(object):

    @staticmethod
    def _get_tourney_tree(base_url):
        return html.fromstring(requests.get(base_url).content)

    def __init__(self, year, challenger=False):
        self.year = year
        _base_url = "http://www.atpworldtour.com/en/scores/results-archive?year=%d"
        self.base_url = _base_url % self.year
        if challenger:
            self.base_url += "&tournamentType=ch"
        self.tourney_tree = self._get_tourney_tree(self.base_url)
        self.tourneys = [
            TournamentScraper(t) for t in tqdm(
                self.tourney_tree.xpath("//tr[@class='tourney-result']")
            )
        ]

    def tourney_df(self):
        return pd.DataFrame([
            t.state_to_dict() for t in self.tourneys
        ])

    def match_df(self):
        _to_concat = [t.result_df() for t in self.tourneys]
        _to_concat = [df for df in _to_concat if df is not None]
        if len(_to_concat) == 0:
            return None
        return pd.concat(_to_concat)
