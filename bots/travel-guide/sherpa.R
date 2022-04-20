#### Sherpa Travel Map ####

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(clipr)
library(jsonlite)
library(countrycode)

setwd("~/NZZ/NZZ Visuals - Dokumente/Projekte/_2022/2214_Sherpa_Travel_Guide")

## Vaccinated People

#data prep
sherpa_json <- fromJSON("mapEndpoint-fullyVaccinated.json", simplifyVector = TRUE)

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

sherpa_data$iso3 <- countrycode(sherpa_data$name, 'country.name', 'iso3c')

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

write_clip(sherpa_q)
head(sherpa_q)

browseURL("https://q.st.nzz.ch/editor/choropleth/e8023456bcfa4f8ea12f9a6114965a33")

#checking
sherpa_q %>% filter(is.na(policy))

## Non-vaccinated People

#data prep
sherpa_json_nv <- fromJSON("mapEndpoint-notVaccinated.json", simplifyVector = TRUE)

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

write_clip(sherpa_q_nv)
head(sherpa_q_nv)

browseURL("https://q.st.nzz.ch/editor/choropleth/85c353bb11cc62672a227f8869521189")

#checking
sherpa_q_nv %>% filter(is.na(policy))
