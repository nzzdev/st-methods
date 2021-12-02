rm(list = ls(all = TRUE))
options(scipen = 999)

library(clipr)
library(tidyverse)
library(readxl)
library(httr)
library(rvest)
library(RCurl)
library(zoo)
library(curl)


# import helper functions
source("./helpers.R")







#######################################################################
# Monitoring Consumption Switzerland -- ALL DATA 
#######################################################################


download <- getURL("https://drive.switch.ch/index.php/s/4JmvjqxKnlmrSVn/download?path=%2F&files=MCS_Overview_Data.csv")
transactions <- read.csv (text = download)


transactions <- subset(transactions, TRANSACTIONS != 'ATM_DEPOSIT')

transactions$Date <- as.Date(transactions$DATE, "%Y-%m-%d")

transactions$week <- strftime(transactions$Date, format = "%V")
transactions$year <- strftime(transactions$Date, format = "%Y")
transactions$year[transactions$week == '53'] <- '2020'

transactions$week_year <- paste0(transactions$year, '-', transactions$week)


transactions <- transactions %>% 
  group_by(week_year) %>% 
  summarise(Total = sum(AMOUNTCHF, na.rm = TRUE))

transactions$week <- substr(transactions$week_year, 6, 7)
transactions$year <- substr(transactions$week_year, 1, 4)

transactions$Datum <- as.Date(paste0(transactions$week_year,'-1'), '%Y-%W-%u') - 7

start = '01'
end = max(subset(transactions,year == 2021)$week)

transactions_2019 = subset(transactions, year == 2019 & week>=start)
transactions_2020 = subset(transactions, year == 2020 & week>=start)
transactions_2021 = subset(transactions, year == 2021 & week>=start)

transactions_2019 <- transactions_2019[order(transactions_2020$Datum),]
transactions_2020 <- transactions_2020[order(transactions_2020$Datum),]
transactions_2021 <- transactions_2021[order(transactions_2021$Datum),]

transactions <- merge(transactions_2020, transactions_2021, by = 'week', all.x = TRUE) %>%
  dplyr::select(week, Total.x, Total.y) %>%
  dplyr::rename(`2021` = Total.y,
                `2020` = Total.x) #%>%
#merge(transactions_2019, by = 'week', all.x = TRUE) %>%
#select(week,`2021`, `2020`, Total) %>%
#rename(`2019` = Total)

transactions <- transactions %>% filter(week != "53")

transactions$week <- paste0('2021-W', transactions$week) 

#q-cli update
update_chart(id = "909e73515b8785336ef65c05d0fa36c7", 
             data = transactions)



#######################################################################
# Monitoring Consumption Switzerland -- Merchant categories
#######################################################################

download <- getURL("https://drive.switch.ch/index.php/s/PSg7Y8Za5LmQ5dn/download?path=%2F2_ACQUIRING%20DATA&files=ACQ_NOGA_Channel.csv") 

merchanttype <- read.csv (text = download) 

merchanttype <- merchanttype %>% 
  group_by(Date, Merchant.category) %>% 
  summarise(All = sum(Amount.CHF))

merchanttype$Date <- as.Date(merchanttype$Date)

merchanttype$week <- strftime(merchanttype$Date, format = "%V")
merchanttype$year <- strftime(merchanttype$Date, format = "%Y")
merchanttype$year[merchanttype$week == '53'] <- '2020'

merchanttype$week_year <- paste0(merchanttype$year, '-', merchanttype$week)

merchanttype <- merchanttype %>% 
  group_by(week_year, Merchant.category) %>% 
  summarise(Total = sum(All, na.rm = TRUE))

merchanttype$week <- substr(merchanttype$week_year, 6, 7)
merchanttype$year <- substr(merchanttype$week_year, 1, 4)

merchanttype$Datum <- as.Date(paste0(merchanttype$week_year,'-1'), '%Y-%W-%u') 

start = '01'
end = max(subset(merchanttype,year == 2021)$week)

merchanttype_2019 = subset(merchanttype, year == 2019 & week>=start)
merchanttype_2020 = subset(merchanttype, year == 2020 & week>=start)
merchanttype_2021 = subset(merchanttype, year == 2021 & week>=start)

merchanttype_2019 <- merchanttype_2019[order(merchanttype_2020$Datum),]
merchanttype_2020 <- merchanttype_2020[order(merchanttype_2020$Datum),]
merchanttype_2021 <- merchanttype_2021[order(merchanttype_2021$Datum),]

merchanttype <- merge(merchanttype_2020, merchanttype_2021, by = c('week', 'Merchant.category'), all.x = TRUE) %>%
  dplyr::select(week, Merchant.category, Total.y, Total.x) %>%
  dplyr::rename(`2021` = Total.y,
                `2020` = Total.x) %>%
  merge(merchanttype_2019, by = c('week', 'Merchant.category'), all.x = TRUE) %>%
  dplyr::select(week, Merchant.category, Total, `2020`, `2021`, Total) %>%
  dplyr::rename(`2019` = Total)

merchanttype <- merchanttype %>% filter(week != "53")
merchanttype$week <- paste0('2021-W', merchanttype$week)

q <- subset(merchanttype, Merchant.category == 'Retail: Food, beverage, tobacco', select = c('week','2019', '2020', '2021'))
update_chart(id = "fa0c8fc6907b186bd970f740254d4c57", 
             data = q)

q <- subset(merchanttype, Merchant.category == 'Accommodation', select = c('week','2019', '2020', '2021'))
update_chart(id = "fa0c8fc6907b186bd970f7402560f664", 
             data = q)

q <- subset(merchanttype, Merchant.category == 'Retail: Other goods', select = c('week','2019', '2020', '2021'))
update_chart(id = "fa0c8fc6907b186bd970f740255f9af7", 
             data = q)

q <- subset(merchanttype, Merchant.category == 'Food and beverage services', select = c('week','2019', '2020', '2021'))
update_chart(id = "47b8b7f460b37c786692405da9c795fd", 
             data = q)




################################
# Google & Apple Mobility Data
################################

URL <- 'https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip'
h <- new_handle()
handle_setopt(h, ssl_verifyhost = 0, ssl_verifypeer=0)
curl_download(url=URL, "Region_Mobility_Report_CSVs.zip", handle = h)
unzip("Region_Mobility_Report_CSVs.zip", files = c("2020_CH_Region_Mobility_Report.csv", "2020_AT_Region_Mobility_Report.csv", "2020_DE_Region_Mobility_Report.csv",
                                                   "2021_CH_Region_Mobility_Report.csv", "2021_AT_Region_Mobility_Report.csv", "2021_DE_Region_Mobility_Report.csv"))

gmr_ch <- rbind(read_csv("2020_CH_Region_Mobility_Report.csv"), read_csv("2021_CH_Region_Mobility_Report.csv"))  %>%
  filter(is.na(sub_region_1)) %>%
  mutate(retail_and_recreation_percent_change_from_baseline = rollmean(retail_and_recreation_percent_change_from_baseline, 7, fill = 0, align = "right"),
         grocery_and_pharmacy_percent_change_from_baseline = rollmean(grocery_and_pharmacy_percent_change_from_baseline, 7, fill = 0, align = "right"),
         transit_stations_percent_change_from_baseline = rollmean(transit_stations_percent_change_from_baseline, 7, fill = 0, align = "right"),
         workplaces_percent_change_from_baseline = rollmean(workplaces_percent_change_from_baseline, 7, fill = 0, align = "right"),
         residential_percent_change_from_baseline = rollmean(residential_percent_change_from_baseline, 7, fill = 0, align = "right")
         ) %>%
  filter(date >= '2020-02-21') %>%
  mutate(Schweiz = (retail_and_recreation_percent_change_from_baseline + grocery_and_pharmacy_percent_change_from_baseline + transit_stations_percent_change_from_baseline + workplaces_percent_change_from_baseline)/4 ) %>%
  dplyr::select(date, Schweiz)

gmr_at <- rbind(read_csv("2020_AT_Region_Mobility_Report.csv"), read_csv("2021_AT_Region_Mobility_Report.csv"))  %>%
  filter(is.na(sub_region_1)) %>%
  mutate(retail_and_recreation_percent_change_from_baseline = rollmean(retail_and_recreation_percent_change_from_baseline, 7, fill = 0, align = "right"),
         grocery_and_pharmacy_percent_change_from_baseline = rollmean(grocery_and_pharmacy_percent_change_from_baseline, 7, fill = 0, align = "right"),
         transit_stations_percent_change_from_baseline = rollmean(transit_stations_percent_change_from_baseline, 7, fill = 0, align = "right"),
         workplaces_percent_change_from_baseline = rollmean(workplaces_percent_change_from_baseline, 7, fill = 0, align = "right"),
         residential_percent_change_from_baseline = rollmean(residential_percent_change_from_baseline, 7, fill = 0, align = "right")
         ) %>%
  filter(date >= '2020-02-21') %>%
  mutate(`Österreich` = (retail_and_recreation_percent_change_from_baseline + grocery_and_pharmacy_percent_change_from_baseline + transit_stations_percent_change_from_baseline + workplaces_percent_change_from_baseline)/4 ) %>%
  dplyr::select(date, `Österreich`)

gmr_de <- rbind(read_csv("2020_DE_Region_Mobility_Report.csv"), read_csv("2021_DE_Region_Mobility_Report.csv"))  %>%
  filter(is.na(sub_region_1)) %>%
  mutate(retail_and_recreation_percent_change_from_baseline = rollmean(retail_and_recreation_percent_change_from_baseline, 7, fill = 0, align = "right"),
         grocery_and_pharmacy_percent_change_from_baseline = rollmean(grocery_and_pharmacy_percent_change_from_baseline, 7, fill = 0, align = "right"),
         transit_stations_percent_change_from_baseline = rollmean(transit_stations_percent_change_from_baseline, 7, fill = 0, align = "right"),
         workplaces_percent_change_from_baseline = rollmean(workplaces_percent_change_from_baseline, 7, fill = 0, align = "right"),
         residential_percent_change_from_baseline = rollmean(residential_percent_change_from_baseline, 7, fill = 0, align = "right")
         ) %>%
  filter(date >= '2020-02-21') %>%
  mutate(Deutschland = (retail_and_recreation_percent_change_from_baseline + grocery_and_pharmacy_percent_change_from_baseline + transit_stations_percent_change_from_baseline + workplaces_percent_change_from_baseline)/4 ) %>%
  dplyr::select(date, Deutschland)

gmr_ch_at <- merge(gmr_ch, gmr_at, by = 'date')
gmr <- merge(gmr_ch_at, gmr_de, by = 'date')

update_chart(id = "101552dc3a2c51542953caad1e8a4bee", 
             data = gmr)

update_chart(id = "6069088c960d0f055227f901b977a49b", 
             data = gmr_ch_at)






########################################
# OENB-Index
########################################

pg <- read_html("https://www.oenb.at/Publikationen/corona/bip-indikator-der-oenb.html")

# get all the Excel (xlsx) links on that page:

html_nodes(pg, xpath=".//a[contains(@href, '.xlsx')]") %>% 
  html_attr("href") %>% 
  sprintf("https://www.oenb.at%s", .) -> excel_links

url <- excel_links[1]
GET(url, write_disk(tf <- tempfile(fileext = ".xlsx")))
oenb <- read_excel(tf, sheet="Wochen-BIP-Indikator", skip = 13)

oenb <- oenb[ -c(1,2) ]
oenb <- oenb %>% drop_na(Tourismusexporte)
names(oenb)[1] <- "Datum"
oenb$Datum <- gsub(' K', '-', oenb$Datum)

q <- oenb[,c(1:7)]
update_chart(id = "84daeadb234674f39b55f90454fca893", 
             data = q)



##############################################################
# täglicher Lkw-Maut-Fahrleistungsindex
##############################################################

pg <- read_html("https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Industrie-Verarbeitendes-Gewerbe/Tabellen/Lkw-Maut-Fahrleistungsindex-Daten.html")
html_nodes(pg, xpath=".//a[contains(@href, '.xlsx')]") %>% 
  html_attr("href") %>% 
  sprintf("https://www.destatis.de%s", .) -> excel_links

url <- excel_links
GET(url, write_disk(tf <- tempfile(fileext = ".xlsx")))
destatis <- read_excel(tf, sheet = 'Daten', skip = 5)

destatis <- destatis %>% drop_na()

destatis <- destatis[,c('Datum','Kalenderwoche','gleitender 7-Tage-Durchschnitt KSB')]
names(destatis)[3] <- "KSB"

destatis$Jahr <- strftime(destatis$Datum, format = "%Y")
destatis$mw <- substring(destatis$Datum, 6, 10)

start = 1

destatis_2021 = subset(destatis, Jahr == 2021 & Kalenderwoche>=start)

destatis_2020 = subset(destatis, Jahr == 2020 & Kalenderwoche>=start)

destatis_2019 = subset(destatis, Jahr == 2019 & Kalenderwoche>=start)

destatis_2019 <- destatis_2019[order(destatis_2019$Datum),]
destatis_2020 <- destatis_2020[order(destatis_2020$Datum),]
destatis_2021 <- destatis_2021[order(destatis_2021$Datum),]

q <- destatis_2021[,c('Datum', 'KSB', 'mw')] %>%
  merge(destatis_2020[,c('Datum', 'KSB', 'mw')], by = "mw" , all.x = TRUE, all.y = TRUE) %>%
  dplyr::select(mw, KSB.x, KSB.y) %>%
  dplyr::rename(`2021` = KSB.x, `2020` = KSB.y) %>%
  merge(destatis_2019[,c('Datum', 'KSB', 'mw')], by = "mw" , all.x = TRUE, all.y = TRUE) %>%
  mutate(Datum = paste0('2021-',mw)) %>%
  dplyr::select(Datum, KSB, `2020`, `2021`) %>%
  dplyr::rename(`2019` = KSB)

update_chart(id = "cb6f52d578153c0940c03f120020de0e", 
             data = q)


###################################################################################
# U.S. consumer spending 
###################################################################################

us <- read_csv("https://raw.githubusercontent.com/Opportunitylab/EconomicTracker/main/data/Affinity%20-%20National%20-%20Daily.csv")

us$date <- as.Date(with(us, paste(year, month, day,sep="-")), "%Y-%m-%d")

q <- subset(us, select = c("date", "spend_all"))
q$spend_all <- as.numeric(q$spend_all)
q$spend_all <- q$spend_all*100
q <- subset(q, date >= '2020-01-07')

update_chart(id = "68a474c4f6f4b2503669c110cedae580", 
             data = q)



########################################################################
# Zurich airport departures
########################################################################

zh_airport_departures <- read_csv('https://raw.githubusercontent.com/KOF-ch/economic-monitoring/master/data/ch.zrh_airport.departures.csv')
zh_airport_departures <- subset(zh_airport_departures, rnwy == 'all' & route == 'total' & time >= '2019-01-01' & time <= Sys.Date(), 
                                select = c('time', 'value'))

zh_airport_departures <- zh_airport_departures %>%
  mutate(mean = rollmean(value, 7, fill = 0, align = "right"))

zh_airport_departures$Jahr <- strftime(zh_airport_departures$time, format = "%Y")
zh_airport_departures$Datum <- substring(zh_airport_departures$time, 6, 10)

zh_airport_departures_2021 <- subset(zh_airport_departures, select = c('Datum', 'Jahr', 'mean'), Jahr == 2021 & time >= '2021-01-01') %>%
  dplyr::rename(`2021` = mean)
zh_airport_departures_2020 <- subset(zh_airport_departures, select = c('Datum', 'Jahr', 'mean'), Jahr == 2020 & time >= as.Date('2021-01-01') - 366) %>%
  dplyr::rename(`2020` = mean, Jahr_2020 = Jahr)
zh_airport_departures_2019 <- subset(zh_airport_departures, select = c('Datum', 'Jahr', 'mean'), Jahr == 2019 & time >= as.Date('2021-01-01') - 366 - 365) %>%
  dplyr::rename(`2019` = mean, Jahr_2019 = Jahr) %>%
  mutate(`2019` = na_if(`2019`, 0))



zh_airport_departures <- merge(zh_airport_departures_2020, zh_airport_departures_2019, by = 'Datum', all.x = TRUE)
zh_airport_departures <- merge(zh_airport_departures, zh_airport_departures_2021, by = 'Datum', all.x = TRUE)

zh_airport_departures <- subset(zh_airport_departures, select = c('Datum', 'Jahr', '2019', '2020', '2021'))
zh_airport_departures$Datum <- paste0('2021-', zh_airport_departures$Datum) 
zh_airport_departures$Jahr <- NULL

update_chart(id = "e009c0862e7418ee009c6b89abca6339", 
             data = zh_airport_departures)


###########################################################
# Labor market
###########################################################

job_room <- read_csv('https://raw.githubusercontent.com/KOF-ch/economic-monitoring/master/data/ch.seco.jobroom.candidates.csv')

job_room <- subset(job_room, availability == 'tot' & geo == 'tot')
job_room$date <- substr(job_room$time, 6, 10)

job_room_2021 <- subset(job_room, time >= '2021-01-04', select = c('date', 'value')) %>%
  dplyr::rename(`2021` = value)
job_room_2020 <- subset(job_room, time >= as.Date('2021-01-04') - 366 & time <= '2020-12-31', select = c('date', 'value')) %>%
  dplyr::rename(`2020` = value)
job_room_2019 <- subset(job_room, time >= as.Date('2021-01-04') - 366 - 365 & time <= '2019-12-31', select = c('date', 'value')) %>%
  dplyr::rename(`2019` = value)

job_room <- merge(job_room_2020, job_room_2019, by = 'date')
job_room <- merge(job_room, job_room_2021, by = 'date', all.x = TRUE)
job_room$date <- paste0('2021-', job_room$date) 

job_room <- job_room[, c('date', '2019', '2020', '2021')]

update_chart(id = "0efbe12a71b5a3de14e8d10edb77724d", 
             data = job_room)

burning_glass <- read_csv('https://raw.githubusercontent.com/OpportunityInsights/EconomicTracker/main/data/Burning%20Glass%20-%20National%20-%20Weekly.csv')

burning_glass$date <- as.Date(as.character(paste0(burning_glass$year,"-",burning_glass$month,"-",burning_glass$day_endofweek)), format="%Y-%m-%d")
burning_glass <- subset(burning_glass, select = c('date', 'bg_posts'))
burning_glass$bg_posts <- burning_glass$bg_posts*100

update_chart(id = "0efbe12a71b5a3de14e8d10edb7abf60", 
             data = burning_glass)



####################################
# Oxford policy tracker
####################################

oxford <- read_csv('https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv') %>%
  mutate(Date = as.Date(as.character(Date), format="%Y%m%d"))

oxford$Land <- countrycode(oxford$`CountryName`, 'country.name', 'cldr.short.de_ch')

oxford$Land <- car::recode(oxford$Land, '"Vereinigte Arabische Emirate"="VAE"')
oxford$Land <- car::recode(oxford$Land, '"Saudi-Arabien"="Saudiarabien"')
oxford$Land <- car::recode(oxford$Land, '"Bosnien und Herzegowina" = "Bosnien-Herz."')
oxford$Land <- car::recode(oxford$Land, '"Nordmazedonien" = "Nordmazed."')
oxford$Land <- car::recode(oxford$Land, '"Republik Moldau" = "Moldau"')
oxford$Land <- car::recode(oxford$Land, '"Trinidad und Tobago" = "Trinidad u. T."')
oxford$Land <- car::recode(oxford$Land, '"Dominikanische Republik" = "Dominikan. Rep."')
oxford$Land <- car::recode(oxford$Land, '"Bangladesch" = "Bangladesh"')
oxford$Land <- car::recode(oxford$Land, '"Zimbabwe" = "Simbabwe"')
oxford$Land <- car::recode(oxford$Land, '"Kirgisistan" = "Kirgistan"')


# OECD countries + BRICS
oecd_brics <- c('Belgien',
                'Dänemark', 
                'Deutschland', 
                'Frankreich', 
                'Griechenland', 
                'Irland',
                'Island', 
                'Italien', 
                'Kanada', 
                'Luxemburg', 
                'Niederlande', 
                'Norwegen', 
                'Österreich', 
                'Portugal', 
                'Schweden', 
                'Schweiz', 
                'Spanien', 
                'Türkei', 
                'USA', 
                'GB', 
                'Japan', 
                'Finnland', 
                'Australien', 
                'Neuseeland', 
                'Mexiko', 
                'Tschechien', 
                'Südkorea', 
                'Ungarn', 
                'Polen', 
                'Slowakei', 
                'Chile', 
                'Slowenien', 
                'Israel', 
                'Estland', 
                'Lettland', 
                'Litauen', 
                'Kolumbien', 
                'Costa Rica', 
                'China',
                'Russland',
                'Brasilien',
                'Indien',
                'Südafrika')

oxford_countries <- oxford  %>%
  filter(Land %in% oecd_brics) %>%
  drop_na(StringencyIndexForDisplay) %>%
  arrange(Land, Date) %>%
  mutate(pct_of_max = (StringencyIndexForDisplay*100) / max(StringencyIndexForDisplay, na.rm = T)) %>%
  mutate(diff_pct_max = pct_of_max - lag(pct_of_max, 14, default = 0)) %>%
  mutate(Tendenz = case_when 
         (diff_pct_max > 5 ~ '\U2191', 
           diff_pct_max < -5 ~ '\U2193',
           TRUE ~ '\U2192',)) %>%
  mutate(StringencyIndexForDisplay = round(StringencyIndexForDisplay, 1)) %>%
  filter(Date == last(Date)) %>%
  select(Land, StringencyIndexForDisplay, Tendenz) %>%
  arrange(desc(StringencyIndexForDisplay)) %>%
  dplyr::rename(`Stringency Index` = StringencyIndexForDisplay) 

notes <- paste0("Lesebeispiel: In ", first(oxford_countries$Land), " betragen die Einschränkungen des öffentlichen Lebens ",  first(round(oxford_countries$`Stringency Index`)), "% des maximalen Niveaus von 100%. <br>Berücksichtigt werden alle OECD- und BRICS-Länder. Als sinkend bzw. steigend gilt eine Entwicklung, wenn der aktuelle Wert im Vergleich zum Maximalwert des Landes in den letzten 14 Tagen um 5 Prozentpunkte ab- bzw. zugenommen hat. GB = Grossbritannien, VAE = Vereinigte Arabische Emirate. <br>Stand: ", format(last(oxford$Date), format = "%d. %m. %Y"))

update_chart(id = "e3eab39da5788b8d4701823ac92fc244", 
             data = oxford_countries, notes = notes)



