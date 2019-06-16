import os
from tennis_new.infra.defs import REPO_DIR
from tennis_new.fetch.defs import STORED_DATA_PATH


API_RESULTS_DIR = os.path.join(
   REPO_DIR, 'fetch', 'atp_api', 'api_results'
)

MATCH_STATS_HEADER = [
    'tourney_order',
    'match_id',
    'match_stats_url_suffix',
    'match_time',
    'match_duration',
    'winner_aces',
    'winner_double_faults',
    'winner_first_serves_in',
    'winner_first_serves_total',
    'winner_first_serve_points_won',
    'winner_first_serve_points_total',
    'winner_second_serve_points_won',
    'winner_second_serve_points_total',
    'winner_break_points_saved',
    'winner_break_points_serve_total',
    'winner_service_points_won',
    'winner_service_points_total',
    'winner_first_serve_return_won',
    'winner_first_serve_return_total',
    'winner_second_serve_return_won',
    'winner_second_serve_return_total',
    'winner_break_points_converted',
    'winner_break_points_return_total',
    'winner_service_games_played',
    'winner_return_games_played',
    'winner_return_points_won',
    'winner_return_points_total',
    'winner_total_points_won',
    'winner_total_points_total',
    'loser_aces',
    'loser_double_faults',
    'loser_first_serves_in',
    'loser_first_serves_total',
    'loser_first_serve_points_won',
    'loser_first_serve_points_total',
    'loser_second_serve_points_won',
    'loser_second_serve_points_total',
    'loser_break_points_saved',
    'loser_break_points_serve_total',
    'loser_service_points_won',
    'loser_service_points_total',
    'loser_first_serve_return_won',
    'loser_first_serve_return_total',
    'loser_second_serve_return_won',
    'loser_second_serve_return_total',
    'loser_break_points_converted',
    'loser_break_points_return_total',
    'loser_service_games_played',
    'loser_return_games_played',
    'loser_return_points_won',
    'loser_return_points_total',
    'loser_total_points_won',
    'loser_total_points_total',
]

MATCH_SCORES_HEADER = [
    'tourney_year_id',
    'tourney_order',
    'tourney_slug',
    'tourney_url_suffix',
    'tourney_round_name',
    'round_order',
    'match_order',
    'winner_name',
    'winner_player_id',
    'winner_slug',
    'loser_name',
    'loser_player_id',
    'loser_slug',
    'winner_seed',
    'loser_seed',
    'match_score_tiebreaks',
    'winner_sets_won',
    'loser_sets_won',
    'winner_games_won',
    'loser_games_won',
    'winner_tiebreaks_won',
    'loser_tiebreaks_won',
    'match_id',
    'match_stats_url_suffix',
]

TOURNAMENTS_HEADER = [
    'tourney_year',
    'tourney_order',
    'tourney_name',
    'tourney_id',
    'tourney_slug',
    'tourney_location',
    'tourney_dates',
    'tourney_month',
    'tourney_day',
    'tourney_singles_draw',
    'tourney_doubles_draw',
    'tourney_conditions',
    'tourney_surface',
    'tourney_fin_commit',
    'tourney_url_suffix',
    'singles_winner_name',
    'singles_winner_url',
    'singles_winner_player_slug',
    'singles_winner_player_id',
    'doubles_winner_1_name',
    'doubles_winner_1_url',
    'doubles_winner_1_player_slug',
    'doubles_winner_1_player_id',
    'doubles_winner_2_name',
    'doubles_winner_2_url',
    'doubles_winner_2_player_slug',
    'doubles_winner_2_player_id',
    'tourney_year_id',
]


class APIResult(object):

    @property
    def name(self):
        raise NotImplementedError

    @property
    def unique_id(self):
        raise NotImplementedError

    @property
    def column_names(self):
        raise NotImplementedError

    @property
    def api_results_path(self):
        return os.path.join(
            API_RESULTS_DIR,
            self.name
        )

    @property
    def static_results_path(self):
        return os.path.join(
            STORED_DATA_PATH,
            self.name
        )


class MatchStatsResult(APIResult):

    @property
    def name(self):
        return 'match_stats'

    @property
    def unique_id(self):
        return 'match_id'

    @property
    def column_names(self):
        return MATCH_STATS_HEADER


class MatchScoresResult(APIResult):

    @property
    def name(self):
        return 'match_scores'

    @property
    def unique_id(self):
        return 'match_id'

    @property
    def column_names(self):
        return MATCH_SCORES_HEADER


class TournamentsResult(APIResult):

    @property
    def name(self):
        return 'tournaments'

    @property
    def unique_id(self):
        return ['tourney_year', 'tourney_order']

    @property
    def column_names(self):
        return TOURNAMENTS_HEADER
