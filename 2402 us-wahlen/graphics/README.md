## Übersicht

Zuerst das Notebook `0 Data Preparation` mit den aktuellsten Daten laufen lassen. Damit wird ein TopoJSON erzeugt, das von den Vega-Specs verwendet wird.

Mit `Arrowmap` und `Bubblemap` werden die respektiven Karten erzeugt.

Im Notebook `Detailkarten` kann oben ein Staat angegeben werden. Es wird eine Pfeil- und Bubblekarte für diesen Staat erzeugt.

Alle erzeugten Vega-Specs finden sich in `temp/specs`


## Requirements

-   jupyterlab
-   pandas
-   geopandas
-   TopoJSON package: https://github.com/topojson/topojson
-   Vega CLI: https://github.com/vega/vega/tree/main/packages/vega-cli

