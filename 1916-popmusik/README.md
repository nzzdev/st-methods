# 1916-popmusik

1. R-Script that scrapes, formats, analyses and visualizes the Swiss single and album charts since 1968 and 1983, respectively. Clean datasets and raw html files are provided as well for convenience.

2. Results in the following piece:
  * [Und plötzlich dominieren wenige Superhits die Schweizer Charts](https://www.nzz.ch/feuilleton/schweizer-charts-und-ploetzlich-dominieren-wenige-superhits-ld.1488251)
  * Publication date: 2019-12-05
  * In recent years, the swiss single charts have increasingly been dominated by single songs and artists, while the opposite is true for the album charts, where the average lifespan of an entry has decreased. The articles looks at some of the longest-leading songs and theorizes on the causes of these trends. Additionally, the lifespan of the average hit ist shown, along with some examples of late bloomers and recurring appearances.
  
3. The data is scraped from hitparade.ch, which gets it from GfK Entertainment AG.

4. The hitparade.ch website was scraped, the data was formatted using regual expressions. Simple summary statistics were used. Median was used as a measure of central tendency for robustness.

5. One script was used: It gets the data from hitparade.ch, saves it in html files and then turns it into a usable data frame. In the published script, this part is commented out and a clean .csv containing all data at publication is provided. The script then calculates the yearly median lifespan of songs and albums at the top of the charts and the median trajectory of a number 1 hit. It then visualizes these findings, along with specific cases of single songs.
  
6. References
  * Data source: [hitparade.ch](https://www.https://hitparade.ch/charts)
  * Methods: [Our methods section](https://www.nzz.ch/feuilleton/schweizer-charts-und-ploetzlich-dominieren-wenige-superhits-ld.1488251#subtitle-die-methodik-im-detail)
  * Code: 
    * R Core Team (2019), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Visuals. We do not guarantee that the information therein is adequate, complete or up to date.
