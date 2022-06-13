#### Sherpa Travel Map ####

#prep2
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(jsonlite)
library(countrycode)

# import helper functions
source("./helpers.R")

# get environment variables
sherpa_api_key <- Sys.getenv("SHERPA_API_KEY")

## Vaccinated People
download.file(url = paste0("https://requirements-api.joinsherpa.com/v2/map/international/CHE?language=de-DE&vaccinationStatus=FULLY_VACCINATED&key=",sherpa_api_key),
               destfile = "map-international-vaccinated-auto.json")

#data prep
sherpa_json <- fromJSON("map-international-vaccinated-auto.json", simplifyVector = TRUE)

#get clean dataset from json
sherpa_data <- sherpa_json$data %>%
  bind_rows() %>%
  select(name, entry, quarantine, testing) %>%
  gather(type, value, 2:4) %>%
  filter(value %in% c("0","1","2","3","4","5")) %>%
  mutate(value = as.numeric(value)) %>%
  spread(type, value) %>%
  mutate(policy = case_when(entry == 5 ~ "Einreise eingeschränkt",
                            entry != 5 & quarantine == 3 ~ "Quarantäne nötig",
                            entry < 5 & quarantine < 3 & testing >= 1 ~ "Test nötig",
                            TRUE ~ "Freie Einreise")) %>%
  filter(name != "Northern Cyprus") %>%
  select(1, 5)

sherpa_data$iso3 <- countrycode(sherpa_data$name, 'country.name', 'iso3c') #assign ISO codes for matching

# Q country list
q_wmap <- read_csv("q-wmap.csv")

#manual fixes
sherpa_data$iso3[sherpa_data$name == "South Sudan"] <- "SDS"
sherpa_data$iso3[sherpa_data$name == "Republic of Kosovo"] <- "KOS"

#join and clean for Q
sherpa_q <- sherpa_data %>%
  distinct() %>%
  right_join(q_wmap, by = c("iso3" = "ID")) %>%
  select(3,2) %>%
  arrange(iso3)

# auto
sherpa_note <- paste0('Einige international umstrittene Gebiete sind grau eingezeichnet. Mehr Details zu den Einreiseregimes',
                               ' <a href="https://apply.joinsherpa.com/map">hier</a>.<br>Stand:', 
                               gsub("\\b0(\\d)\\b", "\\1", format(Sys.Date(), format = "%d. %m. %Y")))

update_chart(id = "e8023456bcfa4f8ea12f9a6114965a33", 
             data = sherpa_q, 
             notes = sherpa_note)


#checking which countries do not have a value
sherpa_q %>% filter(is.na(policy))

## Non-vaccinated People

#data prep
sherpa_json_nv <- fromJSON("map-international-not_vaccinated.json", simplifyVector = TRUE)

sherpa_data_nv <- sherpa_json_nv$data %>%
  bind_rows() %>%
  select(name, entry, quarantine, testing) %>%
  gather(type, value, 2:4) %>%
  filter(value %in% c("0","1","2","3","4","5")) %>%
  mutate(value = as.numeric(value)) %>%
  spread(type, value) %>%
  mutate(policy = case_when(entry == 5 ~ "Einreise eingeschränkt",
                            entry != 5 & quarantine == 3 ~ "Quarantäne nötig",
                            entry < 5 & quarantine < 3 & testing >= 1 ~ "Test nötig",
                            TRUE ~ "Freie Einreise")) %>%
  filter(name != "Northern Cyprus") %>%
  select(name, policy)

sherpa_data_nv$iso3 <- countrycode(sherpa_data_nv$name, 'country.name', 'iso3c')

#manual fixes
sherpa_data_nv$iso3[sherpa_data_nv$name == "South Sudan"] <- "SDS"
sherpa_data_nv$iso3[sherpa_data_nv$name == "Republic of Kosovo"] <- "KOS"

#join and clean for Q
sherpa_q_nv <- sherpa_data_nv %>%
  distinct() %>%
  right_join(q_wmap, by = c("iso3" = "ID")) %>%
  select(3,2) %>%
  arrange(iso3)

#checking
sherpa_q_nv %>% filter(is.na(policy))

# auto
sherpa_note <- paste0('Einige international umstrittene Gebiete sind grau eingezeichnet. Mehr Details zu den Einreiseregimes',
                      ' <a href="https://apply.joinsherpa.com/map">hier</a>.<br>Stand:', 
                      gsub("\\b0(\\d)\\b", "\\1", format(Sys.Date(), format = "%d. %m. %Y")))

update_chart(id = "85c353bb11cc62672a227f8869521189", 
             data = sherpa_q_nv, 
             notes = sherpa_note)

