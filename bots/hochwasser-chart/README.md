# Hochwasser-Karten
Dieses Script aktualisiert die Hochwassergrafiken. Es wird jenes CSV importiert, welches auch die Grafiken des Bafu antreiben.  
  
Cronjob: `Jeweils fünf Minuten nach der vollen Stunde, 6 - 20 Uhr`

## Grafiken
* Zürichsee: https://q.st.nzz.ch/item/6b50824faafb1db49507dbc8cc452e5c
* Limmat: https://q.st.nzz.ch/editor/chart/6b50824faafb1db49507dbc8cc476129
* Sihl: https://q.st.nzz.ch/item/6b50824faafb1db49507dbc8cc481e93
* Vierwaldstättersee: https://q.st.nzz.ch/editor/chart/34937bf850cf702a02c3648cdf22ffba

## Run
`python src/main.py`  
`Q update-item`