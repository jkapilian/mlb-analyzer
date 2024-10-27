# MLB Analyzer
Get more detailed information than what the MLB Ballpark app provides

## How to Run
* Create a CSV with the following columns:
`HomeTeam,Date,DoubleheaderGameNumber(if applicable)`
* Run the following
`pip install -r requirements.txt`
`python main.py -d example.csv`
* Example output:
```
SUMMARY:
--------------------------------------

Total players seen: 110
Most seen players: 
Carlos Beltrán: 4 (NYM)
David Wright: 4 (NYM)
Pedro Feliciano: 4 (NYM)
Aaron Heilman: 3 (Unknown)
José Reyes: 3 (NYM)

You've seen 12 players hit 13 home runs
Biggest power hitters: 
Kelly Johnson: 2 (ATL)
David Wright: 1 (NYM)
Ramon Castro: 1 (NYM)
Shawn Green: 1 (NYM)
Edgar Renteria: 1 (ATL)
Carlos Beltrán: 1 (NYM)
Carlos Delgado: 1 (NYM)
Ramón Vázquez: 1 (Unknown)
Ian Kinsler: 1 (TEX)
Milton Bradley: 1 (Unknown)
Brian Schneider: 1 (NYM)
B.J. Upton: 1 (TB)

You've seen 1 players hit 1 triples
Fastest around the basepaths: 
José Reyes: 1 (NYM)

You've seen 4 games over the years!
Most attended games: 
April 22, 2007 ATL vs. NYM: 55671
June 15, 2008 TEX vs. NYM: 55438
June 18, 2006 BAL vs. NYM: 43393
June 21, 2009 TB vs. NYM: 38791
Least attended games: 
June 21, 2009 TB vs. NYM: 38791
June 18, 2006 BAL vs. NYM: 43393
June 15, 2008 TEX vs. NYM: 55438
April 22, 2007 ATL vs. NYM: 55671
Longest games attended: 
June 21, 2009 TB vs. NYM: 3:55
June 15, 2008 TEX vs. NYM: 3:23
April 22, 2007 ATL vs. NYM: 3:21
June 18, 2006 BAL vs. NYM: 2:58
Shortest games attended: 
June 18, 2006 BAL vs. NYM: 2:58
April 22, 2007 ATL vs. NYM: 3:21
June 15, 2008 TEX vs. NYM: 3:23
June 21, 2009 TB vs. NYM: 3:55
```

## Acknowledgements
Makes use of the [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) Python package.