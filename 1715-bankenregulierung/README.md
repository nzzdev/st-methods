# 1715-bankenregulierung

1. These scripts scrape publications from the Basel Committee on Banking Supervision and perform text analyses based on them. 

2. Results based on these scripts were published in the following article:
  * [Am Anfang stand ein Bankenkollaps. Dann kam die Regulierung – und hörte nicht mehr auf](https://nzz.ch/ld.1304103)
  * Published 10.08.2017
  * The article shows how fast banking regulation is growing, how non-committal the rules are worded, and how the focus on risks and instruments has shifted over time.
  
3. Our database is a textcorpus that we constructed from all final publications of the type "standard", "guideline" or "sound practice" published on the website of the [Basel Committee on Banking Supervision](https://www.bis.org/bcbs/about/work_publication_types.htm).

4. Methods: We scraped PDF documents and transformed them to raw text. We then proceeded to measure the amount of text published over time and to analyze the frequency of occurrence of particular concepts and parts of speech overall and over time. Methods are described in more detail in the scripts and [here](https://nzz.ch/ld.1304103#subtitle-die-methodik-im-detail). 

5. Two scripts were used for the analysis:
  * The R-script bankingSupervision.R was used to scrape documents, transform them to raw text, count pages, words and characters and process and visualize data. 
  * The bash-script bankingSupervision.sh was used to create n-grams and count the occurrence of particular concepts and parts of speech.
  
6. References
  * Data source: [Publications of the Basel Committee on Banking Supervision](https://www.bis.org/bcbs/about/work_publication_types.htm)
  * Methods: [Our methods section](https://nzz.ch/ld.1304103#subtitle-die-methodik-im-detail)
  * Code: 
    * R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)
    * Free Software Foundation (2007), [Bash, Unix shell program](http://www.gnu.org/software/bash/)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.
