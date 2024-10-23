# MLB Analyzer
Get more detailed information than what the MLB Ballpark app provides!

## How to Run
* Create a CSV with the following columns:
`HomeTeam,Date,DoubleheaderGameNumber(if applicable)`
* Run the following
`pip install -r requirements.txt`
`python main.py -f example.csv`
* Example output:
```
SUMMARY:
--------------------------------------

Total players seen: 110
Most seen players: 
Carlos Beltrán: 4
David Wright: 4
Pedro Feliciano: 4
Aaron Heilman: 3
José Reyes: 3

You've seen 12 players hit 13 home runs
Biggest power hitters: 
Kelly Johnson: 2
David Wright: 1
Ramon Castro: 1
Shawn Green: 1
Edgar Renteria: 1
Carlos Beltrán: 1
Carlos Delgado: 1
Ramón Vázquez: 1
Ian Kinsler: 1
Milton Bradley: 1
Brian Schneider: 1
B.J. Upton: 1

You've seen 1 players hit 1 triples
Fastest around the basepaths: 
José Reyes: 1

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