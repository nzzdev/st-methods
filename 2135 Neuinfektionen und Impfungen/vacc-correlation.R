#### Vergleich Neuinfektionen und Impffortschritt in den Schweizer Kantonen #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(ggrepel)

#### Create standard plot: new covid infections over past 14 days per 100k vs. share fully vaccinated people ####

### read-in

bag_data <- fromJSON('https://www.covid19.admin.ch/api/data/context')

bag_cases <- subset(read_csv(bag_data$sources$individual$csv$daily$cases), select = c("geoRegion", "datum", "entries", "sumTotal", "pop")) %>%
  filter(datum <= as.Date("2021-09-22")) #filter data that arrived after publication
names(bag_cases) <- c('geoRegion', 'datum', 'Fälle', 'Fälle kumuliert', 'pop')

bag_hosps <- subset(read_csv(bag_data$sources$individual$csv$daily$hosp), select = c("geoRegion", "datum", "entries", "sumTotal", "pop")) %>%
  filter(datum <= as.Date("2021-09-22"))
names(bag_hosps) <- c('geoRegion', 'datum', 'Fälle', 'Fälle kumuliert', 'pop')

bag_testPcrAntigen <- read_csv(bag_data$sources$individual$csv$daily$testPcrAntigen) %>% 
  select("geoRegion", "datum", "entries", "entries_pos", "entries_neg", "nachweismethode", "pos_anteil") %>%
  filter(datum <= as.Date("2021-09-22"))

bag_tests <- subset(read_csv(bag_data$sources$individual$csv$daily$test), select = c("geoRegion", "datum", "entries", "pos_anteil", "sumTotal", "pop")) %>%
  filter(datum <= as.Date("2021-09-22"))
names(bag_tests) <- c('geoRegion', 'datum', 'Tests', 'pos_anteil', 'Tests kumuliert', "pop")

ch_vacc_del <- read_csv(bag_data$sources$individual$csv$vaccDosesDelivered) %>% 
  filter(type == "COVID19VaccDosesDelivered") %>%
  filter(date <= as.Date("2021-09-22")) %>%
  select(geoRegion, date,pop, sumTotal) %>%
  drop_na()

ch_vacc_adm <- read_csv(bag_data$sources$individual$csv$vaccDosesAdministered) %>% 
  select(geoRegion, date, sumTotal, per100PersonsTotal) %>%
  filter(date <= as.Date("2021-09-22")) %>%
  drop_na()

ch_vacc_full <-read_csv(bag_data$sources$individual$csv$vaccPersons) %>%
  filter(type == "COVID19FullyVaccPersons") %>%
  filter(date <= as.Date("2021-09-22")) %>%
  select(geoRegion, date, sumTotal) %>%
  drop_na()

#data prep
bag_kanton_choro <- bag_cases %>%
  filter(!is.na(datum), datum >= last(datum)-13, geoRegion != "CHFL", geoRegion != "CH", geoRegion != "FL") %>%
  group_by(geoRegion, pop) %>%
  summarise(sum = sum(`Fälle`)) %>%
  mutate(per100k = round(100000*sum/pop, 0)) %>%
  arrange(geoRegion) %>%
  select(geoRegion, per100k)

ch_vacc <- ch_vacc_adm %>%
  full_join(ch_vacc_del, by = c("geoRegion", "date")) %>%
  full_join(ch_vacc_full, by = c("geoRegion", "date")) %>%
  select(geoRegion, date, pop, sumTotal.y, sumTotal.x, sumTotal, per100PersonsTotal)%>%
  rename(geounit = geoRegion, 
         ncumul_delivered_doses = sumTotal.y, 
         ncumul_vacc_doses = sumTotal.x, 
         ncumul_fully_vacc = sumTotal) %>%
  group_by(geounit) %>%
  mutate(new_vacc_doses = ncumul_vacc_doses-lag(ncumul_vacc_doses))%>%
  mutate(ncumul_firstdoses_vacc = ncumul_vacc_doses - ncumul_fully_vacc) %>%
  mutate(ncumul_onlyfirstdoses_vacc = ncumul_firstdoses_vacc - ncumul_fully_vacc) %>%
  fill(pop, ncumul_delivered_doses) %>%
  ungroup()


vacc_ch_2nd <- ch_vacc %>%
  select(geounit, date, pop, ncumul_fully_vacc, ncumul_onlyfirstdoses_vacc) %>%
  drop_na(ncumul_fully_vacc) %>%
  filter(geounit != "CH" & geounit != "FL" & geounit != "CHFL" & date == max(date)-13) %>%
  mutate(first_pct = ncumul_onlyfirstdoses_vacc*100/pop,
         second_pct = ncumul_fully_vacc*100/pop) %>%
  select(geounit, second_pct, pop) %>%
  slice(1:26)


### combine and plot case and vaccination data
combined <- full_join(vacc_ch_2nd, bag_kanton_choro, by = c("geounit" = "geoRegion"))

#plot
ggplot(data = combined, mapping = aes(x = second_pct, y = per100k, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + 
  xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  geom_point(aes(size = pop, alpha = 0.5)) +
  scale_size(range = c(1, 15)) +
  theme_minimal() +
  geom_smooth(method=lm, se = F, linetype = "dashed", color = "darkblue")

#loess trendline
ggplot(data = combined, mapping = aes(x = second_pct, y = per100k, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  scale_color_discrete(name="") +
  geom_point() +
  theme_bw() +
  geom_smooth(method=loess)


### Check correlation and significance
cor(combined$per100k, combined$second_pct)^2 %>% round(2)
lm(combined$per100k ~ combined$second_pct) %>% summary()

#### robustness checks ####

### cases from previous 4 weeks instead of 2

bag_kanton_choro_4w <- bag_cases %>%
  filter(!is.na(datum), datum >= last(datum)-27, geoRegion != "CHFL", geoRegion != "CH", geoRegion != "FL") %>%
  group_by(geoRegion, pop) %>%
  summarise(sum = sum(`Fälle`)) %>%
  mutate(per100k = round(100000*sum/pop, 0)) %>%
  arrange(geoRegion) %>%
  select(geoRegion, per100k, pop)

vacc_ch_2nd_4w <- ch_vacc %>%
  select(geounit, date, pop, ncumul_fully_vacc, ncumul_onlyfirstdoses_vacc) %>%
  drop_na(ncumul_fully_vacc) %>%
  filter(geounit != "CH" & geounit != "FL" & geounit != "CHFL" & date == max(date)-27) %>%
  mutate(first_pct = ncumul_onlyfirstdoses_vacc*100/pop,
         second_pct = ncumul_fully_vacc*100/pop) %>%
  select(geounit, second_pct) %>%
  slice(1:26)


#combine and plot case and vaccination data
combined_4w <- full_join(vacc_ch_2nd_4w, bag_kanton_choro_4w, by = c("geounit" = "geoRegion")) 

#plot
ggplot(data = combined_4w, mapping = aes(x = second_pct, y = per100k, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + 
  xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  geom_point(aes(size = pop, alpha = 0.5)) +
  scale_size(range = c(1, 15)) +
  theme_minimal() +
  geom_smooth(method=lm, se = F, linetype = "dashed", color = "darkblue")

#loess trendline
ggplot(data = combined_4w, mapping = aes(x = second_pct, y = per100k, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  scale_color_discrete(name="") +
  geom_point() +
  theme_bw() +
  geom_smooth(method=loess)

# Check correlation and significance
cor(combined_4w$per100k, combined_4w$second_pct)^2 %>% round(2)
lm(combined_4w$per100k ~ combined_4w$second_pct) %>% summary()


### 6 weeks
bag_kanton_choro_6w <- bag_cases %>%
  filter(!is.na(datum), datum >= last(datum)-41, geoRegion != "CHFL", geoRegion != "CH", geoRegion != "FL") %>%
  group_by(geoRegion, pop) %>%
  summarise(sum = sum(`Fälle`)) %>%
  mutate(per100k = round(100000*sum/pop, 0)) %>%
  arrange(geoRegion) %>%
  select(geoRegion, per100k, pop)

vacc_ch_2nd_6w <- ch_vacc %>%
  select(geounit, date, pop, ncumul_fully_vacc, ncumul_onlyfirstdoses_vacc) %>%
  drop_na(ncumul_fully_vacc) %>%
  filter(geounit != "CH" & geounit != "FL" & geounit != "CHFL" & date == max(date)-41) %>%
  mutate(first_pct = ncumul_onlyfirstdoses_vacc*100/pop,
         second_pct = ncumul_fully_vacc*100/pop) %>%
  select(geounit, second_pct) %>%
  slice(1:26)


# combine and plot case and vaccination data
combined_6w <- full_join(vacc_ch_2nd_6w, bag_kanton_choro_6w, by = c("geounit" = "geoRegion"))
#plot
ggplot(data = combined_6w, mapping = aes(x = second_pct, y = per100k, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + 
  xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  geom_point(aes(size = pop, alpha = 0.5)) +
  scale_size(range = c(1, 15)) +
  theme_minimal() +
  geom_smooth(method=lm, se = F, linetype = "dashed", color = "darkblue")

#loess trendline
ggplot(data = combined_6w, mapping = aes(x = second_pct, y = per100k, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  scale_color_discrete(name="") +
  geom_point() +
  theme_bw() +
  geom_smooth(method=loess)

### Check correlation and significance
cor(combined_6w$per100k, combined_6w$second_pct)^2 %>% round(2)
lm(combined_6w$per100k ~ combined_6w$second_pct) %>% summary()


# Testpositivität

bag_kanton_choro_tpr <- bag_testPcrAntigen %>%
  filter(!is.na(datum), datum >= last(datum)-13, geoRegion != "CHFL", geoRegion != "CH", geoRegion != "FL") %>%
  group_by(geoRegion) %>%
  summarise(entries_pos = sum(entries_pos),
            entries = sum(entries),
            pr = entries_pos*100/entries) %>%
  select(geoRegion, pr)


combined_tpr <- full_join(vacc_ch_2nd, bag_kanton_choro_tpr, by = c("geounit" = "geoRegion"))

#plot
ggplot(data = combined_tpr, mapping = aes(x = second_pct, y = pr, label=geounit)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen (Inzidenz)") + 
  xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent") +
  geom_point(aes(size = pop, alpha = 0.5)) +
  scale_size(range = c(1, 15)) +
  theme_minimal() +
  geom_smooth(method=lm, se = F, linetype = "dashed", color = "darkblue")


### Tests pro Kopf in den Kantonen


bag_tests_kanton <- bag_tests %>% 
  filter(datum > "2020-01-31", geoRegion != 'CH' & geoRegion != 'CHFL' & geoRegion != 'FL') %>%
  mutate(Tests_7 = rollmean(Tests, 14, fill = 0, align = "right"), 
         pos_anteil_7 = round(rollmean(pos_anteil, 14, na.pad = TRUE, align = "right"), 1),
         Tests_pro_Kopf = round(Tests_7*1000/pop, 1))

tests_kopf <- bag_tests_kanton %>%
  mutate(Tests_pro_Kopf = Tests_pro_Kopf*100) %>%
  filter(datum == last(datum)-1) %>%
  select(geoRegion, Tests_pro_Kopf) %>%
  arrange(geoRegion) %>%
  drop_na()  

### Scatterplot: Tests pro Kopf in den Kantonen und Inzidenz

combined_inz_tests <- full_join(tests_kopf, bag_kanton_choro, by = c("geoRegion" = "geoRegion"))

ggplot(data = combined_inz_tests, mapping = aes(x = Tests_pro_Kopf, y = per100k, label=geoRegion)) +
  geom_text_repel() +
  ylab("Fälle pro 100 000 Einwohner in den letzten zwei Wochen") + xlab("Coronavirus-Tests pro 100 000 Einwohner, 14-Tage-Durchschnitt") +
  scale_color_discrete(name="") +
  geom_point() +
  theme_bw() +
  geom_smooth(method=lm)


#### ZH Corr ####
zh_cases_plz <- read_csv("https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_plz/fallzahlen_kanton_ZH_plz.csv") %>%
  filter(Date <= as.Date("2021-09-22")) %>%
  filter(Date %in% c(max(Date), max(Date)-7)) %>%
  separate(NewConfCases_7days,c("low", "high"), "-") %>%
  mutate(mid = (as.numeric(low)+as.numeric(high))/2) %>%
  group_by(PLZ) %>%
  summarise(Population = first(Population), sum = sum(mid)) %>%
  mutate(per1k = 1000*(sum/Population))

zh_vacc_plz <- read_csv("https://raw.githubusercontent.com/openZH/covid_19_vaccination_campaign_ZH/master/COVID19_Impfungen_pro_Woche_PLZ.csv") %>%
  filter(week_until == max(week_until)-14) %>%
  mutate(pct_2nd = ncumul_secondvacc*100/population)

zh_corr <- inner_join(zh_vacc_plz, zh_cases_plz, by = c("plz" = "PLZ")) %>% filter(plz != "unbekannt")

ggplot(data = zh_corr, mapping = aes(x = pct_2nd, y = per1k, label = plz)) +
  geom_point(aes(size = population), alpha = 0.3) +
  scale_size(range = c(1, 5)) +
  theme_minimal() +
  geom_smooth(method=lm, se = F, linetype = "dashed", color = "darkblue") +
  ylab("Fälle pro 1000 Einwohner in den letzten zwei Wochen (Inzidenz)") + 
  xlab("Anteil der vollständig geimpften Personen vor zwei Wochen, in Prozent")

cor(zh_corr$pct_2nd, zh_corr$per1k)^2 %>% round(2)
lm(zh_corr$pct_2nd ~ zh_corr$per1k) %>% summary()
