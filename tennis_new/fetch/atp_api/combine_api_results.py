import os
import pandas as pd

from tennis_new.fetch.defs import STORED_DATA_PATH
from tennis_new.fetch.atp_api.defs import (
    MatchScoresResult,
    MatchStatsResult,
    TournamentsResult
)
import click


RESULT_CLASS_MAPPING = {
    'match_scores': MatchScoresResult,
    'match_stats': MatchStatsResult,
    'tournaments': TournamentsResult
}
OUTPUT_FILENAME = 'combined.csv'


def _abs_path_all_files_in_dir(dir):
    # Get absolute path to all files in a directory
    return [
        os.path.abspath(os.path.join(dir, f)) for f in os.listdir(dir)
    ]


def _combine_data(data_type, static_has_header):
    result_class = RESULT_CLASS_MAPPING[data_type]()
    column_names = result_class.column_names

    print("Reading API results...")
    api_results_dir = result_class.api_results_path
    api_results_files = _abs_path_all_files_in_dir(api_results_dir)
    api_results_dfs = [pd.read_csv(f) for f in api_results_files]

    print("Reading static data...")
    static_dir = result_class.static_results_path
    if OUTPUT_FILENAME in os.listdir(static_dir):  # Use previous combined file if exists...
        print ("Found existing combined file...")
        static_dfs = [
            pd.read_csv(
                os.path.join(static_dir, OUTPUT_FILENAME)
            )
        ]
    else:
        print("Operating on downloaded static history...")
        static_files = _abs_path_all_files_in_dir(static_dir)
        _header = 0 if static_has_header else None
        _names = None if static_has_header else column_names
        static_dfs = [
            pd.read_csv(f, header=_header, names=_names) for f in static_files
        ]

    print("Concatenating...")
    combined = pd.concat(api_results_dfs + static_dfs)  # TODO: Write out this data
    gpd = combined.groupby(result_class.unique_id)
    if gpd.size().max() > 1:
        print("Warning, %d duplicate %s found, deduping..." % (gpd.size().max(), result_class.unique_id))
        combined.drop_duplicates(result_class.unique_id, inplace=True)

    print("Writing...")
    out_path = os.path.join(
        result_class.static_results_path,
        OUTPUT_FILENAME,
    )
    combined.to_csv(out_path, sep=',', index=False)


@click.command()
@click.option('--data-type', help='type of data to combine')
@click.option('--static_has_header', default=False, help='does the static data have a header?')
def combine_data(data_type, static_has_header):
    _combine_data(data_type, static_has_header)


if __name__ == '__main__':
    combine_data()
