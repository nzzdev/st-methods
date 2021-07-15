#### GeoJson Hochwasser ####

rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen

library(tidyverse)
# library(geojsonio)
library(sf)
# library(clipr)
# library(jsonlite)
# library(zoo)


# import helper functions
source("./helpers.R")

#setwd("~/Downloads")

# de <- fromJSON("https://data.geo.admin.ch/ch.bafu.hydroweb-warnkarte_national/ch.bafu.hydroweb-warnkarte_national_de.json")
# bafu_notes <- paste0("Stand: ", str_sub(de$timestamp,1,3), " ", str_remove(str_sub(de$timestamp,4,6),"^0+"), " ", str_sub(de$timestamp,7,10), 
#                      ", ", str_sub(de$timestamp,12,13), " Uhr ", str_sub(de$timestamp,15,16))

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

bafu_notes <- paste0("Stand: ", format(Sys.Date(), format = "%d. %m. %Y"),", ", str_sub(Sys.time(), 12, 16), " Uhr")

update_chart(id = "34937bf850cf702a02c3648cdf487a7f", geojsonList = bafu, notes = bafu_notes)

# write_clip(geojson_json(bafu))
# browseURL("https://q.st.nzz.ch/editor/locator_map/34937bf850cf702a02c3648cdf487a7f")

# st_write(bafu, "bafu.geojson",delete_dsn = T)
# 
# library(renv)
# init()
# snapshot()
# restore()

