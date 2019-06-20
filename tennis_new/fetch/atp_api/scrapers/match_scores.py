import os
import sys
import pandas as pd
from tennis_new.fetch.atp_api.defs import MatchScoresResult
from tennis_new.fetch.atp_api.scrapers.functions import (
    scrape_year, scrape_tourney, array2csv
)

# Command line input
start_year = str(sys.argv[1])
end_year = str(sys.argv[2])

# STEP 1: Scrape year page
msr = MatchScoresResult()
filename = os.path.join(
    msr.api_results_path,
    "match_scores_" + start_year + "-" + end_year + '.csv'
)
for h in range(int(start_year), int(end_year) + 1):

    year = str(h)
    scrape_year_output = scrape_year(year)
    tourney_data_scrape = scrape_year_output[0]
    tourney_urls_scrape = scrape_year_output[1]

    print('')
    print('Scraping match info for ' + str(len(tourney_urls_scrape)) + ' tournaments...')
    print('Year    Order    Tournament                                Matches')
    print('----    -----    ----------                                -------')

    for i in range(0, len(tourney_urls_scrape)):
        tourney_match = []
        if len(tourney_urls_scrape[i]) > 0:
            # STEP 2: Scrape tournament page
            scrape_tourney_output = scrape_tourney(tourney_urls_scrape[i])
            match_data_scrape = scrape_tourney_output[0]
            match_urls_scrape = scrape_tourney_output[1]

            # STEP 3: tourney_data + match_data
            for match in match_data_scrape:
                foo = tourney_data_scrape[i] + match
                tourney_match.append(foo)

            spacing_count1 = len('Order') - len(str(tourney_data_scrape[i][1]))
            spacing1 = ''
            for j in range(0, spacing_count1): spacing1 += ' '

            spacing_count2 = 41 - len(tourney_data_scrape[i][2])
            spacing2 = ''
            for j in range(0, spacing_count2): spacing2 += ' '

            print(
                year + '    ' + str(tourney_data_scrape[i][1]) + spacing1 + '    ' + tourney_data_scrape[i][2] +
                spacing2 + ' ' + str(len(match_data_scrape))
            )

        cur_df = pd.DataFrame(
            tourney_match,
            columns=msr.column_names
        )

        # Encode strings in unicode
        for col in [
            'winner_name',
            'loser_name'
        ]:
            cur_df[col] = cur_df[col].str.decode('utf-8')

        header = not os.path.exists(filename)
        cur_df.to_csv(
            filename,
            header=header,
            mode='a+',
            index=False
        )
