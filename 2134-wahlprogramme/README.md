# "Freedom" in decline in German election platforms

## Summary  
`platforms.py` calculates how often selected words such as "freedom" have been used between 1949 and 2021 per year and party, `platforms_most_common.py` identifies the most common words in German election platforms per party in 2021.

## Results  
Results based on these scripts were published in [this article](http://nzz.ch/ld.1644576).

## Data Sources
* [Konrad-Adenauer-Stiftung](https://www.kas.de/de/web/geschichte-der-cdu/wahlprogramme-und-slogans) (Union 1949-2021)
* [Friedrich-Ebert-Stiftung](https://www.fes.de/bibliothek/grundsatz-regierungs-und-wahlprogramme-der-spd-1949-heute) (SPD 1949-2021)
* [Friedrich-Naumann-Stiftung](https://www.freiheit.org/de/wahlprogramme-der-fdp-zu-den-bundestagswahlen) (FDP 1949-2021)
* [Heinrich-Böll-Stiftung](https://www.boell.de/de/navigation/archiv-4289.html) (Grüne 1980-2021)
* [Rosa-Luxemburg-Stiftung](https://www.rosalux.de/stiftung/historisches-zentrum/archiv/download) (Linke 1990-2021)
* [abgeordnetenwatch.de](https://www.abgeordnetenwatch.de/bundestag/wahl-2013/wahlprogramme) (AfD 2013), [afd.de](https://www.afd.de/wp-content/uploads/sites/111/2017/06/2017-06-01_AfD-Bundestagswahlprogramm_Onlinefassung.pdf) (AfD 2017), [afd.de](https://www.afd.de/wahlprogramm/) (AfD 2021)
* [abgeordnetenwatch.de](https://www.abgeordnetenwatch.de/bundestag/wahl-2013/wahlprogramme) (Freie Wähler 2013), [fw-bayern.de](https://www.fw-bayern.de/fileadmin/user_upload/Dokumente/07-25_Bundestagswahlprogramm.pdf) (Freie Wähler 2017), [freiewaehler.eu](https://www.freiewaehler.eu/dokumente/grundlagen/) (Freie Wähler 2021)
    
## Methods
* [Natural Language Toolkit `nltk`](https://www.nltk.org/)
* [The Hanover Tagger `HanTa`](https://github.com/wartaal/HanTa)
* Regex

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Visuals. We do not guarantee that the information therein is adequate, complete or up to date.
