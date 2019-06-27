#### Source of data and code
https://github.com/serve-and-volley/atp-world-tour-tennis-data/

#### To Check:
Unique ID columns should never be null...

#### Corrections!:
* fin_commit was throwing some errors, so have modified the scraper not to scrape this column.  We fill it in with None to combine with the static data 
* match_id 2019-339-mc10-d994 looks like it was in the future

#### TODOs:
* Add match stats to joined
* Make date column in joined
* See if we can find match date instead of just tourney date
* Do future date correction above

#### How to Use Scripts in this Directory

There are various callable scripts in the scrapers directory:

* match_stats.py: Gets match statistics for each of many matches.  Statistics include:
    * 1st service points won for each player
    * % of first serves in for each player
    * etc.
* match_scores.py:
    * Gets the score of each match
    * winner name
    * loser name
* tournaments.py:
    * Gets metadata about the tournament, including surface
   


When using these scripts:

These scripts scrape web data and fail frequently.  They print out (at least match_stats.py does) the indices of the tournaments as they go, so you know where to pick these up
