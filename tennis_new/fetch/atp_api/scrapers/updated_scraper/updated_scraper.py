import click
from tennis_new.fetch.atp_api.scrapers.updated_scraper.base import TennisScraper
from tennis_new.fetch.atp_api.defs import API_RESULTS_DIR
from pathlib import Path

OUTPUT_DIR = Path.joinpath(API_RESULTS_DIR, 'updated_api_results')
# TODO: Set up logging

@click.command()
@click.option('--start-year', prompt='Start Year')
@click.option('--end-year', default=2020, prompt='End Year')
def scrape(start_year, end_year):
    for year in range(int(start_year), int(end_year)):
        ts = TennisScraper(int(year))
        match_df = ts.match_df()
        match_df.to_csv(
            Path.joinpath(OUTPUT_DIR, "match_results_%s.csv" % year),
            index=False
        )

        ts_challenger = TennisScraper(int(year), challenger=True)
        match_df_ch = ts_challenger.match_df()
        if match_df_ch is not None:
            match_df_ch.to_csv(
                Path.joinpath(OUTPUT_DIR, "match_results_challenger_%s.csv" % year),
                index=False
            )
        else:
            print("No challenger matches found for year %d" % year)


if __name__ == '__main__':
    scrape()
