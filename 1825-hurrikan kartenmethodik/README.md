# 1825-hurrikan kartenmethodik

1. This script leads, step by step, to a geojson-based hurricane-map that can be visualised, e.g., using our [NZZ-toolbox Q](https://www.nzz.ch/storytelling/tech/) as well as to .svg- and .pdf-versions of the map.

2. The rationale for our hurricane visualisation method is described in the following article:
  * [Warum die gängigste Hurrikan-Visualisierung problematisch ist – und wie es die NZZ stattdessen macht](https://nzz.ch/ld.1394033)
  * Published 22.08.2018
  * The article discusses the drawbacks of the most common hurricane visualisation method, shows alternatives and explains why we chose the current visualisation.

3. The data for our hurricane visualisations come from the [National Hurricane Center (NHC)](https://www.nhc.noaa.gov/) of the National Oceanic and Atmospheric Administration (NOAA). The NHC [GIS-procucts page](https://www.nhc.noaa.gov/gis/) offers data on [wind speed probabilities](https://www.nhc.noaa.gov/gis/archive_wsp.php?year=2018), the [advisory forecast track](https://www.nhc.noaa.gov/gis/archive_forecast.php?year=2018) and the [preliminary best track](https://www.nhc.noaa.gov/gis/archive_besttrack.php?year=2018) which are used for the visualisation.

4. The script explains where and how to obtain the most recent hurricane data, loads and processes these data for visualisation, writes out geojson files in order to show the hurricanes' past track, its predicted track, its wind speed probabilities for the next 120 hours and points labelled with dates. It creates one visualisation for the user to check and another that can be written out in .svg or .pdf format (the map layer obtained via ggmap can only be published [with certain restrictions](https://www.google.com/permissions/geoguidelines.html?hl=en&visit_id=1-636676747066554044-2011896175&rd=1)).

5. References
  * Data source: [National Hurricane Center / NOAA](https://www.nhc.noaa.gov/gis/)
  * Code: R Core Team (2017), [R: A language and environment for statistical computing. R Foundation for Statistical Computing, Vienna, Austria](http://www.R-project.org)


We exclude liability for any damages or losses that may arise from using the materials made available by NZZ Storytelling. We do not guarantee that the information therein is adequate, complete or up to date.
