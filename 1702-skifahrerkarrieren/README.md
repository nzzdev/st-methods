# 1702-skifahrerkarrieren

1. This script scrapes the FIS database in order to find the world's top skiers since 1967 and visualize and categorize their careers

2. Results based on these scripts were published in a series of articles, one for each race in the Alpine World Ski Championships in St. Moritz 2017:
  * Main article presenting results: [Die erfolgreichsten Skifahrer der Geschichte im Direktvergleich](https://nzz.ch/ld.139656), published 06.02.2017
  * Article that describes our methods: [Wie aus Datenbergen Karrieretypen wurden](https://nzz.ch/ld.142634), published 06.02.2017
  * Article on Tina Weirather and Lara Gut in the Super-G: [Mutter und Tochter im Duell mit Schweizerinnen](https://nzz.ch/ld.143600), published 07.02.2017
  * Article on the skiers chasing Marcel Hirscher: [Alle jagen Hirscher](https://nzz.ch/ld.141750), published 08.02.2017
  * Article on the favourites for the downhill race: [Das sind Mitfavoriten für die WM-Abfahrt](https://nzz.ch/ld.144112), published 11.02.2017
  * Article on the most sucessful allrounders: [Von Girardelli bis Svindal – die erfolgreichsten Allrounder](https://nzz.ch/ld.144597), published 13.02.2017
  * Article on the revival of the 1980ies regarding sucessful Swiss women skiers: [Revival der 1980er mit Gut und Holdener](https://nzz.ch/ld.144109), published 10.02.2017
  * Article on Lindsey Vonn chasing Ingemar Stenmark records: [Lindsey Vonn jagt Stenmarks Allzeitrekorde](https://nzz.ch/ld.144113), published 12.02.2017
  * Article on the ski rivalry between Switzerland and Austria: [Österreich-Schweiz: Das Duell geht in die nächste Runde](https://nzz.ch/ld.144910), published 16.02.2017
  * Article on historical duels in the giant slaloms: [Wann sich Stenmark, Zurbriggen und Hirscher mit wem duellierten](https://nzz.ch/ld.145751), published 17.02.2017
  * Article on the most sucessful ski countries: [Welches Land die erfolgreichsten Skirennfahrer trainiert](https://nzz.ch/ld.146137), published 18.02.2017
  * Article on the skiers who missed most podium opportunities: [Wer immer wieder am Podest vorbeifuhr](https://nzz.ch/ld.146003), published 19.02.2017

3. Data were scraped from the [FIS database](https://data.fis-ski.com/).

4. Methods: A skier was part of our story if s/he was part of the top ten of the world cup ranking in at least one season since the world cup exists (1967). A skier's careers was shown as cumulative podiums in world cup, world championship and olympic races over time. We approximated each skier's career shape with linear functions and used their slopes [in order to categorize skiers' careers](https://nzz.ch/ld.142634). Methods are described in more detail in the scripts and in [this article](https://nzz.ch/ld.142634). 

6. References
  * Data source: [FIS database](https://data.fis-ski.com/)
  * Methods: [Our methods article](https://nzz.ch/ld.142634)
  * Code: R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)


We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.