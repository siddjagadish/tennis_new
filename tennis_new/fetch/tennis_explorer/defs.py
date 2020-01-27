from tennis_new.infra.defs import REPO_DIR
from pathlib import Path

DATE_FORMAT = '%Y-%m-%d'
DATA_PATH = Path.joinpath(REPO_DIR, 'fetch', 'tennis_explorer', 'stored_data_w_link')
ALL_MATCH_PATH = Path.joinpath(DATA_PATH, 'match_results.csv')
ERROR_FILE = Path.joinpath(REPO_DIR, 'fetch', 'tennis_explorer', 'stored_data_w_link', 'errors.log')
