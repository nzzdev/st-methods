# Parlamentsdebatten-Corona

1. Content: Script that downloads all speeches in German, French and Italian in the Swiss Parliament since 1.1.2020 with the help of the package “Swissparl”. Analysis     of all speeches and of a subset of speeched that concern the coronavirus. Script generates csvs and graphics to help analyse the text. Information was used for the     article “” on NZZ.ch. 

2. Code is used for the analysis and the graphics of the following Article: 
  Die Grünen haben im Parlament am häufigsten mit dem Coronavirus politisiert: https://www.nzz.ch/visuals/ld.1606433
  
3. Sources: Text data of speeches in the Swiss parliament retrieved through the still unofficial and accordingly still undocumented Webservices of The Federal Assembly — The Swiss Parliament Swissparl. Dokumentation can be found here: https://github.com/zumbov2/swissparl. 

4. Script and Method:  First, all speeches in German, French and Italian in the Swiss Parliament since 1/1/2020  were downloaded via the API of the package Swissparl    from the website of the Swiss parliament parlament.ch. Since January 2020, there have been just over 10000 speeches in parliament in seven sessions (last available    text: 19/3/2021). The speeches of the Council Presidents have been filtered out. They mostly speak of organizational things and the text content is therefore not      relevant for the text analysis. If we now remove the speeches of the Federal Councilors (Bundesrat), we are left with just over 8000 speeches. Then two data sets      were worked on. On the one hand with  a dataset with all the speeches in parliament since January 2020, on the other hand with a subset     containing all speeches    that dealt with the coronavirus. The Corona texts were defined as follows: Corona, Covid, Sars or Coronavirus must appear at least once in the respective speech.

  Both dataframes were edited as follows: All so-called stop words were taken out in German, French and Italian (for example definite articles ('der', 'die', 'das'),    indefinite articles ('einer', 'eine', 'un', 'une'), conjunctions ('und', 'oder', 'doch', 'weil', 'mais') and adverbs ('immer', 'selten', 'souvent'). However, words    were also excluded that were not directly relevant for capturing the content of the text ('Bundesrat', 'commission', 'Artikel', 'Frau', 'Herr'. 'Minderheit').         Finally, the words were stemmed, i.e. only their respective root was considered (for example: Fahrer, fahren --> fahr). For the sake of readability, the entire words   are shown in the graphics. "Economie" then stands for the sum of économie, économique, etc., however.

  To determine which words occur relatively more often in a given corpus (here, the Corona corpus) than in a reference corpus, a preloaded function was used, called     the Textstat-Keyness function.

6. References:

* Data sources: Official Website of the Swiss Parliament, parlament.ch, linked in pieces/script accordingly. 
* Methods: linked above
* Tools: 
    R Core Team (2019), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Visuals. We do not guarantee that the information therein is adequate, complete or up to date.

