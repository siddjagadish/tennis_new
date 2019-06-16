from pathlib import Path
from tennis_new.infra.defs import REPO_DIR

STORED_DATA_PATH = Path.joinpath(REPO_DIR, 'fetch', 'stored_data')
STATIC_TOURNAMENTS = Path.joinpath(STORED_DATA_PATH, 'tournaments_1877-2017.csv')

