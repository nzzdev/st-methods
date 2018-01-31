# 1805-regionen im fokus des US-praesidenten

1. These scripts build corpora based on the state of the union addresses and analyse these texts regarding mentions of different countries and regions overall and over time.

2. Results based on these scripts were published in the following article:
  * [Freund und Feind, betrachtet durch die Brille des Weissen Hauses](https://nzz.ch/ld.1349175)
  * Published 31.01.2018
  * The article shows how important America has become, in these addresses, in recent times, how the US presidents' mentions of parts of the world have shifted over time, and how president Donald Trump sets new records.

3. The text corpus was constructed based on the [R-library `sotu`](https://github.com/statsmaths/sotu), the website of the [White House](https://www.whitehouse.gov/briefings-statements/) (addresses by Donald Trump) and [The American Presidency Project](http://www.presidency.ucsb.edu/sou.php) (addresses by Richard Nixon, 1973). 

4. The methods used to extract country and region mentions from the texts are described in the [methods part of the article](https://www.nzz.ch/international/freund-und-feind-betrachtet-durch-die-brille-des-weissen-hauses-ld.1349175#subtitle-die-methodik-im-detail) and, in detail, in the scripts.

5. The scripts extract country and region names, calculate proportions relative to the total number of words of the addresses and visualize data.
   * The script `stateOfUnion.sh` extracts country and region names based on a modified and augmented version of the English regex-vector in the R-library `countrycode`. 
   * The script `stateOfUnion.R` creates different versions of the text corpus for the bash script, and processes and visualizes data extracted with the bash-script.
  
6. References
  * Data sources: [R-library `sotu`](https://github.com/statsmaths/sotu), the White House [https://www.whitehouse.gov/briefings-statements/], [The American Presidency Project](http://www.presidency.ucsb.edu/sou.php), see point 3. above
  * Code: R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)


We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.


