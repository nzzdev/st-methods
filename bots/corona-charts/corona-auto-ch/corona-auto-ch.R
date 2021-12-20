#### Corona-Script SWITZERLAND (automated version) #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(jsonlite)
library(zoo)

# setwd for fixes
# setwd("~/Documents/GitHub/st-methods/bots/corona-charts")
# import helper functions
source("./helpers.R")

# read in additional data
pop <- read_csv("./corona-auto-ch/pop_kant.csv")

#### Update R eth estimate ####
eth <- read_csv("https://raw.githubusercontent.com/covid-19-Re/dailyRe-Data/master/CHE-estimates.csv") %>%
  filter(region == "CHE" & 
           data_type == "Confirmed cases" & 
           estimate_type == "Cori_slidingWindow") %>%
  add_row(date = Sys.Date()-1) %>%
  select(date, median_R_highHPD,median_R_lowHPD,median_R_mean) %>%
  filter(date > "2020-03-02")


eth_notes <- paste0("* 95%-Konfidenzintervall. Die Schätzung endet am ", format(nth(eth$date, -2), format = "%d. %m. %Y"),".")
eth_title <- case_when(nth(eth$median_R_mean, -2) < 0.7 ~ "Die Reproduktionszahl liegt deutlich unter 1",
                       nth(eth$median_R_mean, -2) > 0.7 & nth(eth$median_R_mean, -2) < 0.9 ~ "Die Reproduktionszahl liegt unter 1",
                       nth(eth$median_R_mean, -2) > 0.9 & nth(eth$median_R_mean, -2) < 1.1  ~ "Die Reproduktionszahl liegt etwa bei 1",
                       nth(eth$median_R_mean, -2) > 1.1 & nth(eth$median_R_mean, -2) < 1.3  ~ "Die Reproduktionszahl liegt über 1",
                       nth(eth$median_R_mean, -2) > 1.3 ~ "Die Reproduktionszahl liegt deutlich über 1")

colnames(eth) <- c("Datum", "", "Unsicherheitsbereich*", "Median")

#q-cli update
update_chart(id = "d84021d6716b1e848bd91a20e2b63cb0", 
             data = eth, 
             notes = eth_notes,
             title = eth_title)

#### Update R eth estimate cantons ####

## 10 biggest: ZH, BE, VD, AG, SG, GE, LU, TI, VS, FR

eth_cantons <- read_csv("https://raw.githubusercontent.com/covid-19-Re/dailyRe-Data/master/CHE-estimates.csv") %>%
  filter(region %in% c("BE","ZH","VD","AG","SG","GE","LU", "TI","VS", "FR")) %>%
  filter(data_type == "Confirmed cases" & estimate_type == "Cori_slidingWindow") %>%
  group_by(region) %>%
  filter(date == last(date)) %>%
  ungroup() %>%
  left_join(pop[,1:2], by = c("region" = "ktabk")) %>%
  select(kt, median_R_highHPD,median_R_lowHPD,median_R_mean) %>%
  arrange(desc(median_R_mean))

eth_cantons_title <- paste0("Der Kanton ", eth_cantons[1,1], " verzeichnet den höchsten R-Wert")
eth_cantons_notes <- paste0("Die Daten liegen in einem 95%-Konfidenzintervall. Wir zeigen nur die R-Werte für die zehn grössten Kantone.",
                            " In kleinen Kantonen ist der Unsicherheitsbereich teilweise sehr gross, so dass keine verlässlichen Aussagen möglich sind.",
                            " Die neusten Schätzungen der Kantone liegen in der Regel einige Tage hinter der nationalen Schätzung.<br> Stand: ",
                            gsub("\\b0(\\d)\\b", "\\1", format(nth(eth$Datum, -2)-4, format = "%d. %m. %Y")))

colnames(eth_cantons) <- c("Kanton", "", "Unsicherheitsbereich", "Median")

#q-cli update
update_chart(id = "f649302cbf7dd462f339d0cc35d9695a", 
             data = eth_cantons, 
             notes = eth_cantons_notes,
             title = eth_cantons_title)

#### Update UZH survey ####

uzh_raw <- read_csv("https://covid-norms.ch/wp-content/uploads/data/complete.csv") %>%
  mutate(Woche = paste0(dYear, "-W", KW)) %>%
  filter(Wert == "prop") %>%
  select(Woche, f300_1_Geimpft, f300_1_Zustimmung, f300_1_Neutral, f300_1_Ablehnung) %>%
  mutate_at(2:5, .funs = funs(.*100)) %>%
  rename(Geimpfte = f300_1_Geimpft, Impfwillige = f300_1_Zustimmung, Unentschlossene = f300_1_Neutral, Ablehnende = f300_1_Ablehnung)

# write
update_chart(id = "26356a1918b687a3e1a7ff0d5e0b9675", 
             data = uzh_raw)

#### Update BAG data ####
# Load Data Schema

bag_data <- fromJSON('https://www.covid19.admin.ch/api/data/context')

# data gathering

bag_cases <- read_csv(bag_data$sources$individual$csv$daily$cases)%>% 
  select("geoRegion", "datum", "entries", "sumTotal", "pop") %>%
  filter(datum != max(datum)) #exclude today, because new cases will not be there

bag_cases_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$cases) %>%
  select("altersklasse_covid19", "geoRegion", "datum", "entries", "sumTotal")

bag_deaths <- read_csv(bag_data$sources$individual$csv$daily$death) %>%
  select("geoRegion", "datum", "entries", "sumTotal") %>%
  filter(datum != max(datum)) #exclude today

bag_hosps <- read_csv(bag_data$sources$individual$csv$daily$hosp) %>%
  select("geoRegion", "datum", "entries", "sumTotal") %>%
  filter(datum != max(datum)) #exclude today

bag_hosp_cap <- read_csv(bag_data$sources$individual$csv$daily$hospCapacity) %>%
  select("geoRegion", "date", "ICUPercent_AllPatients", "ICUPercent_NonCovid19Patients",
         "ICUPercent_Covid19Patients", "ICUPercent_FreeCapacity", 
         "TotalPercent_AllPatients", "TotalPercent_NonCovid19Patients", 
         "TotalPercent_Covid19Patients", "TotalPercent_FreeCapacity") %>%
  filter(date != max(date)) #exclude today

bag_tests <- read_csv(bag_data$sources$individual$csv$daily$test) %>%
  select("geoRegion", "datum", "entries", "pos_anteil", "sumTotal", "pop")

bag_testPcrAntigen <- read_csv(bag_data$sources$individual$csv$daily$testPcrAntigen) %>% 
  select("geoRegion", "datum", "entries", "nachweismethode", "pos_anteil")

bag_cert <- read_csv(bag_data$sources$individual$csv$daily$covidCertificates) %>%
  filter(type_variant != 'all') %>%
  select("geoRegion", "date", "type_variant", "sumTotal")

bag_var <- read.csv(bag_data$sources$individual$csv$daily$virusVariantsWgs)%>%
  filter(geoRegion == 'CHFL') %>%
  select("variant_type", "date", "prct", "prct_lower_ci", "prct_upper_ci", "prct_mean7d", "entries")


#### Update Overview (Zahlenübersicht oben)

tmp_cases <- read_csv(bag_data$sources$individual$csv$daily$cases) %>%
  filter(datum == max(datum), geoRegion == 'CHFL')

new_infections <- paste0("+ ", tmp_cases$entries_diff_last)

tmp_hosp <- read_csv(bag_data$sources$individual$csv$daily$hosp) %>%
  filter(datum == max(datum), geoRegion == 'CHFL')

new_hosp <- paste0('+ ', tmp_hosp$entries_diff_last)

tmp_death <- read_csv(bag_data$sources$individual$csv$daily$death) %>%
  filter(datum == max(datum), geoRegion == 'CHFL')

new_death <- paste0('+ ', tmp_death$entries_diff_last)

# ch_vacc_adm <- read_csv(bag_data$sources$individual$csv$vaccDosesAdministered)
# 
# doses_yesterday = filter(ch_vacc_adm, date == max(date - 1), geoRegion == 'CHFL')$sumTotal
# doses_today = filter(ch_vacc_adm, date == max(date), geoRegion == 'CHFL')$sumTotal
# newDoses = paste0('+ ', doses_today - doses_yesterday)

df_overview <- data.frame(
  Indikator = c("Neuinfektionen", "Hospitalisierungen", "Todesfälle"),
  Wert = c(new_infections, new_hosp, new_death)
)

subtitle <- paste0("Neue Meldungen des Bundesamtes für Gesundheit vom ", 
                   gsub("\\b0(\\d)\\b", "\\1", format(max(tmp_death$datum), format = "%d. %m. %Y")),
                   " für die Schweiz und Liechtenstein")

# write
update_chart(id = "2e1103d436e7d4452fc9a58ec507bb2e", 
             data = df_overview,
             subtitle = subtitle)

# Total cases in CH since 2020-02-24 and recovery calculation
bag_total <- merge(bag_cases, bag_deaths, by = c("geoRegion", "datum")) %>%
  filter(geoRegion == 'CHFL') %>%
  mutate(Infizierte = sumTotal.x -sumTotal.y) %>%
  rename("Tote" = `sumTotal.y`) %>%
  select(datum, Infizierte, Tote) %>%
  mutate(`Genesene (Schätzung)` = ((lag(Infizierte,14, default = 0)) * 0.75) + 
           ((lag(Infizierte ,21, default = 0)) * 0.10) + 
           ((lag(Infizierte,28, default = 0)) * 0.10) +
           ((lag(Infizierte,42, default = 0)) * 0.05)) %>%
  mutate(`gegenwärtig Infizierte` = Infizierte-`Genesene (Schätzung)`) %>%
  select("datum", "Tote", "gegenwärtig Infizierte", "Genesene (Schätzung)")

#bag_total_title <- paste0("Über ",str_sub(sum(tail(bag_total[,2:4], 1),3),1,3), " 000 bestätigte Infektionen in der Schweiz")

#q-cli update
update_chart(id = "3209a77a596162b06346995b10896863", 
             data = bag_total)


#Rolling average of cases
bag_cases_ravg <- bag_cases %>%
  filter(geoRegion == 'CHFL', datum <= last(datum)-2) %>%
  mutate(ravg_cases = round(rollmean(entries, 7, fill = 0, align = "right"),0)) %>%
  select(datum, ravg_cases) 

#q-cli update
update_chart(id = "93b53396ee7f90b1271f620a0472c112", data = bag_cases_ravg)

# Tests (Antigen and PCR), absolute number

bag_testPcrAntigen_abs <- bag_testPcrAntigen %>% 
  filter(datum > "2020-11-01", geoRegion == 'CHFL') %>%
  select(datum, entries, nachweismethode) %>%
  spread(nachweismethode, entries) %>%
  mutate("Antigen-Schnelltest" = round(rollmean(Antigen_Schnelltest, 7, fill = 0, align = "right"), 1), 
         "PCR-Test" = round(rollmean(PCR, 7, na.pad = TRUE, align = "right"), 1)) %>%
  select(datum, `Antigen-Schnelltest`, `PCR-Test`) %>%
  filter(`Antigen-Schnelltest` + `PCR-Test` > 0) %>%
  drop_na() 

#q-cli update
update_chart(id = "fe58121b9eb9cbc28fb71b8810a7b573", data = bag_testPcrAntigen_abs)


# Positivity rate (PCR and Antigen)
bag_tests_pct <- bag_testPcrAntigen %>%
  filter(datum > "2020-11-01", geoRegion == 'CHFL') %>%
  group_by(nachweismethode) %>%
  mutate(pct = round(rollmean(pos_anteil, 7, na.pad = TRUE, align = "right"), 1)) %>%
  select(nachweismethode, datum, pct) %>%
  spread(nachweismethode, pct) %>%
  drop_na()  %>%
  rename("Antigen-Schnelltest" = Antigen_Schnelltest, "PCR-Test" = PCR) %>%
  add_column("WHO-Zielwert" = 5)

#q-cli update
update_chart(id = "e18ed50b4fad7ada8063e3a908eb77ac", data = bag_tests_pct)

# Age distribution of cases, weekly
bag_age  <- bag_cases_age %>%
  filter(!is.na(datum), altersklasse_covid19 != "Unbekannt", geoRegion == "CHFL") %>%
  mutate(datum = paste0(substr(datum, 1, 4), "-W", substr(datum, 5, 6))) %>%
  select(datum, altersklasse_covid19, entries) %>%
  spread(altersklasse_covid19, entries) %>%
  mutate(`0-19` = `0 - 9` +  `10 - 19`,
         `20-39` = `20 - 29` +  `30 - 39`,
         `40-59` = `40 - 49` +  `50 - 59`,
         `60-79` = `60 - 69` +  `70 - 79`) %>%
  select(datum, `0-19`,`20-39`, `40-59`, `60-79`, `80+`) %>%
  slice(1:n()-1) #incomplete week results, can be removed by Wednesday

# make relative values 
bag_age[2:6] <- bag_age[2:6]/rowSums(bag_age[2:6])*100

#q-cli update
update_chart(id = "cbef3c928fa4c500c77a2a561e724af6", data = bag_age)


# Kantone 14 Tage Choropleth
bag_kanton_choro <- bag_cases %>%
  filter(!is.na(datum), datum >= max(datum)-13, geoRegion != "CHFL", geoRegion != "CH", geoRegion != "FL") %>%
  group_by(geoRegion, pop) %>%
  summarise(sum = sum(entries), .groups = "drop") %>%
  mutate(per100k = round(100000*sum/pop, 0)) %>%
  arrange(geoRegion) %>%
  select(geoRegion, per100k)

bag_kanton_choro_notes <- paste0("Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(bag_cases$datum), format = "%d. %m. %Y")))

update_chart(id = "a2fc71a532ec45c64434712991efb41f", data = bag_kanton_choro, notes = bag_kanton_choro_notes)


### Hospitalisierungen und Todesfälle

# Absolut 
roll_ch_bag_death_hosp <- bag_cases %>%
  full_join(bag_deaths, by = c("geoRegion", "datum")) %>%
  full_join(bag_hosps, by = c("geoRegion", "datum")) %>%
  filter(datum >= "2020-02-28" & datum <=  last(datum)-2, geoRegion == 'CHFL')  %>%
  mutate(entries.y = replace_na(entries.y, 0),
         hosp_roll = rollmean(entries,7,fill = 0, align = "right"),
         death_roll = rollmean(entries.y,7,fill = 0, align = "right")) %>%
  select(datum, hosp_roll, death_roll) %>%
  rename(Hospitalierungen = hosp_roll, Todesfälle = death_roll)

update_chart(id = "2e86418698ad77f1247bedf99b771e99", data = roll_ch_bag_death_hosp)


### Dashboard
#roll_ch_bag_hosp <- roll_ch_bag_death_hosp %>%
 # select(datum, Hospitalierungen) %>%
  #filter(datum > '2020-10-01') %>%
  #rename(date = datum, value = Hospitalierungen)

#roll_ch_bag_death <- roll_ch_bag_death_hosp %>%
 # select(datum, `Todesfälle`) %>%
  #filter(datum > '2020-10-01') %>%
  #rename(date = datum, value = `Todesfälle`)


#roll_ch_bag_cases_trend <- bag_cases_ravg %>%
 # mutate(pct_of_max = (ravg_cases*100)/max(ravg_cases, na.rm = T)) %>%
  #mutate(diff_pct_max = ravg_cases - lag(ravg_cases, 14, default = 0)) %>%
  #mutate(trend = case_when 
  #       (diff_pct_max > 5 ~ 'steigend', 
   #        diff_pct_max < -5 ~ 'fallend',
    #       TRUE ~ 'gleichbleibend',)) 

#roll_ch_bag_hosp_trend <- roll_ch_bag_hosp %>%
 # mutate(pct_of_max = (value*100)/max(value, na.rm = T)) %>%
  #mutate(diff_pct_max = value - lag(value, 14, default = 0)) %>%
  #mutate(trend = case_when 
        # (diff_pct_max > 5 ~ 'steigend', 
         #  diff_pct_max < -5 ~ 'fallend',
          # TRUE ~ 'gleichbleibend',)) 

#roll_ch_bag_death_trend <- roll_ch_bag_death %>%
 # mutate(pct_of_max = (value*100)/max(value, na.rm = T)) %>%
  #mutate(diff_pct_max = value - lag(value, 14, default = 0)) %>%
  #mutate(trend = case_when 
    #     (diff_pct_max > 5 ~ 'steigend', 
     #      diff_pct_max < -5 ~ 'fallend',
      #     TRUE ~ 'gleichbleibend',)) 

#forJson <- data.frame(indicatorTitle = "Neue Spitaleintritte",
 #                     indicatorSubtitle = "7-Tage-Schnitt, seit dem 1. Oktober 2020",
  #                    value = tmp_hosp$entries_diff_last,
   #                   color = "#24b39c",
    #                  trend = last(roll_ch_bag_hosp_trend$trend))

#forJson$sparkline <- list(roll_ch_bag_hosp)


#forJson_2 <- data.frame(indicatorTitle = "Neuinfektionen",
 #                       value = tmp_cases$entries_diff_last,
  #                      color = "#e66e4a",
   #                     trend = last(roll_ch_bag_cases_trend$trend))

#forJson_3 <- data.frame(indicatorTitle = "Neue Todesfälle",
 #                       value = tmp_death$entries_diff_last,
  #                      color = "#05032d",
   #                     trend = last(roll_ch_bag_death_trend$trend))

#z <- toJSON(rbind_pages(list(forJson, forJson_2, forJson_3)), pretty = T)

#assets <- list(
 # list(
  #  name = "jsonFiles",
   # files = list("./dashboard.json")
  #)
#)


#q-cli update
#update_chart(id = "499935fb791197fd126bda721f15884a",
 #            asset.groups = assets)




# Todesfälle und Hospitalisierungen absolut nach Altersklasse 

bag_deaths_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$death) %>%
  select("altersklasse_covid19", "geoRegion", "datum", "entries", "sumTotal") %>%
  mutate(KW = substr(datum, 5, 6), year = substr(datum, 1, 4))

bag_hosp_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$hosp) %>%
  select("altersklasse_covid19", "geoRegion", "datum", "entries", "sumTotal")  %>%
  mutate(KW = substr(datum, 5, 6), year = substr(datum, 1, 4))

bag_age_deaths  <- bag_deaths_age %>%
  filter(!is.na(datum), altersklasse_covid19 != "Unbekannt", geoRegion == 'CHFL', (year >= '2021' | (year == '2020' & KW >= '52' ) )) %>%
  mutate(datum = paste0(year, "-W", KW)) %>%
  select(datum, altersklasse_covid19, entries) %>%
  spread(altersklasse_covid19, entries) %>%
  mutate(`0–59` = `0 - 9` +  `10 - 19` + `20 - 29` +  `30 - 39` + `40 - 49` +  `50 - 59`, `60–79` = `60 - 69` +  `70 - 79`) %>%
  select(datum, `0–59`,`60–79`, `80+`) 

update_chart(id = "ec163329f1a1a5698ef5d1ee7587b3d6", data = bag_age_deaths)


bag_age_hosps  <- bag_hosp_age %>%
  filter(!is.na(datum), altersklasse_covid19 != "Unbekannt", geoRegion == 'CHFL', (year >= '2021' | (year == '2020' & KW >= '52' ) )) %>%
  mutate(datum = paste0(year, "-W", KW)) %>%
  select(datum, altersklasse_covid19, entries) %>%
  spread(altersklasse_covid19, entries) %>%
  mutate(`0–19` = `0 - 9` +  `10 - 19`,
         `20-39` = `20 - 29` +  `30 - 39`,
         `40-59` =  `40 - 49` +  `50 - 59`, 
         `60–79` = `60 - 69` +  `70 - 79`) %>%
  select(datum, `0–19`, `20-39`, `40-59`, `60–79`, `80+`) %>%
  slice(1:n()-1) #incomplete week results

update_chart(id = "b3423b05ea50c39f8da718719ec3d161", data = bag_age_hosps)

### Intensivbetten 

bag_hosp_cap <- subset(read_csv(bag_data$sources$individual$csv$daily$hospCapacity), type_variant == 'fp7d',
                       select = c("geoRegion", "date", "ICU_AllPatients", "ICU_Covid19Patients", "ICU_Capacity",
                                  "ICUPercent_AllPatients", "ICUPercent_NonCovid19Patients", "ICUPercent_Covid19Patients",
                                  "ICUPercent_FreeCapacity")) %>%
  mutate("Freie Betten" = ICU_Capacity - ICU_AllPatients, "Andere Patienten" = ICU_AllPatients - ICU_Covid19Patients)


names(bag_hosp_cap) <- c('geoRegion', 'datum', "Auslastung", 
                         "Patienten mit Covid-19", "Kapazität",
                         "Auslastung in %", 
                         "Andere Patienten in %", "Patienten mit Covid-19 in %",
                         "Freie Betten in %", "Freie Betten", "Andere Patienten")

bag_hosp_cap_ch <- subset(bag_hosp_cap, geoRegion == 'CH', select = c('datum', 'Patienten mit Covid-19', 'Andere Patienten', 'Freie Betten')) 


update_chart(id = "bd30a27068812f7ec2474f10e427300c", data = bag_hosp_cap_ch)


bag_hosp_cap_cantons <- bag_hosp_cap %>%
  filter(datum == max(datum), geoRegion != 'CHFL' & geoRegion != 'CH' & geoRegion != 'FL') %>%
  select('geoRegion', 'Auslastung', 'Kapazität', 'Patienten mit Covid-19', 'Andere Patienten', 'Freie Betten')

bag_hosp_cap_regions <- bag_hosp_cap_cantons %>%
  mutate(region = case_when(geoRegion %in% c("GE", "VS", "VD") ~ "Genferseeregion",
                            geoRegion %in% c("BE", "SO", "FR", "NE", "JU") ~ "Espace Mittelland",
                            geoRegion %in% c("BS", "BL", "AG") ~ "Nordwestschweiz",
                            geoRegion == "ZH" ~ "Zürich",
                            geoRegion %in% c("SG", "TG", "AI", "AR", "GL", "SH", "GR") ~ "Ostschweiz",
                            geoRegion %in% c("UR", "SZ", "OW", "NW", "LU", "ZG") ~ "Zentralschweiz",
                            geoRegion == "TI" ~ "Tessin")) %>%
  group_by(region) %>% 
  drop_na()  %>%
  summarise(Auslastung = sum(Auslastung),
            "Kapazität" = sum(`Kapazität`),
            "Patienten mit Covid-19" = sum(`Patienten mit Covid-19`),
            "Andere Patienten" = sum(`Andere Patienten`),
            "Freie Betten" = sum(`Freie Betten`)) %>%
  mutate_at((4:6), .funs = list(~ .*100/`Kapazität`)) %>%
  mutate(across(4:6, round, 1)) %>%
  select(1, 4:6) %>%
  arrange(desc(`Patienten mit Covid-19`))

# percentages for notes

bag_hosp_cap_regions_notes <- paste0("Schweizweit sind derzeit etwa ", 
                                      last(subset(bag_hosp_cap, geoRegion == 'CH', select = c('datum', 'Auslastung in %'))$'Auslastung in %' ), 
                                      " Prozent der Intensivbetten belegt. Die Covid-19-Patienten machen derzeit rund ", 
                                      round(100*last(subset(bag_hosp_cap, geoRegion == 'CH', select = c('datum', 'Patienten mit Covid-19'))$'Patienten mit Covid-19') / 
                                              last(subset(bag_hosp_cap, geoRegion == 'CH', select = c('datum', 'Auslastung'))$'Auslastung')),
                                      " Prozent der Patienten aus.<br>Stand: ",
                                     gsub("\\b0(\\d)\\b", "\\1", format(max(bag_hosp_cap$datum), format = "%d. %m. %Y")))


update_chart(id = "e7ab74f261f39c7b670954aaed6de280", data = bag_hosp_cap_regions, notes = bag_hosp_cap_regions_notes)

#### Bezirke Cases ####

bag_cases_bez <- read_csv(bag_data$sources$individual$csv$extraGeoUnits$cases$biweekly) %>%
  select("geoRegion", "period_end_date", "inzCategoryNormalized") %>%
  filter(period_end_date == max(period_end_date)) %>%
  filter(grepl('BZRK', geoRegion)) %>%
  mutate(geoRegion = as.numeric(str_sub(geoRegion,5,9))) %>%
  select(-period_end_date) %>%
  arrange(geoRegion)

bag_cases_bez_dates <- read_csv(bag_data$sources$individual$csv$extraGeoUnits$cases$biweekly) %>%
  filter(period_end_date == max(period_end_date), geoRegion == "CH") %>%
  select(period_start_date, period_end_date)

bag_cases_bez_notes <- paste0("Zeitraum: ", 
                              gsub("\\b0(\\d)\\b", "\\1", format(bag_cases_bez_dates$period_start_date, format = "%d. %m.")),
                              " bis ",
                              gsub("\\b0(\\d)\\b", "\\1", format(bag_cases_bez_dates$period_end_date, format = "%d. %m. %Y")),
                              ". Die Zahlen werden alle 2 Wochen aktualisiert.")

update_chart(id = "1dc855a085bcadbf7a93ebf5b584336e", 
             data = bag_cases_bez, 
             notes = bag_cases_bez_notes)

### Variants ###

bag_var_omikron <- bag_var %>%
  mutate(date = as.Date(date)) %>%
  filter(variant_type == 'B.1.1.529') %>%
  drop_na(prct) %>%
  mutate(prct_7 = rollmean(prct, 7, fill = NA, align = "right"),
         prct_lower_7 = rollmean(prct_lower_ci, 7, fill = NA, align = "right"),
         prct_upper_7 = rollmean(prct_upper_ci, 7, fill = NA, align = "right")) %>%
  filter(date >= '2021-11-01' & date <= last(date)) %>%
  select(date, prct_lower_7, prct_upper_7, prct_7 ) %>%
  filter(date >= '2021-04-01') %>%
  rename(" " = "prct_lower_7", "Unsicherheit*" = "prct_upper_7", "Anteil der Omikron-Variante" = "prct_7")

update_chart(id = "396fd1e1ae7c6223217d80a9c5417e1f",
             data = bag_var_omikron)

bag_var_all <- bag_var %>%
  mutate(date = as.Date(date)) %>%
  drop_na(prct) %>%
  filter(variant_type != "all_sequenced") %>%
  mutate(var = case_when(variant_type == "B.1.1.7"~ "Alpha",
                         variant_type == "B.1.617.2" ~ "Delta",
                         variant_type == "B.1.1.529" ~ "Omikron",
                         variant_type == "other_lineages" ~ "Urtyp/andere Varianten",
                         TRUE ~ "Weitere «relevante Virusvarianten»*")) %>%
  group_by(date, var) %>%
  summarise(prct = sum(prct)) %>%
  group_by(var) %>%
  mutate(prct_7 = round(rollmean(prct, 7, fill = NA, align = "right"),1)) %>%
  select(date, var, prct_7) %>%
  spread(var,prct_7) %>%
  mutate(`Urtyp/andere Varianten` = round(100-(Alpha+Delta+Omikron+`Weitere «relevante Virusvarianten»*`),1)) %>%
  filter(date >= "2020-10-10") %>%
  select(date, Alpha, Delta, Omikron, `Weitere «relevante Virusvarianten»*`, `Urtyp/andere Varianten`)

update_chart(id = "396fd1e1ae7c6223217d80a9c5421999",
             data = bag_var_all)

### Certificates ###

bag_cert <- bag_cert %>% 
  select(-geoRegion) %>%
  spread(type_variant, sumTotal) %>%
  rename('Genesen' = 'recovered', 'Getestet' = 'tested', 'Geimpft' = 'vaccinated')

update_chart(id = "15326b5086f1007b7c67825700c2d149", data = bag_cert)


#### CH Vaccinations ####
# update on TUE and FRI, check if new BAG vacc data are there, if not read in again later

#get latest bag figures
ch_vacc_delrec <- read_csv(bag_data$sources$individual$csv$vaccDosesDelivered) %>% 
  select(date,geoRegion, pop, type, sumTotal)

ch_vacc_adm <- read_csv(bag_data$sources$individual$csv$vaccDosesAdministered) %>% 
  select(date,geoRegion, pop, type, sumTotal)

ch_vacc_doses <- rbind(ch_vacc_delrec, ch_vacc_adm)

ch_vacc_persons <- read_csv(bag_data$sources$individual$csv$vaccPersonsV2) %>%
  filter(age_group == "total_population") %>%
  select(geoRegion, pop, date, type, sumTotal) %>%
  drop_na()

ch_vacc_manuf <- read_csv(bag_data$sources$individual$csv$weeklyVacc$byVaccine$vaccDosesAdministered) %>%
  filter(geoRegion == "CHFL") %>%
  select(date, vaccine, sumTotal) %>%
  spread(vaccine, sumTotal) %>%
  rename('COVID-19 Vaccine Moderna® (Moderna)' = 'moderna', 'Comirnaty® (Pfizer / BioNTech)' = 'pfizer_biontech')

ch_inf_vacc <- read_csv(bag_data$sources$individual$csv$daily$casesVaccPersons) %>%
#  filter(vaccine == "all") %>%
  mutate(type = "Infektionen")

ch_hosp_vacc <- read_csv(bag_data$sources$individual$csv$daily$hospVaccPersons) %>%
#  filter(vaccine == "all") %>%
  mutate(type = "Spitaleintritte")

ch_death_vacc <- read_csv(bag_data$sources$individual$csv$daily$deathVaccPersons) %>%
#  filter(vaccine == "all") %>%
  mutate(type = "Todesfälle")

# ch_inf_vacc_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$casesVaccPersons) %>%
#   filter(vaccine == "all")
# 

ch_hosp_vacc_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$hospVaccPersons) %>% 
  filter(vaccine == "all")

# 
# ch_death_vacc_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$casesVaccPersons) %>%
#   filter(vaccine == "all")

#### Impfdurchbrüche ####
# By Manuf. - one-off
# id_total2 <- rbind(ch_inf_vacc, ch_hosp_vacc, ch_death_vacc) %>%
#   group_by(type, vaccination_status, vaccine) %>%
#   summarise(sum = sum(entries), pop = max(pop)) %>%
#   mutate(per100k = 100000*sum/pop)

id_total <- rbind(ch_hosp_vacc, ch_death_vacc) %>%
  filter(vaccine == "all") %>%
  filter(date == max(date), vaccination_status %in% c("fully_vaccinated","partially_vaccinated")) %>%
  select(type, vaccination_status, sumTotal) %>%
  spread(vaccination_status, sumTotal) %>%
  rename("Typ" = 1, "Vollständig geimpft" = 2, "Teilweise geimpft" = 3)

update_chart(id = "ab97925bcc5055b33011fb4d3320012a", 
             data = id_total, 
             notes = paste0("Die Zahl der gemeldeten Infektionen bei Geimpften wird vom BAG nicht mehr publiziert,",
                            " da die Daten nicht aussagekräftig sind.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(ch_hosp_vacc$date), format = "%d. %m. %Y"))))


id_hist <- rbind(ch_hosp_vacc, ch_death_vacc) %>%
  filter(vaccine == "all") %>%
  filter(date >= "2021-07-01") %>%
  group_by(type, vaccination_status) %>%
  summarise(entries = sum(entries)) %>%
  spread(vaccination_status, entries) %>%
  select("Typ" = 1, "Vollständig geimpft" = 2, "Teilweise geimpft" = 4, "Unbekannt" = 5, "Ungeimpft" = 3)

id_hist[2:5] <- round(id_hist[2:5]/rowSums(id_hist[2:5])*100,1)

update_chart(id = "c041757a38ba1d4e6851aaaee55c6207", 
             data = id_hist, 
             notes = paste0("Der Zeitraum ab 1. Juli wurde so gewählt, weil zu diesem Zeitpunkt bereits eine relativ hohe Impfquote erreicht war. <br>Stand: ",
                            gsub("\\b0(\\d)\\b", "\\1", format(max(ch_hosp_vacc$date), format = "%d. %m. %Y"))))

# id_hosp_line <- ch_hosp_vacc %>%
#   filter(vaccine == "all") %>%
#   select(date, vaccination_status, entries) %>%
#   spread(vaccination_status, entries) %>%
#   mutate_at(2:5, .funs = funs(rollmean(.,7,NA, align = "right"))) %>%
#   filter(date >= "2021-07-01") %>%
#   select("Datum" = 1, "Vollständig geimpft" = 2, "Teilweise geimpft" = 4, "Unbekannt" = 5, "Ungeimpft" = 3) %>%
#   head(-2)

id_hosp_line_weekly_pc_60 <- ch_hosp_vacc_age %>%
  filter(altersklasse_covid19 %in% c("60 - 69", "70 - 79", "80+"), 
         vaccination_status != "unknown" & vaccination_status != "partially_vaccinated",
         date >= "202126") %>%
  select(date, altersklasse_covid19, vaccination_status, entries, pop) %>%
  group_by(date, vaccination_status) %>%
  summarise(entries = sum(entries), pop = sum(pop)) %>%
  mutate(per100k = 100000*entries/pop) %>%
  select(-entries, -pop) %>%
  spread(vaccination_status, per100k) %>%
  mutate(date = paste0(str_sub(date, 1,4), "-W", str_sub(date, 5,6)))

names(id_hosp_line_weekly_pc_60) <- c("date", "Vollständig geimpft", "Ungeimpft")

if (weekdays(Sys.Date()) %in% c("Monday", "Montag", "Dienstag", "Tuesday")){
  id_hosp_line_weekly_pc_60 <- id_hosp_line_weekly_pc_60 %>%
    head(-1)
}

update_chart(id = "6069088c960d0f055227f901b974637f", 
             data = id_hosp_line_weekly_pc_60)

id_rel_age <- ch_hosp_vacc_age %>% 
  select(1:4,6) %>%
  filter(date %in% tail(unique(ch_hosp_vacc_age$date), 3)) %>%
  group_by(altersklasse_covid19, vaccination_status) %>%
  summarise(entries = sum(entries), pop = first(pop)) %>%
  mutate(per100k = round(100000*entries/pop, 1))

id_rel_age_q <- id_rel_age %>%
  select(-entries, -pop) %>% 
  spread(vaccination_status, per100k) %>%
  select(altersklasse_covid19, not_vaccinated, fully_vaccinated) %>%
  filter(altersklasse_covid19 != "all" & altersklasse_covid19 != "Unbekannt")

names(id_rel_age_q) <- c("Altersgruppe", "Ungeimpft", "Vollständig geimpft")

update_chart(id = "32933cfe729928ecb4906a82bdcc4f9f", 
             data = id_rel_age_q)


#Manufacturer of Vaccine
update_chart(id = "e5aee99aec92ee1365613b671ef405f7", data = ch_vacc_manuf)

ch_vacc_date <-  gsub("\\b0(\\d)\\b", "\\1", format(last(ch_vacc_adm$date), format = "%d. %m. %Y"))


vaccchart_kant <- ch_vacc_doses %>%
  filter(geoRegion != "FL" & geoRegion != "CHFL"  & geoRegion != "CH", type == "COVID19VaccDosesAdministered") %>%
  group_by(geoRegion) %>%
  filter(date ==last(date)) %>%
  mutate(per100 = round(100*sumTotal/pop,0)) %>%
  select(geoRegion, per100) %>%
  arrange(geoRegion)

vaccchart_kant_notes <- paste0("Die Zahlen beziehen sich auf die verabreichten Impfdosen, nicht auf geimpfte Personen.",
                               " Eine Person muss im Normalfall zwei Dosen verimpft bekommen.",
                               "<br>Stand: ", 
                               ch_vacc_date)

update_chart(id = "e039a1c64b33e327ecbbd17543e518d3", data = vaccchart_kant, notes = vaccchart_kant_notes)


# Diese beiden Grafiken sind aktuell nirgends mehr eingebunden, könnten aber wieder aktuell werden.
# Wenn dies eintritt, muss im q.config.json die ID wieder hinterlegt werden mit notes und data.
# Plus die Datenstruktur ist stark verändert

# vaccchart_pctfull <- vacc_pop %>%
#   filter(geounit != "FL" & geounit != "CHFL"  & geounit != "CH") %>%
#   group_by(geounit) %>%
#   filter(date ==last(date)) %>%
#   ungroup() %>%
#   select(kt, verimpft, "nicht verimpft") %>%
#   arrange(desc(verimpft))
# 
# vaccchart_pctfull$`nicht verimpft`[vaccchart_pctfull$`nicht verimpft` < 0] <- NA
# 
# vaccchart_pctfull_notes <- paste0("In einigen Kantonen wurden mehr Impfdosen aus den Ampullen gewonnen,",
#                                   " als offiziell in den Lieferangaben ausgewiesen ist.<br>Stand: ",
#                                   ch_vacc_date)
# 
# update_chart(id = "f8559c7bb8bfc74e70234e717e0e1f8e", 
#              data = vaccchart_pctfull, 
#              notes = vaccchart_pctfull_notes)
# 
# vaccchart_pctpop <- vacc_pop %>%
#   filter(geounit != "FL" & geounit != "CHFL"  & geounit != "CH") %>%
#   group_by(geounit) %>%
#   filter(date ==last(date)) %>%
#   ungroup() %>%
#   select(kt, pct_vacc_doses, pct_notvacc_doses) %>%
#   rename("Verimpft" = pct_vacc_doses, "Nicht verimpft" = pct_notvacc_doses)
# 
# vaccchart_pctpop$`Nicht verimpft`[vaccchart_pctpop$`Nicht verimpft` < 0] <- 0
# 
# vaccchart_pctpop2 <- vaccchart_pctpop %>%
#   mutate(bar = Verimpft+`Nicht verimpft`) %>%
#   arrange(desc(bar)) %>%
#   select(-bar)
# 
# update_chart(id = "5e2bb3f16c0802559ccdf474af11f453", 
#              data = vaccchart_pctpop2, 
#              notes = paste0("Stand: ", ch_vacc_date))

# second doses

vacc_ch_persons_kant <- ch_vacc_persons %>%
  filter(geoRegion != "FL" & geoRegion != "CHFL"  & geoRegion != "CH") %>%
  filter(date == max(date)) %>%
  mutate(per100 =round(100*sumTotal/pop,1)) %>%
  left_join(pop[,c(1:2)], by = c("geoRegion" = "ktabk")) %>%
  select(-pop, -sumTotal, -geoRegion, -date) %>%
  spread(type, per100) %>%
  select(-COVID19AtLeastOneDosePersons) %>%
  mutate(COVID19FullyVaccPersons = COVID19FullyVaccPersons-COVID19FirstBoosterPersons) %>%
  rename("Nur doppelt geimpft" = COVID19FullyVaccPersons, 
         "Nur einmal geimpft" = COVID19PartiallyVaccPersons,
         "Booster erhalten" = COVID19FirstBoosterPersons) %>%
  arrange(desc(`Nur doppelt geimpft`+`Nur einmal geimpft`+`Booster erhalten`))

title_vacc_kant <- paste("In", head(vacc_ch_persons_kant$kt, 1), "sind am meisten Menschen geimpft")

update_chart(id = "54381c24b03b4bb9d1017bb91511e21d",
             data = vacc_ch_persons_kant,
             notes = paste0("In der Schweiz wurden nur wenige Impfungen mit dem Impfstoff von Johnson & Johnson durchgeführt. Diese Impfungen erfordern eine statt zwei Impfdosen und sind daher in der Kategorie «Nur doppelt geimpft» enthalten. Auch Genesene, die eine Impfdosis erhalten haben, sind dort aufgeführt.<br>Stand: ", ch_vacc_date), 
             title = title_vacc_kant)

### Schweiz geimpft nach Altersgruppen

vacc_ch_age <- read_csv(bag_data$sources$individual$csv$weeklyVacc$byAge$vaccPersons) %>%
  filter(geoRegion == 'CHFL', type %in% c("COVID19FullyVaccPersons", "COVID19PartiallyVaccPersons", "COVID19FirstBoosterPersons")) %>%
  filter(date ==last(date), age_group_type == "age_group_AKL10") %>%
  select(altersklasse_covid19, per100PersonsTotal,type) %>%
  spread(type,per100PersonsTotal) %>%
  rename('Altersklasse' = altersklasse_covid19, 
         "Vollständig geimpft" = COVID19FullyVaccPersons,
         "Nur einfach geimpft" = COVID19PartiallyVaccPersons,
         "Booster erhalten" = COVID19FirstBoosterPersons) %>%
  mutate(`Nur doppelt geimpft` = round(`Vollständig geimpft`-`Booster erhalten`, 1),
         `Nur einfach geimpft` = round(`Nur einfach geimpft`, 1),
         `Booster erhalten` = round(`Booster erhalten`, 1))  %>%
  select(Altersklasse, `Booster erhalten`, `Nur doppelt geimpft`, `Nur einfach geimpft`) %>%
  arrange(desc(`Altersklasse`))

vacc_ch_age_date <- read_csv(bag_data$sources$individual$csv$weeklyVacc$byAge$vaccPersonsV2) %>%
  select(date) %>% 
  filter(date == max(date)) %>% 
  mutate(date = as.Date(paste0(str_sub(date,1,4), "-", str_sub(date,5,6),"-", 1), "%Y-%W-%u")+2) %>%
  unique() %>%
  deframe() %>%
  format(format = "%d. %m. %Y")

title <- paste("Rund", round(vacc_ch_age[vacc_ch_age$Altersklasse == "80+",]$`Booster erhalten`), "Prozent der Ältesten sind geboostert")

update_chart(id = "674ce1e7cf4282ae2db76136cb301ba1", 
             data = vacc_ch_age, 
             notes = paste0("In der Schweiz wurden nur wenige Impfungen mit dem Impfstoff von Johnson & Johnson durchgeführt. Diese Impfungen erfordern eine statt zwei Impfdosen und sind daher in der Kategorie «Nur doppelt geimpft» enthalten. Auch Genesene, die eine Impfdosis erhalten haben, sind dort aufgeführt.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", vacc_ch_age_date)),
             title = title)

#### Vaccination, delivered, received ####

ch_vacc_missing_dates <- seq(as.Date("2020-12-23"), as.Date("2021-01-24"), by = "days") %>% as_tibble()

ch_vacc_vdr <- ch_vacc_doses %>%
  filter(geoRegion == "CHFL") %>%
  select(-geoRegion, -pop) %>%
  spread(type, sumTotal) %>%
  rename(Verimpft = COVID19VaccDosesAdministered) %>%
  mutate("An Kantone verteilt" = case_when(COVID19VaccDosesDelivered-Verimpft >= 0 ~ COVID19VaccDosesDelivered-Verimpft,
                                           COVID19VaccDosesDelivered-Verimpft < 0 ~ 0),
         "in die Schweiz geliefert" = case_when(COVID19VaccDosesReceived-(Verimpft+`An Kantone verteilt`) >= 0 ~ COVID19VaccDosesReceived-(Verimpft+`An Kantone verteilt`),
                                                COVID19VaccDosesReceived-(Verimpft+`An Kantone verteilt`) < 0 ~ 0)) %>%
  select(-c(3:4)) %>%
  fill(c(3:4))

tail(ch_vacc_vdr,1)

update_chart(id = "ce1529d1facf24bb5bef83a3df033bfc", 
             data = ch_vacc_vdr)


#### Vaccination Projection CH ####
ch_vacc_speed <- ch_vacc_doses %>%
   filter(geoRegion == "CHFL", type == "COVID19VaccDosesAdministered") %>%
   mutate(new_vacc_doses = sumTotal-lag(sumTotal, 1, default = 0)) %>%
   mutate(new_vacc_doses_7day = (sumTotal-lag(sumTotal,7, default = 0))/7) %>%
   mutate(new_vacc_doses_7day = round(new_vacc_doses_7day))
 
#Just vacc Speed
#write to Q-cli
update_chart(id = "b5f3df8202d94e6cba27c93a5230cd0e",
             data = ch_vacc_speed %>% select(date, new_vacc_doses_7day))

# #Projection
# dates_proj_ch <- seq(last(ch_vacc_speed$date)+1, as.Date("2099-12-31"), by="days")
# ndays_proj_ch <- seq(1,length(dates_proj_ch), by = 1)
# 
# ch_vacc_esti <- ch_vacc_speed %>%
#   filter(date >= last(date)-13) %>%
#   summarise(  max_iqr = max(new_vacc_doses_7day), 
#               min_iqr = min(new_vacc_doses_7day), 
#               mean = mean(new_vacc_doses_7day, na.rm = TRUE))
# 
# vacc_proj_mean_ch <- ndays_proj_ch*ch_vacc_esti$mean + sum(ch_vacc_speed$new_vacc_doses, na.rm = T)
# vacc_proj_max_iqr_ch <- ndays_proj_ch*ch_vacc_esti$max_iqr + sum(ch_vacc_speed$new_vacc_doses, na.rm = T)
# vacc_proj_min_iqr_ch <- ndays_proj_ch*ch_vacc_esti$min_iqr + sum(ch_vacc_speed$new_vacc_doses, na.rm = T)
# 
# ch_vacc_proj_raw <- tibble(dates_proj_ch, vacc_proj_mean_ch, vacc_proj_max_iqr_ch, vacc_proj_min_iqr_ch)
# 
# herd_immunity_ch <-8644780*1.6
# herd_immunity_date_ch <- first(ch_vacc_proj_raw$dates_proj_ch[vacc_proj_mean_ch > herd_immunity_ch])
# herd_immunity_date_ch_max <- first(ch_vacc_proj_raw$dates_proj_ch[vacc_proj_min_iqr_ch > herd_immunity_ch])
# 
# 
# #calculate goal
# ch_vacc_goaldays <- length(ch_vacc_proj_raw$dates_proj_ch[ch_vacc_proj_raw$dates_proj_ch <= "2021-08-31"])
# ch_vacc_goalspeed <- (herd_immunity_ch-last(ch_vacc_speed$sumTotal))/ch_vacc_goaldays
# vacc_proj_goal_ch <- ndays_proj_ch*ch_vacc_goalspeed + sum(ch_vacc_speed$new_vacc_doses, na.rm = T)
# 
# ch_vacc_proj_raw_goal <- tibble(ch_vacc_proj_raw, vacc_proj_goal_ch)
# 
# ch_vacc_hi <- ch_vacc_proj_raw_goal %>% filter(dates_proj_ch <= herd_immunity_date_ch_max)
# 
# # clean off unneecessary data points
# ch_vacc_hi$vacc_proj_mean_ch[ch_vacc_hi$vacc_proj_mean_ch >= herd_immunity_ch] <- NA
# ch_vacc_hi$vacc_proj_max_iqr_ch[ch_vacc_hi$vacc_proj_max_iqr_ch >= herd_immunity_ch] <- NA
# ch_vacc_hi$vacc_proj_min_iqr_ch[ch_vacc_hi$vacc_proj_min_iqr_ch >= herd_immunity_ch] <- NA
# ch_vacc_hi$vacc_proj_goal_ch[ch_vacc_hi$vacc_proj_goal_ch >= herd_immunity_ch] <- NA
# 
# colnames(ch_vacc_hi) <- c("Datum",	"Momentante Geschwindigkeit", " ",	"Unsicherheitsbereich*", "Nötige Geschwindigkeit")
# 
# ch_past <- cbind(ch_vacc_speed[,c(1,5)], NA, NA, NA)
# 
# colnames(ch_past) <- colnames(ch_vacc_hi)
# 
# ch_vacc_hi2 <- rbind(ch_past, ch_vacc_hi) %>%
#   select(1,3,4,2,5)
# 
# #write to Q-cli
# 
# update_chart(id = "37fc5e48506c4cd050bac04346238a2d", 
#              data = ch_vacc_hi2,
#              notes = paste0("* Maximaler und minimaler 7-Tage-Schnitt der letzten zwei Wochen.<br>Stand: ",
#                             ch_vacc_date))

#Vacc pct by dose
ch_vacc_persons_hist <- ch_vacc_persons %>%
  filter(geoRegion == "CHFL") %>%
  mutate(per100 = 100*sumTotal/pop) %>%
  select(-sumTotal, -geoRegion, -pop) %>%
  spread(type, per100) %>%
  select(-COVID19AtLeastOneDosePersons) %>%
  rename(Vollständig = COVID19FullyVaccPersons, Teilweise = COVID19PartiallyVaccPersons)

ch_vacc_persons_hist_new <- ch_vacc_persons %>%
  filter(geoRegion == "CHFL") %>%
  select(-geoRegion, -pop) %>%
  spread(type, sumTotal) %>%
  mutate(n1 = COVID19AtLeastOneDosePersons-lag(COVID19AtLeastOneDosePersons), 
         n2 = COVID19FullyVaccPersons-lag(COVID19FullyVaccPersons,1),
         n3 = COVID19FirstBoosterPersons-lag(COVID19FirstBoosterPersons,1))%>%
  mutate(Erstimpfungen = rollmean(n1, 7, NA, align = "right"),
         Zweitimpfungen = rollmean(n2, 7, NA, align = "right"),
         Boosterimpfungen = rollmean(n3, 7, NA, align = "right"))%>%
  select(date, Erstimpfungen, Zweitimpfungen, Boosterimpfungen)

ch_vacc_persons_hist_new$Boosterimpfungen[ch_vacc_persons_hist_new$Boosterimpfungen < 20] <- NA

update_chart(id = "82aee9959c2dd62ec398e00a2d3eb5ae",
             data = ch_vacc_persons_hist_new)

### BAG VACC GOAL

vacc_bag_goal <- read_csv(bag_data$sources$individual$csv$weeklyVacc$byAge$vaccPersons) %>%
  filter(geoRegion == 'CHFL', 
         type %in% c("COVID19AtLeastOneDosePersons"), 
         date ==last(date),
         age_group_type == "age_group_vacc_strategy") %>%
  select(altersklasse_covid19, per100PersonsTotal, type) %>%
  spread(type,per100PersonsTotal)%>%
  rename('Altersklasse' = altersklasse_covid19, 
         Impfquote = COVID19AtLeastOneDosePersons) %>%
  mutate(Impfquote = round(Impfquote, 1)) %>%
  arrange(desc(`Altersklasse`)) %>%
  mutate(Altersklasse = str_replace_all(Altersklasse, " - ", "–")) %>%
  add_column(Zielwert = c(93, 80, NA))

vacc_bag_goal_notes <- paste0("Der Bundesrat hat Zielwerte für 18- bis 65-Jährige und über 65-Jährige festgelegt,",
                               " die Daten des BAG weisen leicht abweichende Altersgruppen aus (16 bis 64  und über 64 Jahre).",
                              " Für unter 18-Jährige wurde kein Zielwert festgelegt.",
                              " Die Zahlen werden wöchentlich aktualisiert.",
                               "<br>Stand: ", 
                               ch_vacc_date)

update_chart(id = 'b4f50110543451f0029c2fdefe53d578',
             data = vacc_bag_goal,
             notes = vacc_bag_goal_notes)


# fin
