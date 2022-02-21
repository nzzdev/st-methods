##### Script for Coronacases INTERNATIONAL ####

#prep
rm(list=ls(all=TRUE)) 
options(scipen=999)
library(tidyverse)
library(zoo)
library(countrycode)
library(car)


# import helper functions
source("./helpers.R")

# get data from JHU
cases <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
dead <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
cured <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

# get population figures
un <- read_csv("./corona-auto-int/un_pop.csv")

cases$Land <- countrycode(cases$`Country/Region`, 'country.name', 'cldr.short.de_ch')
dead$Land <- countrycode(dead$`Country/Region`, 'country.name', 'cldr.short.de_ch')
cured$Land <- countrycode(cured$`Country/Region`, 'country.name', 'cldr.short.de_ch')
cases$Region <- countrycode(cases$`Province/State`, 'country.name', 'cldr.short.de_ch')
dead$Region <- countrycode(dead$`Province/State`, 'country.name', 'cldr.short.de_ch')
cured$Region <- countrycode(cured$`Province/State`, 'country.name', 'cldr.short.de_ch')

cases$Land[cases$Region == "Macau"] <- "Macau"
cases$Land[cases$Region == "Hongkong"] <- "Hongkong"
dead$Land[dead$Region == "Macau"] <- "Macau"
dead$Land[dead$Region == "Hongkong"] <- "Hongkong"
cured$Land[cured$Region == "Macau"] <- "Macau"
cured$Land[cured$Region == "Hongkong"] <- "Hongkong"


#to long, get total per date and place
cases_crty <- cases %>%
  gather(date, value, 5:(ncol(cases)-2)) %>%
  group_by(date, Land) %>%
  summarise(first(`Country/Region`), cases = sum(value, na.rm = T))

dead_ctry <- dead %>%
  gather(date, value, 5:(ncol(dead)-2)) %>%
  group_by(date, Land) %>%
  summarise(first(`Country/Region`), dead = sum(value, na.rm = T))

cured_ctry <- cured %>%
  gather(date, value, 5:(ncol(cured)-2)) %>%
  group_by(date, Land) %>%
  summarise(first(`Country/Region`), cured = sum(value, na.rm = T))

#merge
all_ctry <- cbind(as_tibble(dead_ctry), cases_crty$cases)
all_ctry <- left_join(all_ctry, cured_ctry, by = c("date" = "date", "Land" = "Land")) %>%
  select(-6)

#adapt for Q date format
all_ctry$date <- as.Date(all_ctry$date, format = "%m/%d/%y")
all_ctry <- arrange(all_ctry, date)

#calc sick, rename
all_ctry$sick <- all_ctry$`cases_crty$cases`-all_ctry$dead-all_ctry$cured
all_ctry <- all_ctry %>%  dplyr::rename(country = 3, all_cases = 5)

#### CORRECTIONS (not beautiful, run it all at once) ####

#spain deaths adjust
cum_spain_deaths <- all_ctry$dead[all_ctry$country == "Spain" & all_ctry$date < "2020-05-25"]
new_spain_deaths <- cum_spain_deaths - lag(cum_spain_deaths,1)
new_spain_deaths[1] <- 0
corr_spain_deaths <- -((new_spain_deaths/28752)*1918)
cum_spain_deaths_check <- cumsum(new_spain_deaths+corr_spain_deaths)
all_ctry$dead[all_ctry$country == "Spain" & all_ctry$date < "2020-05-25"] <- cum_spain_deaths_check

#spain_2 deaths adjust
cum_spain_2_deaths <- all_ctry$dead[all_ctry$country == "Spain" & all_ctry$date < "2020-06-19"]
new_spain_2_deaths <- cum_spain_2_deaths - lag(cum_spain_2_deaths,1)
new_spain_2_deaths[1] <- 0
corr_spain_2_deaths <- ((new_spain_2_deaths/27136)*1179)
cum_spain_2_deaths_check <- cumsum(new_spain_2_deaths+corr_spain_2_deaths)
all_ctry$dead[all_ctry$country == "Spain" & all_ctry$date < "2020-06-19"] <- cum_spain_2_deaths_check

#chile deaths adjust
cum_chile_deaths <- all_ctry$dead[all_ctry$country == "Chile" & all_ctry$date < "2020-07-17"]
new_chile_deaths <- cum_chile_deaths - lag(cum_chile_deaths,1)
new_chile_deaths[1] <- 0
corr_chile_deaths <- ((new_chile_deaths/7290)*1057)
cum_chile_deaths_check <- cumsum(new_chile_deaths+corr_chile_deaths)
all_ctry$dead[all_ctry$country == "Chile" & all_ctry$date < "2020-07-17"] <- cum_chile_deaths_check

#peru deaths adjust
cum_peru_deaths <- all_ctry$dead[all_ctry$country == "Peru" & all_ctry$date < "2020-07-23"]
new_peru_deaths <- cum_peru_deaths - lag(cum_peru_deaths,1)
new_peru_deaths[1] <- 0
corr_peru_deaths <- ((new_peru_deaths/13767)*3887)
cum_peru_deaths_check <- cumsum(new_peru_deaths+corr_peru_deaths)
all_ctry$dead[all_ctry$country == "Peru" & all_ctry$date < "2020-07-23"] <- cum_peru_deaths_check

#peru_2 deaths adjust
cum_peru_2_deaths <- all_ctry$dead[all_ctry$country == "Peru" & all_ctry$date < "2020-08-14"]
new_peru_2_deaths <- cum_peru_2_deaths - lag(cum_peru_2_deaths,1)
new_peru_2_deaths[1] <- 0
corr_peru_2_deaths <- ((new_peru_2_deaths/21713)*4143)
cum_peru_2_deaths_check <- cumsum(new_peru_2_deaths+corr_peru_2_deaths)
all_ctry$dead[all_ctry$country == "Peru" & all_ctry$date < "2020-08-14"] <- cum_peru_2_deaths_check

#peru_3 deaths adjust
cum_peru_3_deaths <- all_ctry$dead[all_ctry$country == "Peru" & all_ctry$date < "2021-06-02"]
new_peru_3_deaths <- cum_peru_3_deaths - lag(cum_peru_3_deaths,1)
new_peru_3_deaths[1] <- 0
corr_peru_3_deaths <- ((new_peru_3_deaths/69342)*115600)
cum_peru_3_deaths_check <- cumsum(new_peru_3_deaths+corr_peru_3_deaths)
all_ctry$dead[all_ctry$country == "Peru" & all_ctry$date < "2021-06-02"] <- cum_peru_3_deaths_check

#france cases adjust
cum_fra_cases <- all_ctry$all_cases[all_ctry$country == "France" & all_ctry$date < "2020-04-12"]
new_fra_cases <- cum_fra_cases - lag(cum_fra_cases,1)
new_fra_cases[1] <- 0
corr_fra_cases <- ((new_fra_cases/94863)*26849)
cum_fra_cases_check <- cumsum(new_fra_cases+corr_fra_cases)
all_ctry$all_cases[all_ctry$country == "France" & all_ctry$date < "2020-04-12"] <- cum_fra_cases_check

#india deaths adjust
cum_india_deaths <- all_ctry$dead[all_ctry$country == "India" & all_ctry$date < "2020-06-16"]
new_india_deaths <- cum_india_deaths - lag(cum_india_deaths,1)
new_india_deaths[1] <- 0
corr_india_deaths <- ((new_india_deaths/9900)*2003)
cum_india_deaths_check <- cumsum(new_india_deaths+corr_india_deaths)
all_ctry$dead[all_ctry$country == "India" & all_ctry$date < "2020-06-16"] <- cum_india_deaths_check

#ecuador deaths adjust
cum_ecuador_deaths <- all_ctry$dead[all_ctry$country == "Ecuador" & all_ctry$date < "2020-09-07"]
new_ecuador_deaths <- cum_ecuador_deaths - lag(cum_ecuador_deaths,1)
new_ecuador_deaths[1] <- 0
corr_ecuador_deaths <- ((new_ecuador_deaths/6724)*3852)
cum_ecuador_deaths_check <- cumsum(new_ecuador_deaths+corr_ecuador_deaths)
all_ctry$dead[all_ctry$country == "Ecuador" & all_ctry$date < "2020-09-07"] <- cum_ecuador_deaths_check

#ecuador deaths adjust
cum_ecuador_deaths_2 <- all_ctry$dead[all_ctry$country == "Ecuador" & all_ctry$date < "2021-07-20"]
new_ecuador_deaths_2 <- cum_ecuador_deaths_2 - lag(cum_ecuador_deaths_2,1)
new_ecuador_deaths_2[1] <- 0
corr_ecuador_deaths_2 <- ((new_ecuador_deaths_2/21958)*8839)
cum_ecuador_deaths_2_check <- cumsum(new_ecuador_deaths_2+corr_ecuador_deaths_2)
all_ctry$dead[all_ctry$country == "Ecuador" & all_ctry$date < "2021-07-20"] <- cum_ecuador_deaths_2_check

#bolivia deaths adjust
cum_bolivia_deaths <- all_ctry$dead[all_ctry$country == "Bolivia" & all_ctry$date < "2020-09-07"]
new_bolivia_deaths <- cum_bolivia_deaths - lag(cum_bolivia_deaths,1)
new_bolivia_deaths[1] <- 0
corr_bolivia_deaths <- ((new_bolivia_deaths/5398)*1656)
cum_bolivia_deaths_check <- cumsum(new_bolivia_deaths+corr_bolivia_deaths)
all_ctry$dead[all_ctry$country == "Bolivia" & all_ctry$date < "2020-09-07"] <- cum_bolivia_deaths_check

#ch deaths adjust
cum_ch_deaths <- all_ctry$dead[all_ctry$country == "Switzerland" & all_ctry$date < "2020-10-21"]
new_ch_deaths <- cum_ch_deaths - lag(cum_ch_deaths,1)
new_ch_deaths[1] <- 0
corr_ch_deaths <- -((new_ch_deaths/2145)*106)
cum_ch_deaths_check <- cumsum(new_ch_deaths+corr_ch_deaths)
all_ctry$dead[all_ctry$country == "Switzerland" & all_ctry$date < "2020-10-21"] <- cum_ch_deaths_check

#turkey cases adjust
cum_tur_cases <- all_ctry$all_cases[all_ctry$country == "Turkey" & all_ctry$date < "2020-12-10"]
new_tur_cases <- cum_tur_cases - lag(cum_tur_cases,1)
new_tur_cases[1] <- 0
corr_tur_cases <- ((new_tur_cases/955766)*824907)
cum_tur_cases_check <- cumsum(new_tur_cases+corr_tur_cases)
all_ctry$all_cases[all_ctry$country == "Turkey" & all_ctry$date < "2020-12-10"] <- cum_tur_cases_check

#argentina deaths adjust
cum_arg_deaths <- all_ctry$dead[all_ctry$country == "Argentina" & all_ctry$date < "2020-10-01"]
new_arg_deaths <- cum_arg_deaths - lag(cum_arg_deaths,1)
new_arg_deaths[1] <- 0
corr_arg_deaths <- (new_arg_deaths/16937)*3351
cum_arg_deaths_argeck <- cumsum(new_arg_deaths+corr_arg_deaths)
all_ctry$dead[all_ctry$country == "Argentina" & all_ctry$date < "2020-10-01"] <- cum_arg_deaths_argeck

#nepal deaths adjust
cum_nep_deaths <- all_ctry$dead[all_ctry$country == "Nepal" & all_ctry$date < "2021-02-24"]
new_nep_deaths <- cum_nep_deaths - lag(cum_nep_deaths,1)
new_nep_deaths[1] <- 0
corr_nep_deaths <- (new_nep_deaths/2065)*619
cum_nep_deaths_nepeck <- cumsum(new_nep_deaths+corr_nep_deaths)
all_ctry$dead[all_ctry$country == "Nepal" & all_ctry$date < "2021-02-24"] <- cum_nep_deaths_nepeck

#us-corr-recovered (they are not included anymore)
all_ctry$sick[all_ctry$country == "US"] <- all_ctry$all_cases[all_ctry$country == "US"]
all_ctry$cured[all_ctry$country == "US"] <- 0

#### 7-day averages ####

rolling_average_all <- all_ctry %>%
  group_by(Land, date) %>%
  summarise(all_cases = sum(all_cases, na.rm = T), dead = sum(dead, na.rm = T)) %>%
  group_by(Land) %>%
  mutate(new_deaths = dead-lag(dead,1)) %>%
  mutate(new_deaths = case_when(new_deaths < 0 ~ 0, is.na(new_deaths) ~ 0, TRUE ~ new_deaths)) %>%
  mutate(ravg_deaths = rollmean(new_deaths, 7, fill = 0, align = "right")) %>%
  mutate(new_cases = all_cases-lag(all_cases,1)) %>%
  mutate(new_cases = case_when(new_cases < 0 ~ 0, is.na(new_cases) ~ 0, TRUE ~ new_cases)) %>%
  mutate(ravg_cases = rollmean(new_cases, 7, fill = 0, align = "right")) %>%
  left_join(un, by = c("Land"= "Land")) %>%
  select(date, continent, region_2, Land, entity, ravg_cases, ravg_deaths, all_cases, dead, pop) %>%
  mutate(ravg_cases_pop = ravg_cases/(pop/100000)) %>%
  mutate(ravg_deaths_pop = ravg_deaths/(pop/1000000))

#change country names if necessary for matching and displaying
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Vereinigte Arabische Emirate"="VAE"')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Saudi-Arabien"="Saudiarabien"')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Bosnien und Herzegowina" = "Bosnien-Herz."')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Nordmazedonien" = "Nordmazed."')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Republik Moldau" = "Moldau"')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Trinidad und Tobago" = "Trinidad u. T."')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Dominikanische Republik" = "Dominikan. Rep."')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Bangladesch" = "Bangladesh"')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Zimbabwe" = "Simbabwe"')
rolling_average_all$Land <- recode(rolling_average_all$Land, '"Kirgisistan" = "Kirgistan"')


continents <- rolling_average_all %>%
  select(date, continent, Land, all_cases) %>%
  filter(date == last(date)) %>%
  group_by(continent) %>%
  slice_max(order_by = all_cases, n = 5) %>%
  drop_na() %>%
  ungroup()


rolling_average_continents <- rolling_average_all  %>%
  select(continent, Land, date, ravg_cases_pop) %>%
  filter(Land %in% continents$Land & date >= '2020-03-01')





#### Vaccinations ####

vaccination <- read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv",
                        col_types = cols(
                          total_boosters = col_double(),
                          total_boosters_per_hundred = col_double()
                        )) %>%
  rename(Land = location,
         Iso = iso_code,
         Datum = date,
         Impfdosen_total = total_vaccinations,
         Personen_total = people_vaccinated,
         Personen_komplett = people_fully_vaccinated,
         Booster = total_boosters,
         Impfdosen_daily_raw = daily_vaccinations_raw,
         Impfdosen_daily = daily_vaccinations,
         Impfdosen_total_100 = total_vaccinations_per_hundred,
         "Mind. eine Impfdose, in % der Bev." = people_vaccinated_per_hundred,
         "Doppelt geimpft, in % der Bev." = people_fully_vaccinated_per_hundred,
         "Booster-Impfungen, in % der Bev." = total_boosters_per_hundred,
         "Täglich verabreichte Impfdosen, pro 1000 Einw." = daily_vaccinations_per_million
         )

world <- vaccination %>%
  filter(Land == "World") %>%
  select(Datum, Impfdosen_total)

title_world <- paste0("Weltweit wurden über ", str_sub(last(world$Impfdosen_total)/1000000000,1,2), " Milliarden Impfdosen verabreicht")

update_chart(id = "83dcb25c0e922ac143111ad204e65d15", data = world, title = title_world)


vaccination$Land <- countrycode(vaccination$Land, 'country.name', 'cldr.short.de_ch')

vaccination <- merge(vaccination, un, by = "Land", all.x = TRUE) %>%
  filter(Iso != "OWID_CYN")

vaccination$Land <- recode(vaccination$Land, '"Vereinigte Arabische Emirate"="VAE"')
vaccination$Land <- recode(vaccination$Land, '"Saudi-Arabien"="Saudiarabien"')
vaccination$Land <- recode(vaccination$Land, '"Bosnien und Herzegowina" = "Bosnien-Herz."')
vaccination$Land <- recode(vaccination$Land, '"Nordmazedonien" = "Nordmazed."')
vaccination$Land <- recode(vaccination$Land, '"Republik Moldau" = "Moldau"')
vaccination$Land <- recode(vaccination$Land, '"Trinidad und Tobago" = "Trinidad u. T."')
vaccination$Land <- recode(vaccination$Land, '"Dominikanische Republik" = "Dominikan. Rep."')
vaccination$Land <- recode(vaccination$Land, '"Bangladesch" = "Bangladesh"')
vaccination$Land <- recode(vaccination$Land, '"Zimbabwe" = "Simbabwe"')
vaccination$Land <- recode(vaccination$Land, '"Kirgisistan" = "Kirgistan"')



# Vaccinated people (at least one dose) in percent
vacc <- vaccination %>%
  drop_na(Land) %>%
  drop_na(`Mind. eine Impfdose, in % der Bev.`) %>%
  group_by(Land) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) %>%
  filter(Land != 'World', pop > 1000000) %>%
  slice_max(order_by = Datum, n = 1) %>%
  arrange(desc(`Mind. eine Impfdose, in % der Bev.`)) %>%
  select(Land, `Mind. eine Impfdose, in % der Bev.`) %>%
  mutate(`Mind. eine Impfdose, in % der Bev.` = round(`Mind. eine Impfdose, in % der Bev.`, 1)) %>%
  ungroup()

# fully vaccinated people in percent
full_vacc <- vaccination %>%
  drop_na(Land) %>%
  drop_na(`Doppelt geimpft, in % der Bev.`) %>%
  group_by(Land) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) %>%
  filter(Land != 'World', pop > 1000000, `Doppelt geimpft, in % der Bev.` > 0) %>%
  slice_max(order_by = Datum, n = 1) %>%
  arrange(desc(`Doppelt geimpft, in % der Bev.`)) %>%
  select(Land, `Doppelt geimpft, in % der Bev.`) %>%
  mutate(`Doppelt geimpft, in % der Bev.` = round(`Doppelt geimpft, in % der Bev.`, 1)) %>%
  ungroup()

notes <- paste0("Länder mit mehr als 1 Million Einwohnern. GB = Grossbritannien, VAE = Vereinigte Arabische Emirate.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(vaccination$Datum), format = "%d. %m. %Y")))
update_chart(id = 'ee2ce1d4bd795db54ef74a9ed8abb147', data = full_vacc, notes = notes)


booster <- vaccination %>%
  drop_na(Land) %>%
  drop_na(`Booster-Impfungen, in % der Bev.`) %>%
  group_by(Land) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) %>%
  filter(Land != 'World', pop > 1000000, `Booster-Impfungen, in % der Bev.` > 0) %>%
  slice_max(order_by = Datum, n = 1) %>%
  arrange(desc(`Booster-Impfungen, in % der Bev.`)) %>%
  select(Land, `Booster-Impfungen, in % der Bev.`) %>%
  mutate(`Booster-Impfungen, in % der Bev.` = round(`Booster-Impfungen, in % der Bev.`, 1)) %>%
  ungroup()

title <- paste(head(booster$Land, 1), "ist mit den Booster-Impfungen schon weit fortgeschritten" )

notes <- paste0("Länder mit mehr als 1 Million Einwohnern. GB = Grossbritannien, VAE = Vereinigte Arabische Emirate.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(vaccination$Datum), format = "%d. %m. %Y")))
update_chart(id = '33696d9875c026f74a2335377666f2b8', data = booster, notes = notes, title = title)


booster_10 <- vaccination %>%
  drop_na(Land) %>%
  drop_na(`Booster-Impfungen, in % der Bev.`) %>%
  group_by(Land) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) %>%
  filter(Land != 'World', Land != 'Deutschland', pop > 1000000) %>%
  slice_max(order_by = Datum, n = 1) %>%
  arrange(desc(`Booster-Impfungen, in % der Bev.`)) %>%
  select(Land, `Booster-Impfungen, in % der Bev.`, `Doppelt geimpft, in % der Bev.`) %>%
  mutate(`Booster-Impfungen, in % der Bev.` = round(`Booster-Impfungen, in % der Bev.`, 1)) %>%
  mutate(`Doppelt geimpft, in % der Bev.` = round(`Doppelt geimpft, in % der Bev.`, 1)) %>%
  ungroup() %>% slice(1:20)

booster_d <- vaccination %>%
  drop_na(Land) %>%
  drop_na(`Booster-Impfungen, in % der Bev.`) %>%
  group_by(Land) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) %>%
  filter(Land == 'Deutschland') %>%
  slice_max(order_by = Datum, n = 1) %>%
  select(Land, `Booster-Impfungen, in % der Bev.`, `Doppelt geimpft, in % der Bev.`) %>%
  mutate(`Booster-Impfungen, in % der Bev.` = round(`Booster-Impfungen, in % der Bev.`, 1)) %>%
  mutate(`Doppelt geimpft, in % der Bev.` = round(`Doppelt geimpft, in % der Bev.`, 1))

booster_d <- rbind(booster_d, booster_10) %>%
  dplyr::rename('Booster-Impfungen' = 2, 'Doppelt geimpft' = 3)

notes <- paste0("Die Tabelle zeigt die 20 Länder ab einer Million Einwohner mit den meisten Booster-Impfungen sowie Deutschland. <br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(vaccination$Datum), format = "%d. %m. %Y")))
update_chart(id = 'e8f976e14bac8280d4b908f99e49f8d6', data = booster_d, notes = notes)





#### for Newsroom ####
# 14-day Incidence

combo_table <- rolling_average_all %>%
  group_by(Land, date) %>%
  summarise(cases_all = sum(all_cases), deaths_all = sum(dead), pop = first(pop)) %>%
  mutate(cases_new14 = cases_all-lag(cases_all, 14, default = 0),
         deaths_new14 = deaths_all-lag(deaths_all, 14, default = 0),
         cases_new_100k = round(100000*cases_new14/pop, 1),
         deaths_new_100k = round(100000*deaths_new14/pop,1)) %>%
  dplyr::rename("Fälle" = cases_new_100k, "Tote" = deaths_new_100k) %>%
  ungroup() %>%
  filter(date == last(date), pop > 1000000, `Fälle` > 0) %>%
  arrange(desc(`Fälle`)) %>%
  select(Land, `Fälle`, Tote) 

notes <- paste0("Gezeigt werden Länder mit mehr als einer Million Einwohnern.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = 'd04de590ccac9ec5c74ec405ece8ffb1', data = combo_table, notes = notes)



# USA
us <- rolling_average_all %>%
  filter(Land == "USA")  %>%
  ungroup() %>%
  select(date, ravg_cases)

update_chart(id = '6c2576748a77f670cb88f2bb792bcdf3', data = us)



#### Cases ####

# All cases
all_cum <- rolling_average_all %>%
  filter(date == last(all_ctry$date), pop > 1000000) %>%
  group_by(Land, pop, date) %>%
  summarise(all_cases = sum(all_cases),
            dead = sum(dead)) %>%
  mutate(all_cases_pop = round(all_cases/(pop/100000), 1))  %>%
  mutate(dead_pop = round(dead/(pop/100000),1))

all_cum_cases <- all_cum %>%
  arrange(desc(all_cases_pop)) %>%
  ungroup() %>%
  slice(1:20) %>%
  select(Land, all_cases_pop)

title <- paste(head(all_cum_cases$Land, 1), "insgesamt am stärksten betroffen")
notes <- paste0("Länder mit mehr als 1 Million Einwohnern.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(all_ctry$date), format = "%d. %m. %Y")))
update_chart(id = '7c647e0bd14b018f4f4f91aa86eb1872', data = all_cum_cases, notes = notes, title = title)


#Continents

roll_cont <- rolling_average_all %>%
  group_by(date, region_2) %>%
  summarise(cases = sum(ravg_cases)) %>%
  spread(region_2, cases) %>%
  select(date, Europa, Asien, Afrika, Nordamerika, Lateinamerika, Ozeanien) %>%
  filter(date > "2020-01-28")

update_chart(id = 'af5ce13bfad0180d368a3810c9e9eabf', data = roll_cont)
update_chart(id = 'afb382321448e30ea606ea26259b4004', data = roll_cont)


roll_cont <- rolling_average_all %>%
  group_by(date, region_2) %>%
  summarise(cases = sum(ravg_deaths)) %>%
  spread(region_2, cases) %>%
  select(date, Europa, Asien, Afrika, Nordamerika, Lateinamerika, Ozeanien) %>%
  filter(date > "2020-01-28")

update_chart(id = '549b5522072c32f00946aa2ea0db1247', data = roll_cont)



### Table with countries, number of new cases per capita

cases_countries <- rolling_average_all %>%
  filter(pop > 1000000) %>%
  drop_na(ravg_cases_pop) %>%
  arrange(Land, date) %>%
  mutate(pct_of_max = (ravg_cases_pop*100)/max(ravg_cases_pop, na.rm = T)) %>%
  mutate(diff_pct_max = pct_of_max - lag(pct_of_max, 14, default = 0)) %>%
  mutate(Tendenz = case_when
         (diff_pct_max > 5 ~ '\U2191',
           diff_pct_max < -5 ~ '\U2193',
           TRUE ~ '\U2192',)) %>%
  mutate(ravg_cases_pop = round(ravg_cases_pop, 1)) %>%
  filter(date == last(date), ravg_cases_pop > 0) %>%
  select(Land, ravg_cases_pop, Tendenz) %>%
  arrange(desc(ravg_cases_pop)) %>%
  dplyr::rename(`Neue Fälle` = ravg_cases_pop)

notes <- paste0("Berücksichtigt werden Länder mit mehr als 1 Million Einwohnern. Als sinkend bzw. steigend gilt eine Entwicklung, wenn der aktuelle Wert im Vergleich zum Maximalwert des Landes in den letzten 14 Tagen um 5 Prozentpunkte ab- bzw. zugenommen hat. GB = Grossbritannien, VAE = Vereinigte Arabische Emirate. <br>Stand: "
, gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = 'aa6f47afcb5960d3151eefaa3ef6bba7', data = cases_countries, notes = notes)



# Europe

europe <- subset(rolling_average_continents, select = c('Land', 'date', 'ravg_cases_pop'), continent == 'Europe') %>%
  spread(Land, ravg_cases_pop) %>%
  replace(is.na(.), 0)

update_chart(id = '3ff86ba4f375303f8173c2e3f348f6dc', data = europe)


#### Deaths ####

# All deaths
all_cum_deaths <- all_cum %>%
  arrange(desc(dead_pop)) %>%
  ungroup() %>%
  slice(1:20) %>%
  select(Land, dead_pop)

title <- paste(head(all_cum_deaths$Land, 1), "hat gemessen an der Bevölkerungszahl am meisten Tote zu beklagen")

notes <- paste0("Länder mit mehr als 1 Million Einwohnern. <br>Stand: "
                , gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = 'c7004f4d1b11f50ecbbd2d4a1849f329', data = all_cum_deaths, notes = notes, title = title)



all_cum_world <- rolling_average_all %>%
  filter(date == last(all_ctry$date)) %>%
  group_by(date) %>%
  summarise(all_cases = sum(all_cases),
            dead = sum(dead)) %>%
  mutate(variable = round(dead, 0)) %>%
  select(variable)

all_cum_world$col <- 'Offizielle Todesfälle'

economist <- read_csv('https://raw.githubusercontent.com/TheEconomist/covid-19-the-economist-global-excess-deaths-model/main/output-data/output-for-interactive/world_line_chart_cumulative.csv')

economist <- economist %>% filter(date == last(date)) %>%
  mutate(variable = round(estimate, 0)) %>%
  select(variable)

economist$col <- 'Schätzung des «Economist»'

q <- rbind(all_cum_world, economist) %>% select(col, variable)
  
notes <- paste0("Die Schätzung der Todesfälle beinhaltet einen Unsicherheitsbereich, der nicht angezeigt wird.<br>Stand: ", gsub("\\b0(\\d)\\b", "\\1", format(max(all_ctry$date), format = "%d. %m. %Y")))
update_chart('3634bbb802cb1a3fb644a38fbe0c9579', data = q, notes = notes)



# Table with countries, number of new deaths per capita
deaths_countries <- rolling_average_all %>%
  filter(pop > 1000000) %>%
  drop_na(ravg_deaths_pop) %>%
  arrange(Land, date) %>%
  mutate(pct_of_max = (ravg_deaths_pop*100)/max(ravg_deaths_pop, na.rm = T)) %>%
  mutate(diff_pct_max = pct_of_max - lag(pct_of_max, 14, default = 0)) %>%
  mutate(Tendenz = case_when
         (diff_pct_max > 5 ~ '\U2191',
           diff_pct_max < -5 ~ '\U2193',
           TRUE ~ '\U2192',)) %>%
  mutate(ravg_deaths_pop = round(ravg_deaths_pop, 1)) %>%
  filter(date == last(date), ravg_deaths_pop > 0) %>%
  select(Land, ravg_deaths_pop, Tendenz) %>%
  arrange(desc(ravg_deaths_pop)) %>%
  dplyr::rename(`Neue Todesfälle` = ravg_deaths_pop) 


notes <- paste0("Berücksichtigt werden Länder mit mehr als 1 Million Einwohnern. Als sinkend bzw. steigend gilt eine Entwicklung, wenn der aktuelle Wert im Vergleich zum Maximalwert des Landes in den letzten 14 Tagen um 5 Prozentpunkte ab- bzw. zugenommen hat. GB = Grossbritannien, VAE = Vereinigte Arabische Emirate. <br>Stand: "
                , gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = '12c077ec9e34e0a0817527a6a302143b', data = deaths_countries, notes = notes)




#### Update the following graph for 'Wirtschaft in Echtzeit' ####

dach_dead <- rolling_average_all %>%
  select (date, Land, dead, pop) %>%
  filter ((Land == 'Österreich' | Land == 'Deutschland' | Land == 'Schweiz'), date >= '2020-03-01' ) %>%
  mutate(dead = dead/(pop/100000)) %>%
  select(Land, date, dead) %>%
  spread(Land, dead)

col_order <- c('date', 'Deutschland', 'Österreich', 'Schweiz')
dach_dead <- dach_dead[, col_order]

update_chart(id = 'c3363717f697b849984f891eeca1db45', data = dach_dead)




# vaccination speed
vaccination_speed <- vaccination %>%
  drop_na(Land) %>%
  drop_na(`Täglich verabreichte Impfdosen, pro 1000 Einw.`) %>%
  group_by(Land) %>%
  arrange(Datum) %>%
  mutate(ravg = rollmean(`Täglich verabreichte Impfdosen, pro 1000 Einw.`, 7, fill = 0, align = "right")) %>%
  mutate(Datum = as.Date(Datum, "%d.%m.%Y")) %>%
  filter(Land != 'World', pop > 1000000)  %>%
  slice_max(order_by = Datum, n = 1) %>%
  arrange(desc(`Täglich verabreichte Impfdosen, pro 1000 Einw.`)) %>%
  select(Land, `Täglich verabreichte Impfdosen, pro 1000 Einw.`) %>%
  mutate(`Täglich verabreichte Impfdosen, pro 1000 Einw.` = round(`Täglich verabreichte Impfdosen, pro 1000 Einw.` / 1000, 1)) %>%
  ungroup()

vacc_table <- full_join(vacc, full_vacc, by = "Land") %>%
  full_join(vaccination_speed, by = "Land") %>%
  arrange(desc(`Täglich verabreichte Impfdosen, pro 1000 Einw.`)) %>%
  drop_na() %>%
  filter(`Doppelt geimpft, in % der Bev.` > 1)

vacc_table$Land <- recode(vacc_table$Land, '"Griechenland"="GR"')
vacc_table$Land <- recode(vacc_table$Land, '"Niederlande"="NL"')
vacc_table$Land <- recode(vacc_table$Land, '"Grossbritannien"="GB"')

notes <- paste0("Nur Länder mit mehr als 1 Million Einwohnern, in denen bereits mehr als 1 Prozent der Bevölkerung doppelt geimpft ist. Für die täglich verabreichten Impfdosen weisen wir den 7-Tage-Schnitt aus. Aufgrund unterschiedlicher Meldeverfahren können für einige Länder die Daten schon mehrere Tage alt sein. GB = Grossbritannien,  GR = Griechenland, NL = Niederlande, VAE = Vereinigte Arabische Emirate. <br>Stand: "
                , gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = '6e4d9b2212af59f507ce3da0b9537963', data = vacc_table, notes = notes)




# Which manufacturer?
manufacturer <- read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv")

colnames(manufacturer) <- c("Land", "Datum", "Hersteller", "Anzahl_Impfdosen")

# filter out 'European Union'
manufacturer <- manufacturer %>%
  filter(Land != 'European Union')

manufacturer$Land <- countrycode(manufacturer$Land, 'country.name', 'country.name.de')

manufacturer$Land <- recode(manufacturer$Land, '"Vereinigte Staaten"="USA"')
manufacturer$Land <- recode(manufacturer$Land, '"Tschechische Republik"="Tschechien"')

manufacturer <- merge(manufacturer, un, by = "Land", all.x = TRUE)

manufacturer$Land <- recode(manufacturer$Land, '"Vereinigte Arabische Emirate"="VAE"')
manufacturer$Land <- recode(manufacturer$Land, '"Saudi-Arabien"="Saudiarabien"')
manufacturer$Land <- recode(manufacturer$Land, '"Bosnien und Herzegowina" = "Bosnien-Herz."')
manufacturer$Land <- recode(manufacturer$Land, '"Nordmazedonien" = "Nordmazed."')
manufacturer$Land <- recode(manufacturer$Land, '"Republik Moldau" = "Moldau"')
manufacturer$Land <- recode(manufacturer$Land, '"Trinidad und Tobago" = "Trinidad u. T."')
manufacturer$Land <- recode(manufacturer$Land, '"Dominikanische Republik" = "Dominikan. Rep."')
manufacturer$Land <- recode(manufacturer$Land, '"Bangladesch" = "Bangladesh"')
manufacturer$Land <- recode(manufacturer$Land, '"Zimbabwe" = "Simbabwe"')
manufacturer$Land <- recode(manufacturer$Land, '"Kirgisistan" = "Kirgistan"')


hersteller <- manufacturer %>%
  filter(pop > 1000000) %>%
  group_by(Land, Hersteller) %>%
  summarize(Anzahl_Impfdosen = sum(Anzahl_Impfdosen)) %>%
  ungroup() %>%
  spread(Hersteller, Anzahl_Impfdosen) %>%
  mutate_all(~replace(., is.na(.), 0)) %>%
  mutate(Summe = Moderna + `Oxford/AstraZeneca` + `Pfizer/BioNTech` + `Johnson&Johnson` + Sinovac + `Sinopharm/Beijing` + `CanSino` + `Sputnik V`) %>%
  mutate(Moderna = Moderna/Summe*100,
         `Oxford/AstraZeneca` = `Oxford/AstraZeneca`/Summe*100,
         `Pfizer/BioNTech` = `Pfizer/BioNTech`/Summe*100,
         Sinovac = Sinovac/Summe*100,
         `Sinopharm/Beijing` = `Sinopharm/Beijing`/Summe*100,
         `Johnson&Johnson` = `Johnson&Johnson`/Summe*100,
         `CanSino` = `CanSino`/Summe*100,
         `Sputnik V` = `Sputnik V`/Summe*100) %>%
  dplyr::rename(
    "AstraZeneca" = "Oxford/AstraZeneca",
    "Biontech/Pfizer" = "Pfizer/BioNTech",
    "Johnson & Johnson" = "Johnson&Johnson"
    )

hersteller <- hersteller %>%
  select(-Summe)  %>%
  relocate(Land, `Biontech/Pfizer`, AstraZeneca, Moderna, `Johnson & Johnson`, CanSino, `Sinopharm/Beijing`, Sinovac)

notes <- paste0("Daten sind nur für eine begrenzte Zahl Länder verfügbar. Nur Länder mit mehr als 1 Million Einwohner. <br>Stand: "
                , gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = '20a5c20ca1e9e69ecfd6cb5a8684ca89', data = hersteller, notes = notes)



#### new cases - different world regions ####

# America

america <- subset(rolling_average_continents, select = c('Land', 'date', 'ravg_cases_pop'), continent == 'Americas') %>%
  spread(Land, ravg_cases_pop) %>%
  replace(is.na(.), 0)

update_chart(id = '51b77940546ab3f720aeaa28116b4eb6', data = america)

# Asia

asia <- subset(rolling_average_continents, select = c('Land', 'date', 'ravg_cases_pop'), continent == 'Asia') %>%
  spread(Land, ravg_cases_pop) %>%
  replace(is.na(.), 0)

update_chart(id = 'd6e523e17e1d929e6277292aea017e6e', data = asia)



#### Testing ####

tests <- read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-latest-data-source-details.csv') %>%
  separate(col = Entity, into = c("Country", "Entity"), sep = " - ") %>%
  select("Country", "Entity", "Date", "7-day smoothed daily change per thousand", "Short-term positive rate", "Short-term tests per case")

tests$Land <- countrycode(tests$Country, 'country.name', 'cldr.short.de_ch')

tests <- merge(tests, un, by = "Land", all.x = TRUE)

tests$Land <- recode(tests$Land, '"Vereinigte Arabische Emirate"="VAE"')
tests$Land <- recode(tests$Land, '"Saudi-Arabien"="Saudiarabien"')
tests$Land <- recode(tests$Land, '"Bosnien und Herzegowina" = "Bosnien-Herz."')
tests$Land <- recode(tests$Land, '"Nordmazedonien" = "Nordmazed."')
tests$Land <- recode(tests$Land, '"Republik Moldau" = "Moldau"')
tests$Land <- recode(tests$Land, '"Trinidad und Tobago" = "Trinidad u. T."')
tests$Land <- recode(tests$Land, '"Dominikanische Republik" = "Dominikan. Rep."')
tests$Land <- recode(tests$Land, '"Bangladesch" = "Bangladesh"')
tests$Land <- recode(tests$Land, '"Zimbabwe" = "Simbabwe"')
tests$Land <- recode(tests$Land, '"Kirgisistan" = "Kirgistan"')

tests$Entity <- factor(tests$Entity, levels = c("tests performed", "people tested", "people tested (incl. non-PCR)", 'units unclear', 'units unclear (incl. non-PCR)',
                                                'samples tested'))

test_table <- tests %>%
  drop_na(Land) %>%
  drop_na(`7-day smoothed daily change per thousand`) %>%
  arrange(Land, desc(Date), Entity) %>%
  distinct(Land, .keep_all = TRUE) %>%
  group_by(Land) %>%
  mutate(Datum = as.Date(Date, "%d.%m.%Y")) %>%
  filter(pop > 1000000) %>%
  slice_max(order_by = Datum, n = 1) %>%
  select("Land",  "7-day smoothed daily change per thousand", "Short-term positive rate") %>%
  dplyr::rename(
    "Tests pro 1000 Einwohner" = "7-day smoothed daily change per thousand",
    "Anteil positiver Tests (in %)" = "Short-term positive rate"
  ) %>%
  arrange(desc(`Tests pro 1000 Einwohner`)) %>%
  mutate(`Tests pro 1000 Einwohner` = round(`Tests pro 1000 Einwohner`, 1), `Anteil positiver Tests (in %)` = round(`Anteil positiver Tests (in %)`*100, 1)) %>%
  filter(`Tests pro 1000 Einwohner` > 1) %>%
  ungroup()

title <- paste(head(test_table$Land, 1), "testet am meisten")

notes <- paste0("Nur Länder mit mehr als 1 Million Einwohnern, die mehr als einen Test pro 1000 Einwohner pro Tag durchführen. Aufgrund unterschiedlicher Meldeverfahren können die Daten für einige Länder schon mehrere Tage alt sein. GB = Grossbritannien, VAE = Vereinigte Arabische Emirate.<br>Stand: "
                , gsub("\\b0(\\d)\\b", "\\1", format(max(rolling_average_all$date), format = "%d. %m. %Y")))
update_chart(id = 'fdf83ddd0451dc0c0d09c18769f1abd5', data = test_table, notes = notes, title = title)

