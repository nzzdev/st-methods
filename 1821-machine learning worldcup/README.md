# 1821 WM-Machine Learning

1. The uploaded scripts were used to 
	* gather statistics and market value data on football players participating in the world cup
	* understand what makes the top-players valuable
	* predict which players will be more valuable after the world cup (not all datasets and all of the code published, yet as we want to run a post-worldcup analysis)

2. Which articles present results generated with those scripts ?
  * Explaining before the world cup what makes great football playes so valuable: [Faule Fussballspieler sind besonders wertvoll – das sagt zumindest eine Maschine](https://www.nzz.ch/sport/fussball-wm-2018/faule-fussballspieler-sind-besonders-wertvoll-das-sagt-zumindest-eine-maschine-ld.1388000), published 20.06.2018
  * Who are the overperformers and the underperformers of the eight remaining teams in the quartefinal: [Der nächste grosse englische Spieler könnte Jesse Lingard sein – wieso Sie bei der WM nicht ausschalten sollten](https://www.nzz.ch/sport/fussball-wm-2018/englischer-spaetzuender-und-die-leiden-des-jesus-von-sao-paulo-wieso-sie-bei-der-wm-nicht-ausschalten-sollten-ld.1401093) , published 06.07.2018


  
3. We used data from Fifa and Transfermarkt

4. We used the Machine Learning library scikit-learn and its algorithm Ada Boost regressor

5. What the scripts do:
	* The Step 1 and Step 2 scripts scrape the websites of FIFA (player statistics) and Transfermarkt(data on market value of players before and after the world cup) for the year 2014. 
	* The Step 3-script merges the two databases and cleans the data. Also, it creates so-called features, metrics that might be more specific for each player because they are relative to their playing time or represent a player's contribution to his team. 
	* In Step 4, this data is used to train and test a machine learning model called Ada Boost that should learn to predict a player's market value based on his statistics.

  
6. References:
  * [Data from Fifa for 2014](https://www.fifa.com/worldcup/archive/brazil2014/statistics/players/goal-scored.html) 
  * [Data from Transfermarkt for 2014](https://www.transfermarkt.de/spieler-statistik/marktwertnachwm/marktwertetop?land_id=0&spielerposition_id=0&altersklasse=&plus=1)
  * [Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011. ](http://scikit-learn.org/stable/)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.
