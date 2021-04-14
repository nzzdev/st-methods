# 2105-bundestagswahl

Summary: Downloads data from wahlrecht.de using the coalitions R package, performs averaging, calculates margins of error based on number of poll participants and party strength. Prepares polling data for publications in q.tools

Published here: [So stark verliert die Union nach der Korruptionsaffäre an Rückhalt – die neuesten Umfragen zur Bundestagswahl 2021](https://www.nzz.ch/ld.1605950) on 2021-03-17 (updated regularly)
  
Methods:
- Margin of error is calculated based on sample size, population size and party strength. Margins of error are of the last 30 days are averaged per party.
- Last 10 polls are used for averaging. If there are multiple polls on one day, the values are averaged again.
- Estimated seat number is extrapolated from percentages to current parliament size (709 seats).

References:
  * Data: [Wahlrecht.de](http://wahlrecht.de)
  * Software: [R](http://www.R-project.org), [Python](https://www.python.org/)
  * Methods: [MOE](https://goodcalculators.com/margin-of-error-calculator/)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.

---

[LOESS](https://en.wikipedia.org/wiki/Local_regression) method was removed on 2021-04-14 due to suboptimal regression at the most recent data points and comprehensibility issues.

Old code remains in the script (commented out) for reference
