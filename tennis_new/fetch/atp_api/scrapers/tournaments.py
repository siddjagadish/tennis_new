import os
import pandas as pd
import sys
from tennis_new.fetch.atp_api.scrapers.functions import tournaments
from tennis_new.fetch.atp_api.defs import TournamentsResult

# Command line input
start_year = str(sys.argv[1])
end_year = str(sys.argv[2])

# Iterate through the years and scrape tourney data

print('')
print('Year    Tournaments')
print('----    -----------')

tourney_data = []
for h in range(int(start_year), int(end_year) + 1):
    year = str(h)
    tourney_data += tournaments(year)

# Output to CSV

tr = TournamentsResult()

# tourney_fin_commit was having parsing issues, so we've ruled this out for now
_rel_column_names = [
    x for x in tr.column_names if x != 'tourney_fin_commit'
]
df = pd.DataFrame(
    tourney_data,
    columns=_rel_column_names
)
df['tourney_fin_commit'] = None
df = df[tr.column_names]

filename = os.path.join(
    tr.api_results_path,
    'tournaments_' + start_year + '-' + end_year + '.csv'
)
df.to_csv(filename, sep=',', index=False)
