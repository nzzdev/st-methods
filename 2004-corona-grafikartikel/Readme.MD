# Coronavirus-Grafikartikel

1. Content: Scripts that generate charts and information for the graphics piece on coronavirus and supporting articles describing methodology and process.

2. Code used in these articles as well as in coronavirus graphics throughout nzz.ch:
  * Die wichtigsten Grafiken zum Coronavirus: https://www.nzz.ch/panorama/die-wichtigsten-grafiken-zum-coronavirus-ld.1542774
  * Die perfekte Corona-Grafik gibt es nicht: https://www.nzz.ch/visuals/coronavirus-die-perfekte-grafik-gibt-es-nicht-ld.1550139
  * Wie viele Menschen haben sich wirklich von Covid-19 erholt? https://www.nzz.ch/coronavirus-wie-viele-patienten-sind-wirklich-genesen-ld.1552519
  
3. Sources: Data from Johns Hopkins University, swiss cantons, the World Bank are used in the script. Additionally, data from the swiss Federal Office of Public Health, the Federal Statistical Office, the University of Oxford, various national public health offices and international institutions are used in the main graphics piece.

4. Non-trivial methods: 
* Method for calculating an estimate of recovered patients described here: https://www.nzz.ch/coronavirus-wie-viele-patienten-sind-wirklich-genesen-ld.1552519

* Our assumptions for recovery:
    * 75% of patientes have recovered after 14 days
    * an aditional 10% of patientes have recovered after 21 days
    * an aditional 10% of patientes have recovered after 28 days
    * the remaining 5% of patientes have recovered after 42 days

* Sources for estimations:
    * BL: https://www.baselland.ch/politik-und-behorden/direktionen/volkswirtschafts-und-gesundheitsdirektion/amt-fur-gesundheit/medizinische-dienste/kantonsarztlicher-dienst/aktuelles/covid-19-faelle-kanton-basel-landschaft/pdf/konzept-geheilte-bl.pdf/@@download/file/Konzept_Geheilte_BL.pdf
    * WHO: https://www.who.int/docs/default-source/coronaviruse/who-china-joint-mission-on-covid-19-final-report.pdf
    * ECDC: https://www.ecdc.europa.eu/sites/default/files/documents/covid-19-rapid-risk-assessment-coronavirus-disease-2019-eighth-update-8-april-2020.pdf
    * Lancet: https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30243-7/fulltext#figures

* doubling time method by J.M. Spicer http://rstudio-pubs-static.s3.amazonaws.com/10369_9e0e4a116538489baa18908c1690293c.html
  
  
5. Scripts: 
* corona-master-public.R: Main script used for updating the coronavirus graphics that need regular updates. The script is executed from start to finish every morning, delivering data that is correctly formatted for use in our graphics tool Q as well as summary statistics for use in the main article. Script also delivers data for updates of country-specific graphics that are used in other pieces (e.g. news tickers) or for use in daily coronavirus reporting. Script has been adjusted for public use and will be updated when necessary.

* corona-meta-public.R: Code chunks used in secondary pieces, not functional on its own, run after main script has rum through.

6. References:

* Data sources: JHU, Canton of Zurich, linked in pieces/script accordingly. Population figures are [World Bank](https://data.worldbank.org/indicator/SP.POP.TOTL) / [Federal Statistical Office](https://www.bfs.admin.ch/bfs/de/home/statistiken/bevoelkerung/stand-entwicklung/bevoelkerung.assetdetail.9486033.html)
* Methods: linked above
* Tools: 
    * R Core Team (2019), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Visuals. We do not guarantee that the information therein is adequate, complete or up to date.

