import click
from datetime import datetime, timedelta
from tennis_new.fetch.tennis_explorer.scraper import TennisExplorerParser
from tennis_new.fetch.tennis_explorer.defs import DATE_FORMAT, ERROR_FILE
from time import sleep


def scrape_dates(max_date, min_date, wait_time):
    max_date = datetime.strptime(max_date, DATE_FORMAT)
    min_date = datetime.strptime(min_date, DATE_FORMAT)
    max_date = min(datetime.today() - timedelta(days=1), max_date)
    cur_date = max_date
    while cur_date > min_date:
        print("Scraping For Date %s" % cur_date.strftime(DATE_FORMAT))
        try:
            te = TennisExplorerParser(cur_date)
            te.process()
            te.write_df()
        except:
            with open(ERROR_FILE, 'a') as wr:
                wr.write("Error on date %s\n" % cur_date.strftime(DATE_FORMAT))
        cur_date += timedelta(days=-1)
        print("Waiting %d seconds..." % wait_time)
        sleep(wait_time)

@click.command()
@click.option('--max-date', prompt='Max Date')
@click.option('--min-date', default='1997-01-01', prompt='Min Date')
@click.option('--wait-time', default=0, prompt='Wait Time (seconds)')
def scrape(max_date, min_date, wait_time):
    scrape_dates(max_date, min_date, wait_time)


if __name__ == '__main__':
    scrape()