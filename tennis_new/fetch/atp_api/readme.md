#### Source of data and code
https://github.com/serve-and-volley/atp-world-tour-tennis-data/

#### To Check:
Unique ID columns should never be null...

#### Corrections!:
* fin_commit was throwing some errors, so have modified the scraper not to scrape this column.  We fill it in with None to combine with the static data 

#### How to Use Scripts in this Directory

There are various callable scripts in this directory:

* match_stats.py: Gets match statistics for each of many matches.  Statistics include:
    * 1st service points won for each player
    * % of first serves in for each player
    * etc.
* match_results.py: Need to write this one...


When using these scripts:

These scripts scrape web data and fail frequently.  They print out (at least match_stats.py does) the indices of the tournaments as they go, so you know where to pick these up
