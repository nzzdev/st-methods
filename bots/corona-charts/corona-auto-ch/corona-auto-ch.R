#### Corona-Script SWITZERLAND (automated version) #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
# #if tidyverse causes github error
# update.packages(ask = F)
options(scipen=999)
library(tidyverse)
library(jsonlite)
library(zoo)
library(rvest)

# #setwd for fixes
# setwd("~/Documents/GitHub/st-methods/bots/corona-charts")
# setwd("/Users/simon/Documents/projects/st-methods/bots/corona-charts/")
# 
# #renv
# library(renv)
# renv::init()
# renv::snapshot()

# import helper functions

source("./helpers.R")

# read in additional data
pop <- read_csv("./corona-auto-ch/pop_kant.csv")

#### Wastewater Analysis Werdhölzli ####

ww_zh_0 <- read_delim("https://sensors-eawag.ch/sars/__data__/processed_normed_data_zurich_v1.csv", delim = ";") %>% 
  select(...1, `median_7d_new_cases [1/(d*100000 capita)]`, `median_7d_sars_cov2_rna [gc/(d*100000 capita)]`) %>%
  rename(date = 1, cases = 2, old = 3) %>%
  mutate(old = old/100000000000)

ww_zh <- read_delim("https://sensors-eawag.ch/sars/__data__/processed_normed_data_zurich_v2.csv", delim = ";") %>% 
  select(...1, `median_7d_sars_cov2_rna [gc/(d*100000 capita)]`) %>%
  rename(date = 1, new = 2) %>%
  mutate(new = new/250000000000)

ww_zh_comb <- ww_zh_0 %>%
  full_join(ww_zh, by = "date") %>%
  mutate(cases = cases*100/max(cases, na.rm = TRUE), 
         old = old*100/max(new, na.rm = TRUE),
         new = new*100/max(new, na.rm = TRUE)) %>%
  rename("Viruslast (alte Methoden)" = old, 
         "Viruslast (neue Methode)" = new,
         "Fallzahlen" = cases)

update_chart(id = "ae2fa42664db4ab375dba744d0706269", 
             data = ww_zh_comb)

#### Excess deaths (BfS) ####

url_xm <- read_html("https://www.bfs.admin.ch//bfs/de/home/statistiken/gesundheit/gesundheitszustand/sterblichkeit-todesursachen/_jcr_content/par/ws_composed_list_1765412048.dynamiclist.html") %>%
  as.character() %>%
  str_extract_all("/bfs.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+") %>%
  unlist() %>%
  as_vector()

link_xm <- paste0("https://www.bfs.admin.ch/bfsstatic/dam/assets/",str_sub(url_xm[1], -13,-6), "/master")

bfs <- read_csv2(link_xm) %>%
  filter((Jahr >= "2020"), AnzTF_HR != ".") %>%
  select(Alter, endend, untGrenze, obeGrenze, AnzTF_HR, Diff) %>%
  mutate(AnzTF_HR = as.numeric(AnzTF_HR), Diff = as.numeric(Diff), endend = as.Date(endend, "%d.%m.%Y")) %>%
  rename(Datum = endend) %>%
  replace(is.na(.), 0) 

bfs_old <- read.csv2(text=paste0(head(readLines('https://www.bfs.admin.ch/bfsstatic/dam/assets/12607336/master'), -11), collapse="\n")) %>%
  select(Alter, Endend, untGrenze, obeGrenze, Anzahl_Todesfalle, Exzess) %>%
  replace(is.na(.), 0) %>%
  dplyr::rename(Datum = Endend, AnzTF_HR = Anzahl_Todesfalle, Diff = Exzess) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) 

bfs_all <- rbind(bfs_old, bfs) %>%  
  filter(Datum >= '2015-01-01', Alter == "65+") %>%
  select(-Alter, -Diff) %>%
  rename("Tatsächlich verzeichnete Todesfälle" = "AnzTF_HR", " " = "untGrenze", "Erwartete Bandbreite" = "obeGrenze")

## Neuster Stand für die Q Grafik

xm_notes <- paste0("Die Datenreihe endet am ", gsub("\\b0(\\d)\\b", "\\1", format(max(bfs_all$Datum), format = "%d. %m. %Y.")))

#q-cli update
update_chart(id = "f7b3b35758e309767ad0d3096a2fe0ff", 
             data = bfs_all, 
             notes = xm_notes)

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

#eth_cantons <- read_csv("https://raw.githubusercontent.com/covid-19-Re/dailyRe-Data/master/CHE-estimates.csv") %>%
 # filter(region %in% c("BE","ZH","VD","AG","SG","GE","LU", "TI","VS", "FR")) %>%
  #filter(data_type == "Confirmed cases" & estimate_type == "Cori_slidingWindow") %>%
  #group_by(region) %>%
  #filter(date == last(date)) %>%
  #ungroup() %>%
  #left_join(pop[,1:2], by = c("region" = "ktabk")) %>%
  #select(kt, median_R_highHPD,median_R_lowHPD,median_R_mean) %>%
  #arrange(desc(median_R_mean))

#eth_cantons_title <- paste0("Der Kanton ", eth_cantons[1,1], " verzeichnet den höchsten R-Wert")
#eth_cantons_notes <- paste0("Die Daten liegen in einem 95%-Konfidenzintervall. Wir zeigen nur die R-Werte für die zehn grössten Kantone.",
 #                           " In kleinen Kantonen ist der Unsicherheitsbereich teilweise sehr gross, so dass keine verlässlichen Aussagen möglich sind.",
 #                          " Die neusten Schätzungen der Kantone liegen in der Regel einige Tage hinter der nationalen Schätzung.<br> Stand: ",
 #                           gsub("\\b0(\\d)\\b", "\\1", format(nth(eth$Datum, -2)-4, format = "%d. %m. %Y")))

#colnames(eth_cantons) <- c("Kanton", "", "Unsicherheitsbereich", "Median")

#q-cli update
#update_chart(id = "f649302cbf7dd462f339d0cc35d9695a", 
 #            data = eth_cantons, 
  #           notes = eth_cantons_notes,
   #          title = eth_cantons_title)



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

bag_var <- read.csv(bag_data$sources$individual$csv$daily$virusVariantsWgs)%>%
  filter(geoRegion == 'CHFL') %>%
  select("variant_type", "date", "prct", "prct_lower_ci", "prct_upper_ci", "prct_mean7d", "entries")




### Dashboard ###

tmp_cases <- read_csv(bag_data$sources$individual$csv$daily$cases) %>%
  filter(datum == max(datum), geoRegion == 'CHFL')


bag_cases_ravg <- bag_cases %>%
  filter(geoRegion == 'CHFL', datum >= "2020-02-28" & datum <= last(datum)-2) %>%
  mutate(value = round(rollmean(entries, 7, fill = 0, align = "right"),0)) %>%
  select("datum", "value") %>%
  rename(date = datum)
 
roll_ch_bag_death_hosp_dash <- bag_deaths %>%
  full_join(bag_hosps, by = c("geoRegion", "datum")) %>%
  filter(datum >= "2020-02-28" & datum <=  last(datum)-5, geoRegion == 'CHFL')  %>%
  mutate(hosp_roll = rollmean(entries.y,7,fill = 0, align = "right"),
     death_roll = rollmean(entries.x,7,fill = 0, align = "right")) %>%
  select("datum", "hosp_roll", "death_roll") %>%
  rename(Hospitalierungen = hosp_roll, Todesfälle = death_roll)
 
roll_ch_bag_hosp <- roll_ch_bag_death_hosp_dash %>%
  select(datum, Hospitalierungen) %>%
  filter(datum >= '2020-10-01') %>%
  rename(date = datum, value = Hospitalierungen)
 
roll_ch_bag_death <- roll_ch_bag_death_hosp_dash %>%
  select(datum, `Todesfälle`) %>%
  filter(datum >= '2020-10-01') %>%
  rename(date = datum, value = `Todesfälle`)
 
roll_ch_bag_cases_trend <- bag_cases_ravg %>%
  mutate(pct_of_max = (value*100)/max(value, na.rm = T)) %>%
  mutate(diff_pct_max = pct_of_max - lag(pct_of_max, 14, default = 0)) %>%
  mutate(trend = case_when(diff_pct_max > 3 ~ 'steigend',
                     diff_pct_max < -3 ~ 'fallend',
                     TRUE ~ 'gleichbleibend',))
 
roll_ch_bag_hosp_trend <- roll_ch_bag_hosp %>%
  mutate(pct_of_max = (value*100)/max(value, na.rm = T)) %>%
  mutate(diff_pct_max = pct_of_max - lag(pct_of_max, 14, default = 0)) %>%
  mutate(trend = case_when(diff_pct_max > 3 ~ 'steigend',
                      diff_pct_max < -3 ~ 'fallend',
                      TRUE ~ 'gleichbleibend',))
 
roll_ch_bag_death_trend <- roll_ch_bag_death %>%
  mutate(pct_of_max = (value*100)/max(value, na.rm = T)) %>%
  mutate(diff_pct_max = pct_of_max - lag(pct_of_max, 14, default = 0)) %>%
  mutate(trend = case_when(diff_pct_max > 3 ~ 'steigend',
                      diff_pct_max < -3 ~ 'fallend',
                      TRUE ~ 'gleichbleibend',))
 
forJson_1 <- data.frame(indicatorTitle = "Neue Spitaleintritte",
                   date = tmp_cases$datum,
                   indicatorSubtitle = "7-Tage-Schnitt",
                   value = round(last(roll_ch_bag_hosp$value)),
                   color = "#24b39c",
                   trend = last(roll_ch_bag_hosp_trend$trend),
                   chartType = "area")

forJson_1$chartData <- list(roll_ch_bag_hosp)
 
tail(roll_ch_bag_hosp)
forJson_2 <- data.frame(indicatorTitle = "Neuinfektionen",
                  date = tmp_cases$datum,
                  value = round(last(bag_cases_ravg$value)),
                  color = "#e66e4a",
                  trend = last(roll_ch_bag_cases_trend$trend),
                  chartType = "area")
 
forJson_2$chartData <- list(bag_cases_ravg %>% filter(date >= '2020-10-01'))
 
forJson_3 <- data.frame(indicatorTitle = "Neue Todesfälle",
                  date = tmp_cases$datum,
                  value = round(last(roll_ch_bag_death$value)),
                  color = "#05032d",
                  trend = last(roll_ch_bag_death_trend$trend),
                  chartType = "area")
 
forJson_3$chartData <- list(roll_ch_bag_death)

if (!(file.exists("./data/"))) {
  dir.create("./data/")
}

z <- toJSON(rbind_pages(list(forJson_1, forJson_2, forJson_3)), pretty = T)
write(z, "./data/dashboard_ch.json")

files <- list(
  list(
    file = list(
      path = "./data/dashboard_ch.json"
    )
  )
)
 
#q-cli update
update_chart(id = "499935fb791197fd126bda721f15884a", files = files)



# Total cases in CH since 2020-02-24 and recovery calculation
bag_total <- merge(bag_cases, bag_deaths, by = c("geoRegion", "datum")) %>%
  filter(geoRegion == 'CHFL') %>%
  mutate(Infizierte = sumTotal.x - sumTotal.y) %>%
  rename("Tote" = `sumTotal.y`) %>%
  select("datum", "Infizierte", "Tote") %>%
  mutate(`Genesene (Schätzung)` = ((lag(Infizierte,14, default = 0)) * 0.75) + 
           ((lag(Infizierte,21, default = 0)) * 0.10) + 
           ((lag(Infizierte,28, default = 0)) * 0.10) +
           ((lag(Infizierte,42, default = 0)) * 0.05)) %>%
  mutate(`gegenwärtig Infizierte` = Infizierte -`Genesene (Schätzung)`) %>%
  select("datum", "Tote", "gegenwärtig Infizierte", "Genesene (Schätzung)")

bag_total_title <- paste0(gsub('\\.', ',' ,toString(round(sum(tail(bag_total[,2:4], 1))/1000000, 1))), " Millionen bestätigte Infektionen und ", toString(tail(bag_total$Tote, 1)), " Todesfälle in der Schweiz")

#q-cli update
update_chart(id = "3209a77a596162b06346995b10896863", 
             data = bag_total, title = bag_total_title)

#now infected only
#bag_inf <- bag_total %>% select(datum, `gegenwärtig Infizierte`)

#update_chart(id = "9c87f52098e02f80740ec4a3743615b2", 
 #            data = bag_inf)

#### Rolling average of cases ####

#q-cli update
update_chart(id = "93b53396ee7f90b1271f620a0472c112", data = bag_cases_ravg)


# Tests (Antigen and PCR), absolute number

bag_testPcrAntigen_abs <- bag_testPcrAntigen %>% 
  filter(datum > "2020-11-01", geoRegion == 'CHFL') %>%
  select("datum", "entries", "nachweismethode") %>%
  spread(nachweismethode, entries) %>%
  mutate("Antigen-Schnelltests" = round(rollmean(Antigen_Schnelltest, 7, fill = 0, align = "right"), 1), 
         "PCR-Tests" = round(rollmean(PCR, 7, na.pad = TRUE, align = "right"), 1)) %>%
  select(datum, `Antigen-Schnelltests`, `PCR-Tests`) %>%
  filter(`Antigen-Schnelltests` + `PCR-Tests` > 0) %>%
  drop_na() 

#q-cli update
update_chart(id = "fe58121b9eb9cbc28fb71b8810a7b573", data = bag_testPcrAntigen_abs)

# Positivity rate (PCR and Antigen)
bag_tests_pct <- bag_testPcrAntigen %>%
  filter(datum > "2020-11-01", geoRegion == 'CHFL') %>%
  group_by(nachweismethode) %>%
  mutate(pct = round(rollmean(pos_anteil, 7, na.pad = TRUE, align = "right"), 1)) %>%
  select("nachweismethode", "datum", "pct") %>%
  spread(nachweismethode, pct) %>%
  drop_na()  %>%
  rename("Antigen-Schnelltests" = Antigen_Schnelltest, "PCR-Tests" = PCR) %>%
  add_column("WHO-Zielwert" = 5)

#q-cli update
update_chart(id = "e18ed50b4fad7ada8063e3a908eb77ac", data = bag_tests_pct)

# Age distribution of cases, weekly
bag_age  <- bag_cases_age %>%
  filter(!is.na(datum), altersklasse_covid19 != "Unbekannt", geoRegion == "CHFL") %>%
  mutate(datum = paste0(substr(datum, 1, 4), "-W", substr(datum, 5, 6))) %>%
  select("datum", "altersklasse_covid19", "entries") %>%
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
  select("geoRegion", "per100k")

bag_kanton_choro_notes <- paste0("Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(bag_cases$datum), format = "%d. %m. %Y")))

update_chart(id = "a2fc71a532ec45c64434712991efb41f", data = bag_kanton_choro, notes = bag_kanton_choro_notes)

#### Wastewater BAG ####

ww_bag_stations <- read_csv(bag_data$sources$individual$csv$wasteWater$viralLoad)

ww_bag_mean <- ww_bag_stations %>%
  select(date, name, vl_mean7d) %>%
  spread(name, vl_mean7d) %>%
  mutate(count_na = rowSums(is.na(.))) %>%
  filter(count_na < 25) %>%
  mutate(mean = round(rowMeans(.[2:100], na.rm = T)/1000000000)) %>%
  select(date, mean) %>%
  full_join(bag_cases_ravg, by = c("date" = "date")) %>%
  filter(date >= "2022-02-10") %>%
 mutate(ravg_cases = value*100/max(value), 
        mean = mean*100/max(mean, na.rm = TRUE)) %>%
  select("Datum" = date, 
         "Fallzahlen" = ravg_cases, 
         "Viruslast im Abwasser (Durchschnitt aller Messtationen)" = mean)

update_chart(id = "eaf294e8d0fac38bd3261ab67be4d6fb",
             data = ww_bag_mean)

#### Hospitalisierungen und Todesfälle ####

# Absolut 
roll_ch_bag_death_hosp <- bag_cases %>%
  full_join(bag_deaths, by = c("geoRegion", "datum")) %>%
  full_join(bag_hosps, by = c("geoRegion", "datum")) %>%
  filter(datum >= "2020-02-28" & datum <=  last(datum)-5, geoRegion == 'CHFL')  %>%
  mutate(entries.y = replace_na(entries.y, 0),
         hosp_roll = rollmean(entries,7,fill = 0, align = "right"),
         death_roll = rollmean(entries.y,7,fill = 0, align = "right")) %>%
  select("datum", "hosp_roll", "death_roll") %>%
  rename(Hospitalisierungen = hosp_roll, Todesfälle = death_roll)

update_chart(id = "2e86418698ad77f1247bedf99b771e99", data = roll_ch_bag_death_hosp)


# Todesfälle only 
roll_ch_bag_death <- roll_ch_bag_death_hosp %>%
  select("datum", "Todesfälle")

update_chart(id = "ae2fa42664db4ab375dba744d07afac4", data = roll_ch_bag_death)

# Hosps only (with correction)
roll_ch_bag_hosp_2 <- roll_ch_bag_death_hosp %>%
  select("datum", "Hospitalisierungen")

hosp_corr <- read_csv("./corona-auto-ch/hosp-corr.csv")
hosp_corr_fill <- as_tibble(rep(1, nrow(roll_ch_bag_hosp_2)-nrow(hosp_corr)))

hosp_corr_2 <- bind_rows(hosp_corr_fill, hosp_corr)

hosp_with_corr <- cbind(roll_ch_bag_hosp_2, hosp_corr_2) %>% 
  mutate(corr = Hospitalisierungen*((((value-1)/3)*2)+1)*1.3) %>%
  select(datum, Hospitalisierungen, corr) %>%
  rename("Hospitalisierungen laut BAG" = Hospitalisierungen, "Schätzung inkl. Nachmeldungen und Meldelücke*" = corr) %>% 
  as_tibble() %>%
  tail(-6)

update_chart(id = "ae2fa42664db4ab375dba744d0712df3", data = hosp_with_corr)

# Todesfälle und Hospitalisierungen absolut nach Altersklasse 

bag_deaths_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$death) %>%
  filter(geoRegion == 'CHFL') %>%
  select("altersklasse_covid19", "geoRegion", "date", "entries") %>%
  distinct() %>%
  mutate(KW = substr(date, 5, 6), year = substr(date, 1, 4)) %>% 
  group_by(KW, year, altersklasse_covid19) %>%
  summarize(sum = sum(entries)) %>% distinct() %>% ungroup()


bag_hosp_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$hosp) %>%
  select("altersklasse_covid19", "geoRegion", "datum", "entries", "sumTotal")  %>%
  mutate(KW = substr(datum, 5, 6), year = substr(datum, 1, 4))

bag_age_deaths  <- bag_deaths_age %>%
  filter(!is.na(date), altersklasse_covid19 != "Unbekannt", (year >= '2021' | (year == '2020' & KW >= '52' ) )) %>%
  mutate(date = paste0(year, "-W", KW)) %>%
  select(date, altersklasse_covid19, sum) %>%
  spread(altersklasse_covid19, sum) %>%
  select(date, `0 - 64`,`65+`) 

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



### Variants ###

bag_var_all <- bag_var %>%
  mutate(date = as.Date(date)) %>%
  drop_na(prct) %>%
  filter(variant_type != "all_sequenced") %>%
  mutate(var = case_when(variant_type == "B.1.1.7"~ "Alpha",
                         variant_type == "B.1.617.2" ~ "Delta",
                         variant_type == "B.1.1.529" ~ "Omikron",
                         variant_type == "other_lineages" ~ "Urtyp / andere Varianten",
                         TRUE ~ "Weitere «relevante Virusvarianten»*")) %>%
  group_by(date, var) %>%
  summarise(prct = sum(prct)) %>%
  group_by(var) %>%
  mutate(prct_7 = round(rollmean(prct, 7, fill = NA, align = "right"),1)) %>%
  select(date, var, prct_7) %>%
  spread(var,prct_7) %>%
  mutate(`Urtyp / andere Varianten` = round(100-(Alpha+Delta+Omikron+`Weitere «relevante Virusvarianten»*`),1)) %>%
  filter(date >= "2020-10-10") %>%
  select(date, Alpha, Delta, Omikron, `Weitere «relevante Virusvarianten»*`, `Urtyp / andere Varianten`)

update_chart(id = "396fd1e1ae7c6223217d80a9c5421999",
             data = bag_var_all)




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

ch_inf_vacc <- read_csv(bag_data$sources$individual$csv$daily$casesVaccPersons) %>%
#  filter(vaccine == "all") %>%
  mutate(type = "Infektionen")

ch_hosp_vacc <- read_csv(bag_data$sources$individual$csv$daily$hospVaccPersons) %>%
#  filter(vaccine == "all") %>%
  mutate(type = "Spitaleintritte")

ch_death_vacc <- read_csv(bag_data$sources$individual$csv$daily$deathVaccPersons) %>%
#  filter(vaccine == "all") %>%
  mutate(type = "Todesfälle")

ch_hosp_vacc_age <- read_csv(bag_data$sources$individual$csv$weekly$byAge$hospVaccPersons) %>% 
  filter(vaccine == "all")


#### Impfdurchbrüche ####

id_total <- rbind(ch_hosp_vacc, ch_death_vacc) %>%
  filter(vaccine == "all") %>%
  filter(date == max(date), vaccination_status %in% c("fully_vaccinated","partially_vaccinated")) %>%
  select(type, vaccination_status, sumTotal) %>%
  spread(vaccination_status, sumTotal) %>%
  rename("Typ" = 1, "Mindestens zweimal geimpft" = 2, "Teilweise geimpft" = 3)

update_chart(id = "ab97925bcc5055b33011fb4d3320012a", 
             data = id_total, 
             notes = paste0("Die Zahl der gemeldeten Infektionen bei Geimpften wird vom BAG nicht mehr publiziert,",
                            " da die Daten nicht aussagekräftig sind.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(ch_hosp_vacc$date), format = "%d. %m. %Y"))))


id_hist <- rbind(ch_hosp_vacc, ch_death_vacc) %>%
  filter(vaccine == "all") %>%
  filter(date >= "2021-11-01") %>%
  group_by(type, vaccination_status) %>%
  summarise(entries = sum(entries)) %>%
  spread(vaccination_status, entries) %>%
  select("Typ" = 1, "Mindestens doppelt geimpft" = 2, "Einmal geimpft" = 6, "Nicht geimpft" = 5, "Unbekannt" = 6)

id_hist[2:5] <- round(id_hist[2:5]/rowSums(id_hist[2:5])*100,1)

update_chart(id = "c041757a38ba1d4e6851aaaee55c6207", 
             data = id_hist, 
             notes = paste0("Der Zeitraum ab 1. November 2021 wurde so gewählt, weil zu diesem Zeitpunkt die Booster-Impfungen starteten. <br>Stand: ",
                            gsub("\\b0(\\d)\\b", "\\1", format(max(ch_hosp_vacc$date), format = "%d. %m. %Y"))))



id_hosp_line_weekly_pc_60 <- ch_hosp_vacc_age %>%
  filter(altersklasse_covid19 %in% c("60 - 69", "70 - 79", "80+"), 
         vaccination_status != "unknown" & vaccination_status != "partially_vaccinated",
         date >= "202146") %>%
  select(date, altersklasse_covid19, vaccination_status, entries, pop) %>%
  group_by(date, vaccination_status) %>%
  summarise(entries = sum(entries), pop = sum(pop)) %>%
  mutate(per100k = 100000*entries/pop) %>%
  select(-entries, -pop) %>%
  spread(vaccination_status, per100k) %>%
  mutate(date = paste0(str_sub(date, 1,4), "-W", str_sub(date, 5,6))) %>%
  select(1, 3, 4, 5)

names(id_hosp_line_weekly_pc_60) <- c("date", "Booster erhalten", "Doppelt geimpft", "Ungeimpft") 
  

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
  summarise(entries = sum(entries), pop = last(pop)) %>%
  mutate(per100k = round(100000*entries/pop, 1))

id_rel_age_q <- id_rel_age %>%
  select(-entries, -pop) %>% 
  spread(vaccination_status, per100k) %>%
  select(altersklasse_covid19, not_vaccinated, fully_vaccinated) %>%
  filter(altersklasse_covid19 != "all" & altersklasse_covid19 != "Unbekannt" & altersklasse_covid19 != "0 - 9")

id_rel_age_q$altersklasse_covid19 <- str_replace_all(id_rel_age_q$altersklasse_covid19," - ","–")

names(id_rel_age_q) <- c("Altersgruppe", "Ungeimpft", "Mindestens zweimal geimpft")

update_chart(id = "32933cfe729928ecb4906a82bdcc4f9f", 
             data = id_rel_age_q)


# second doses

vacc_ch_persons_kant <- ch_vacc_persons %>%
  filter(type != 'COVID19VaccSixMonthsPersons') %>%
  filter(geoRegion != "FL" & geoRegion != "CHFL"  & geoRegion != "CH") %>%
  filter(date == max(date)) %>%
  mutate(per100 =round(100*sumTotal/pop,1)) %>%
  left_join(pop[,c(1:2)], by = c("geoRegion" = "ktabk")) %>%
  select(-pop, -sumTotal, -geoRegion, -date) %>%
  spread(type, per100) %>%
  select(-COVID19AtLeastOneDosePersons) %>%
  mutate(COVID19FullyVaccPersons = COVID19FullyVaccPersons-COVID19FirstBoosterPersons) %>%
  rename("Doppelt geimpft*" = COVID19FullyVaccPersons, 
         "Einmal geimpft" = COVID19PartiallyVaccPersons,
         "Dreimal geimpft" = COVID19FirstBoosterPersons,
         "Viermal geimpft" = COVID19SecondBoosterPersons) %>%
  mutate(`Dreimal geimpft` = `Dreimal geimpft` - `Viermal geimpft`) %>%
  arrange(desc(`Doppelt geimpft*`+`Einmal geimpft`+`Dreimal geimpft`+`Viermal geimpft`))

title_vacc_kant <- paste("In", head(vacc_ch_persons_kant$kt, 1), "sind am meisten Menschen geimpft")


ch_vacc_date <- gsub("\\b0(\\d)\\b", "\\1", format(max(ch_vacc_persons$date), format = "%d. %m. %Y"))

update_chart(id = "54381c24b03b4bb9d1017bb91511e21d",
             data = vacc_ch_persons_kant,
             notes = paste0("* Inkl. Genesene mit einer Impfdosis und Personen, die einen Ein-Dosis-Impfstoff erhalten haben.<br>Stand: ", ch_vacc_date), 
             title = title_vacc_kant)


vacc_persons_ch <- ch_vacc_persons %>%
  filter(geoRegion == "CHFL") %>%
  group_by(type) %>%
  filter(date == max(date)) %>%
  mutate(per100 =round(100*sumTotal/pop,1)) %>%
  select(-pop, -sumTotal, -date, -geoRegion) %>%
  mutate(type = dplyr::recode(type, COVID19FullyVaccPersons = "Doppelt geimpft*", 
                              COVID19SecondBoosterPersons = "Zweiten Booster erhalten",
                              COVID19FirstBoosterPersons = "Ersten Booster erhalten")) %>%
  filter(type != "COVID19AtLeastOneDosePersons" & 
           type != "COVID19NotVaccPersons" & 
           type != "COVID19VaccSixMonthsPersons" &
           type != "COVID19PartiallyVaccPersons") %>%
  arrange(desc(per100))

title_vacc_ch <- paste0(gsub('\\.', ',', toString(vacc_persons_ch$per100[vacc_persons_ch$type == "Doppelt geimpft*"])), ' Prozent der Schweizer Bevölkerung ist doppelt geimpft')

update_chart(id = "8022cf0d0f108d3a2f65d2d360266789",
             data = vacc_persons_ch,
             notes = paste0("* Inkl. Genesene mit einer Impfdosis und Personen, die einen Ein-Dosis-Impfstoff erhalten haben.<br>Stand: ", ch_vacc_date), 
             title = title_vacc_ch)


### Schweiz geimpft nach Altersgruppen

vacc_ch_age <- read_csv(bag_data$sources$individual$csv$weeklyVacc$byAge$vaccPersons) %>%
  filter(geoRegion == 'CHFL', type %in% c("COVID19FullyVaccPersons", "COVID19PartiallyVaccPersons", "COVID19FirstBoosterPersons", "COVID19SecondBoosterPersons")) %>%
  filter(date ==last(date), age_group_type == "age_group_AKL10") %>%
  select(altersklasse_covid19, per100PersonsTotal,type) %>%
  spread(type,per100PersonsTotal) %>%
  mutate(COVID19FullyVaccPersons = COVID19FullyVaccPersons-COVID19FirstBoosterPersons) %>%
  rename('Altersklasse' = altersklasse_covid19, 
         "Doppelt geimpft*" = COVID19FullyVaccPersons,
         "Einfach geimpft" = COVID19PartiallyVaccPersons,
         "Dreimal geimpft" = COVID19FirstBoosterPersons,
         "Viermal geimpft" = COVID19SecondBoosterPersons) %>%
  mutate(`Doppelt geimpft*` = round(`Doppelt geimpft*`, 1),
         `Einfach geimpft` = round(`Einfach geimpft`, 1),
         `Dreimal geimpft` = round(`Dreimal geimpft`-`Viermal geimpft`, 1))  %>%
  select(Altersklasse, `Einfach geimpft`, `Doppelt geimpft*`, `Dreimal geimpft`, `Viermal geimpft`) %>%
  arrange(desc(`Altersklasse`))

vacc_ch_age_date <- read_csv(bag_data$sources$individual$csv$weeklyVacc$byAge$vaccPersons) %>%
  select(date) %>% 
  filter(date == max(date)-1) %>% 
  mutate(date = as.Date(paste0(str_sub(date,1,4), "-", str_sub(date,5,6),"-", 5), "%Y-%W-%u")) %>%
  unique() %>%
  deframe() %>%
  format(format = "%d. %m. %Y")

title <- paste("Rund", round(vacc_ch_age[vacc_ch_age$Altersklasse == "80+",]$`Viermal geimpft`), "Prozent der Ältesten sind zweimal geboostert")

update_chart(id = "674ce1e7cf4282ae2db76136cb301ba1", 
             data = vacc_ch_age, 
             notes = paste0("* Inkl. Genesene mit einer Impfdosis und Personen, die einen Ein-Dosis-Impfstoff erhalten haben.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", vacc_ch_age_date)),
             title = title)



#Just vacc Speed
ch_vacc_speed <- ch_vacc_doses %>%
   filter(geoRegion == "CHFL", type == "COVID19VaccDosesAdministered") %>%
   mutate(new_vacc_doses = sumTotal-lag(sumTotal, 1, default = 0)) %>%
   mutate(new_vacc_doses_7day = (sumTotal-lag(sumTotal,7, default = 0))/7) %>%
   mutate(new_vacc_doses_7day = round(new_vacc_doses_7day))
 

#write to Q-cli
update_chart(id = "b5f3df8202d94e6cba27c93a5230cd0e",
             data = ch_vacc_speed %>% select(date, new_vacc_doses_7day))



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
         n3 = COVID19FirstBoosterPersons-lag(COVID19FirstBoosterPersons,1),
         n4 = COVID19SecondBoosterPersons-lag(COVID19SecondBoosterPersons,1))%>%
  mutate(Erstimpfungen = rollmean(n1, 7, NA, align = "right"),
         `Zweitimpfungen*` = rollmean(n2, 7, NA, align = "right"),
         `Erste Booster-Impfungen` = rollmean(n3, 7, NA, align = "right"),
         `Zweite Booster-Impfungen` = rollmean(n4, 7, NA, align = "right"))%>%
  select(date, Erstimpfungen, `Zweitimpfungen*`, `Erste Booster-Impfungen`, `Zweite Booster-Impfungen`)

ch_vacc_persons_hist_new$`Erste Booster-Impfungen`[ch_vacc_persons_hist_new$`Erste Booster-Impfungen` < 20] <- NA
ch_vacc_persons_hist_new$`Zweite Booster-Impfungen`[ch_vacc_persons_hist_new$`Zweite Booster-Impfungen` < 20] <- NA

update_chart(id = "82aee9959c2dd62ec398e00a2d3eb5ae",
             data = ch_vacc_persons_hist_new)

# fin
