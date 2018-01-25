# 1755-gemeinderatskandidaten

1. These scripts were written to process and analyse data regarding socio-demographic variables of the candidates for the Zurich parliamentary election, 2018.

2. Results based on these scripts were published in the following articles:
  * Article that shows how strongly the candidates deviate from the Zurich population regarding socio-demographic variables: [Rund 1000 Personen bewerben sich für einen Sitz im Stadtzürcher Parlament – warum sie Zürich trotzdem schlecht abbilden](https://nzz.ch/ld.1341817), published 09.01.2018
  * Follow-up article that shows how strongly the political parties differ from each other, regarding these variables: [Welche Partei stellt die jüngsten Kandidaten? Die wenigsten Frauen? Die meisten Führungskräfte?](https://nzz.ch/ld.1346145), published 25.01.2018

3. Data on the distribution of these variables among the candidates were provided by [Smartvote](https://www.smartvote.ch/) for the first article. Complete data for the follow-up article were available only from January 17th on, and provied by [Statistik Stadt Zürich via Open data Zurich](https://data.stadt-zuerich.ch/dataset/politik-gemeinderatswahlen-2018-alle-kandidierenden). Data on the distribution of the same variables ([age, gender](https://data.stadt-zuerich.ch/dataset/bev_monat_bestand_quartier_geschl_ag_herkunft_seit2013_od3250), [fist name](https://data.stadt-zuerich.ch/dataset/bev_bestand_vornamen_jahrgang_geschlecht_od3701)) in the population are provided by Statistik Stadt Zürich via Open Data Zurich, or, regarding polling data on profession, by Statistik Stadt Zürich on request.

4. The semi-automatic and iterative method used to categorize professions is described in the [methods part of the articles](https://www.nzz.ch/zuerich/wer-sind-die-kandidierenden-fur-den-zurcher-gemeinderat-ld.1341817#subtitle-die-methodik-im-detail) and, in detail, in the scripts.

5. The scripts calculate buckets for age groups, proportions for gender, age and first name among the candidates and within the population, categorize the professions indicated by the candidates and attributes candidates' zip code to districts. 
   * The script `gemeinderat.R` determines the districts the candidates of which represent its population in the best / poorest way. And it makes out the most prototypical and the most representative candidate. 
   * The script `gemeinderat_partei.R` determines the same measures by political party.
  
6. References
  * Data sources: [Smartvote](https://www.smartvote.ch/), [Statistik Stadt Zürich / Open Data Zürich](https://data.stadt-zuerich.ch/), see point 3. above
  * Code: R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)


We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.