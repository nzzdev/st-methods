# 1782-bundestagswahl

1. These scripts were used to create maps and scatterplots following the German parliamentary elections (Bundestagswahl) 2017

2. Results based on these scripts were published in several articles:
  * Overview of the election results: [So hat Deutschland gewählt – alle Resultate in der Übersicht](https://nzz.ch/ld.1316249), published 25.09.2017
  * Article showing where the German parties won or lost their votes: [Wo die Parteien gewonnen haben, wo sie verloren haben](https://nzz.ch/ld.1316297), published 25.09.2017
  * Article showing correlations between electoral results and socio-economic variables: [Wie Einkommen, Migration und Arbeitslosigkeit das Wahlergebnis beeinflussen](https://nzz.ch/ld.1318290), published 25.09.2017
  * Explainer on the crash of the SPD: [Der Absturz der SPD – mit Grafiken erklärt](https://nzz.ch/ld.1318264), published 25.09.2017
  * Explainer on the rise of the AFD: [Der Erfolg der AfD – mit Grafiken erklärt](https://nzz.ch/ld.1316942), published 25.09.2017

3. [Electoral data](https://service.bundeswahlleiter.de/medien/), [socioeconomic data](https://www.bundeswahlleiter.de/bundestagswahlen/2017/strukturdaten.html) as well as a shapefile of [German electoral constituencies (Wahlkreise)](https://www.bundeswahlleiter.de/bundestagswahlen/2017/wahlkreiseinteilung/downloads.html) were obtained on the webpage of the German [Federal Returning Officer (Bundeswahlleiter)](https://www.bundeswahlleiter.de/).

4. The methods used to cluster values into buckets depended on the map type, see point 5. below. Correlations were calculated using Spearman's method.

5. Several R-cripts were written for data processing, analysis and visualisation:
  * kartenBTW_1_setup.R loads and processes data and fonts and defines colors
  * kartenBTW_2_parteistaerke.R loops over the major German parties and creates a geographical map of their vote shares (buckets are created using k-means clustering, polygons are colored accordingly)
  * kartenBTW_3_diff.R calculates the wins and losses for each party, as compared to the previous election, and creates a geographical map (buckets are 10 intervals of equal length between the +/- the absolute value of the maximal deviation
  * kartenBTW_4_gewinner.R creates a map with the strongest party per electoral constituency
  * kartenBTW_5_wahlbeteiligung.R creates a map of the vote turnout (buckets are created using k-means clustering)
  * kartenBTW_6_parteifokus.R loops over the major German parties and creates the maps parteistaerke and diff (see above) side-by-side
  * kartenBTW_7_gekippt.R creates two maps: one with the strongest party per electoral constituency and the same with data from the previous election, in order to show which constituencies were won by another party than 2013 (and, therefore, are sending a representative from another party to the parliament)
  * scatterplotsBTW.R loads and processes electoral and socio-economic data for each electoral constituency, calculates correlation coefficients and r^2-values and creates scatterplots between all combinations of the levels of these variables, for analysis; it then creates scatterplots with or without labelled points / highlighted groups of points for selected levels, for publication
  
6. References
  * Data source: [Bundeswahlleiter](https://data.fis-ski.com/), see point 3. above
  * Code: R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)


We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.