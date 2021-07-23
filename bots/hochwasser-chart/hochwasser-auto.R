#### Hochwasser CH und DE, manuelle Updates ####
# Automatisierte Skipte (Wasserstände CH) sind auf GitHub: 
# https://github.com/nzzdev/st-methods/tree/master/bots/hochwasser-chart

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
library(tidyverse)
library(sf)
library(geojsonio)
library(rvest)

# import helper functions
source("./helpers.R")

# Karte CH
bafu <- st_read("https://data.geo.admin.ch/ch.bafu.hydroweb-warnkarte_national/ch.bafu.hydroweb-warnkarte_national_de.json") %>%
  mutate(fill = case_when(ws.class == 1 ~ "#24B39C",
                          ws.class == 2 ~ "#EBBD22",
                          ws.class == 3 ~ "#E17A18",
                          ws.class == 4 ~ "#C31906",
                          ws.class == 5 ~ "#750F04",),
         stroke = fill,
         label = case_when(ws.class == 1 ~ "Gering",
                           ws.class == 2 ~ "Mässig",
                           ws.class == 3 ~ "Erheblich",
                           ws.class == 4 ~ "Gross",
                           ws.class == 5 ~ "Sehr gross"),
         "fill-opacity" = 0.8,
         "stroke-opacity" = 0.8) %>%
  arrange(ws.class) %>%
  st_transform(crs = 4326)

# in Q-CLI schreiben: Letzte volle Stunde als Stand
update_chart(id = "34937bf850cf702a02c3648cdf487a7f", 
             geojsonList = geojson_json(bafu),
             notes = gsub(" 0", " ", format(Sys.time(), format= "Stand: %d. %m., %H Uhr")))


# ## Wasserstände NRW und RP
# #NRW, mögliche Stationen hier prüfen: 
# 
# download.file("http://luadb.it.nrw.de/LUA/hygon/messwerte/messwerte.tar.gz", destfile ="messwerte.tar.gz")
# untar("messwerte.tar.gz")
# 
# rur <- read_delim("messwerte.txt", delim = ";") %>%
#   filter(Name == "Altenburg_1") %>% #hier den Stationsnamen auswählen. Übersicht: http://luadb.it.nrw.de/LUA/hygon/pegel.php?karte=nrw
#   rename("Messwert, Informationswert:" = "Messwert") %>%
#   mutate("1" = 105, #an Station anpassen
#          "2" = 135,
#          "3" = 170) %>%
#   select(-Datum, -Name) %>%
#   arrange(Datum_zeit)
# 
# update_chart(id = "34937bf850cf702a02c3648cdf9a7e53", 
#              data = rur,
#              notes = gsub(" 0", " ", format(max(as.POSIXct(rur$Datum_zeit)), format= "Stand: %d. %m., %H.%M Uhr")))
# 
# 
# #RP
# 
# #URL an Station anpassen, Übersicht (Fluss > Hauptpegel): http://www.hochwasser-rlp.de/
# url_rp <- "http://www.hochwasser-rlp.de/pegeluebersichten/einzelpegel/flussgebiet/mosel/darstellung/tabellarisch/pegel/TRIER"
# 
# html <- url_rp %>%
#   read_html() %>%
#   html_table()
# 
# mosel <- html[1] %>% 
#   as.data.frame() %>%
#   mutate(datetime = paste0(Datum, " ", Uhrzeit),
#          Meldehöhe = 600) %>% #an Station anpassen
#   select(datetime, Wasserstand.in.cm, Meldehöhe) %>%
#   rename("Messwert" = Wasserstand.in.cm)
# 
# write_clip(mosel)
# browseURL("https://q.st.nzz.ch/editor/chart/34937bf850cf702a02c3648cdf9c02bc")
# 
# 
# #Ahr
# url_ahr <- "http://www.hochwasser-rlp.de/weitere-pegel/einzelpegel/flussgebiet/rhein/teilgebiet/mittelrhein/pegel/ALTENAHR/darstellung/tabellarisch"
# 
# html_ahr <- url_ahr %>%
#   read_html() %>%
#   html_table()
# 
# ahr <- html_ahr[1] %>% 
#   as.data.frame() %>%
#   mutate(datetime = paste0(Datum, " ", Uhrzeit),
#          "Bisheriger Rekordwert (2016)" = 371) %>%
#   select(datetime, Wasserstand.in.cm, "Bisheriger Rekordwert (2016)") %>%
#   rename("Messwert" = Wasserstand.in.cm)
# 
# write_clip(ahr)
# browseURL("https://q.st.nzz.ch/editor/chart/bc7500f99eb2b7328406d6abbdd732eb")
