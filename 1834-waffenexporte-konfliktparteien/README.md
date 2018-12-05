# 1834-waffenexporte-konfliktparteien

1. This script uses data on Swiss weapon exports and worldwide data on conflicts to examine whether such exports also happen during times where the receiving country is involved in a conflict.

2. Results based on this script were published in the following article:
  * [Die Schweiz exportiert vermehrt Waffen in kriegführende Länder](https://www.nzz.ch/waffenexporte-schweiz-liefert-vermehrt-in-laender-mit-konflikten-ld.1422907)
  * Published 06.12.2018
  * The article shows that weapon exports to countries whose government is involved in an international or internal conflict are increasing since 2014, when the Swiss reglementation on weapon exports was loosened. It further depicts to which countries the largest shares were exported and explains the conflict situations for the countries to which Switzerland exported weapons during conflicts in ten years or more.

3. A script that processes data on weapon exports by receiving country and year (2000-2017.xlsx) was processed by [SRF Data](https://srfdata.github.io/2017-02-kriegsmaterial/#) earlier. We included part of their code in our script. We added data on [state-based](http://ucdp.uu.se/downloads/#d3) and [one-sided](http://ucdp.uu.se/downloads/#d6) violence from the [Uppsala Conflict Data Program (UCDP)](http://ucdp.uu.se/), and merged the conflict data to the export data. The UCDP collects and curates detailed data on conflicts, their actors, their start and end dates and their victims.

4. We only included conflicts that involve the government of a state as the primary actor of the conflict. Exceptions were made for Saudi Arabia and the United Arab Emirates regarding the conflict in Yemen as well as for Russia regarding the conflicts in Syria, Ukraine and Georgia. The UCDP defines these states as being secondary / supporting actors in these conflicts; however, the NZZ regards them as being central actors in these contexts and therefore treated them as if they were primary actors in these specific cases. More detailed comments on our rationale for this, and on our sources and methods in general can be found [at the bottom of our article](https://www.nzz.ch/ld.1422907#subtitle-die-methodik-im-detail).

5. References
  * Data sources: [Swiss State Secretariat for Economic Affairs (Seco)](https://www.seco.admin.ch/seco/de/home/Aussenwirtschaftspolitik_Wirtschaftliche_Zusammenarbeit/Wirtschaftsbeziehungen/exportkontrollen-und-sanktionen/ruestungskontrolle-und-ruestungskontrollpolitik--bwrp-/zahlen-und-statistiken0.html), [Uppsala Conflict Data Program](http://ucdp.uu.se/), see point 3. above
  * Code: R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)
  
6. License<br>
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This project (1834-waffenexporte-konfliktparteien) by NZZ Visuals is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>. The code that reads and processes weapon export data was written by [SRF Data](https://github.com/srfdata/2017-02-kriegsmaterial) and added to our script. 


We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.
