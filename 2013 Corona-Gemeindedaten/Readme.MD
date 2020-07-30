# Coronavirus cases in Swiss municipalities

This is where NZZ Visuals describes methods and code used for our articles. 
Each project has its own sub-repository with scripts and a README.md containing the following information:

1. This folder contains: 
 * Data on the per capita prevalence of confirmed coronavirus cases in the 2222 municipalities of Switzerland
 * A script that formats data provided by the Swiss Federal Office of Public Health (FOPH), see below

2. Results are published here:
  * [Die Schweizer Corona-Hochburgen: Diese Gemeinden haben die meisten Fälle pro Kopf verzeichnet](https://www.nzz.ch/ld.1564581)
  * Published on 2020-08-30
  * The article presents the data mentioned above, highlights some heavily affected municipalities, regions and cities and puts them into context.
  
3. Process: Dummy data (fictional values, real structure) provided by the FOPH was analysed using R. The existing dataset was formatted to get a value for every day and every municipality, then the values were separated into categories using Jenks natural breaks, and every municipality was assigned a category. The final dataset contains only date, municipality and category. The script was then used by the FOPH on the real data and the NZZ was only given the categories, not the precise figures. Additionally, a dataset was generated for cities (municipalities with over 10'000 residents) with the precise cumulative number of cases per 1000 inhabitants and given to the NZZ, this data was deemed to be in compliance with privacy rules by the FOPH.

4. Non-trivial methods used: Jenks natural breaks to better sort the values into groups that show different levels of affectedness 

6. References:
  * Data: FOPH, not published because of privacy regulations
  * Software:[R](http://www.R-project.org), [QGIS](http://www.qgis.org)

We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.
