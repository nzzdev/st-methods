# Hochwasser-Karten
Dieses Script aktualisiert Temperaturdaten. Konkret:
* Temperatur in Zürich: https://q.st.nzz.ch/item/d0be298e35165ab925d72923352cad8b
* Waldbrandgefahr: https://q.st.nzz.ch/item/d0be298e35165ab925d72923355c5379

Zwei Cronjobs steuern die Grafiken
* `wetterereignisse_live_ch.yml` alle 15 Minuten
* `wetterereignisse_gefahrenkarten_ch.yml` alle zwei Stunden

Quellen:
* https://www.meteoschweiz.admin.ch/home/messwerte.html?param=messwerte-lufttemperatur-10min&station=SMA&chart=hour
* https://www.naturgefahren.ch/home/aktuelle-naturgefahren/waldbrand.html
  
Cronjob: `Jeweils fünf Minuten nach der vollen Stunde`

## Run
```python
python src/temperatur.py
python src/hitzegefahr.py
Q update-item
```