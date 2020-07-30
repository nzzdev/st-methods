##### Script for municilal BAG data #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999, stringsAsFactors = F)
library(tidyverse)
library(BAMMtools)
library(readxl)

setwd("~/Downloads/bag-script") #adjust this to your WD

#data read-in
bag_data_raw <- readRDS("ncov2019_falldetail_nzz_gmde_sim.rds") %>%
  group_by(fall_dt, gemeinde_cd) %>% # this is just for the test data which has date*district doubles
  summarise(n = sum(n)) %>% # which are summarised per day and district
  as.tibble()

bfs_table_2019 <- read_delim("g1g19.csv", delim = ";") %>% select(GMDNR, GMDNAME)
bfs_hist <- read_tsv("20200101_GDEHist_GDE.txt", 
                     col_names = FALSE, 
                     locale = locale(encoding = "latin1"))

#### DATA FORMATTING ####
# this formats the data so there is a cumulative and a 14-day-new cases value for every day and municipality

# there is not a case every day, so all the dates are compared to the calendar
# missing days are added with dummy district 9999

bag_days <-as.vector(unique(bag_data_raw$fall_dt))
cal_days <- as.character(seq(as.Date(first(bag_days)), as.Date(last(bag_days)), by="days"))
dummy_days <- tibble(setdiff(cal_days, bag_days)) %>% 
  add_column(gemeinde_cd = as.factor(9999) , n = NA) %>%
  rename(fall_dt = `setdiff(cal_days, bag_days)`) %>%
  as.tibble()

bag_data_alldates <- rbind(bag_data_raw, dummy_days)

n_gem <- length(unique(bag_data_alldates$gemeinde_cd)) #get number of distinct disticts

#dataset with cumulated and 14-day-new cases is created here
bag_data_formatted <- bag_data_alldates %>%     
  group_by(gemeinde_cd) %>%
  arrange(gemeinde_cd, fall_dt) %>%
  mutate(cum = cumsum(n)) %>% #get cumulative numbers
  select(-n) %>%
  spread(gemeinde_cd, cum) %>% #spread...
  fill(2:(n_gem+1)) %>% #to fill up NAs, resulting in a complete dataset
  gather(gemeinde, cum, 2:(n_gem+1)) %>%
  group_by(gemeinde) %>%
  mutate(cum = replace_na(cum, 0)) %>% 
  mutate(roll = cum-lag(cum,14, default = 0)) %>% # new cases in the last 14 days
  ungroup() %>%
  mutate(gemeinde = as.numeric(gemeinde))

#check for gemeinden not in the bfs set
missing <- setdiff(unique(bag_data_formatted$gemeinde), unique(bfs_table_2019$GMDNR)) %>%
  as.numeric() #these are in the bag dataset but have no 2019 bfs nr

missing <- missing[missing < 7000] #exclude dummy, liechtenstein and campione d'italia

missing_dataset <- bfs_hist %>% #pulling info on missings from hist.gemeindeverzeichnis
  filter(X4 %in% missing) %>%
  select(X3:X5,X15) %>% 
  arrange(X4)

missing_dataset
#WILL THIS BE CLEARED UP? IF NOT: NEEDS FIX, PROB ANOTHER GROUP BY - SUMMARISE

#merge bag dataset with bfs 2019 geodata table
data_merged <- bag_data_formatted %>% 
  full_join(bfs_table_2019, by = c("gemeinde" = "GMDNR")) 

#get all the districts without any cases and create rows with zeroes for every day/distict
data_zeroes <- data_merged %>% 
  filter(is.na(fall_dt)) %>% 
  expand(cal_days,gemeinde) %>%
  add_column(cum = 0, roll = 0, GMDNAME = NA) %>%
  rename(fall_dt = cal_days)

#reassign district names
data_compl <- rbind(data_merged, data_zeroes) %>%
  select(-GMDNAME) %>%
  full_join(bfs_table_2019, by = c("gemeinde" = "GMDNR")) %>%
  filter(!is.na(fall_dt))

#merge with population data

data_pop <- read_excel("je-d-21.03.01(2).xlsx",2) #subset (select cols) this if necessary

data_all <- data_compl %>% full_join(data_pop, by = c("gemeinde" = "Gemeindecode"))

#calculate cases per 1000 inhabitants
data_all$cumper1k <- (1000*data_all$cum)/data_all$Einwohner
data_all$rollper1k <- (1000*data_all$roll)/data_all$Einwohner

#some subsetting (most recent day) to get the basis for jenks
data_aktuell <- data_all %>% 
  select(fall_dt, gemeinde, GMDNAME, cum, roll, cumper1k,rollper1k) %>% 
  filter(fall_dt == last(as.character(fall_dt)))

last(as.character(data_all$fall_dt)) #most recent day

# getting jenks breaks that departamentalise the data into groups so that different levels are reflected
# more on the method here: https://en.wikipedia.org/wiki/Jenks_natural_breaks_optimization

cumjenks <- getJenksBreaks(data_aktuell$cumper1k,7) %>% round(2)
rolljenks <- getJenksBreaks(data_all$rollper1k,7) %>% round(2) #takes a few minutes, calculates 250k values

#get strings for category names
ranges_cum <- c(paste0(0.01,"-",cumjenks[2]),
                paste0(cumjenks[2],"-",cumjenks[3]),
                paste0(cumjenks[3],"-",cumjenks[4]),
                paste0(cumjenks[4],"-",cumjenks[5]),
                paste0(cumjenks[5],"-",cumjenks[6]),
                paste0(cumjenks[6],"-",cumjenks[7]))

ranges_roll <- c(paste0(0.01,"-",rolljenks[2]),
                 paste0(rolljenks[2],"-",rolljenks[3]),
                 paste0(rolljenks[3],"-",rolljenks[4]),
                 paste0(rolljenks[4],"-",rolljenks[5]),
                 paste0(rolljenks[5],"-",rolljenks[6]),
                 paste0(rolljenks[6],"-",rolljenks[7]))

#creating the publishable dataset: categories are assigned for each day, all precise data is removed
data_publish <- data_all %>%
  mutate(kat_cum = case_when(cumper1k == 0 ~ "0", 
                             cumper1k > cumjenks[1]  & cumper1k <= cumjenks[2] ~ ranges_cum[1],
                             cumper1k > cumjenks[2]  & cumper1k <= cumjenks[3] ~ ranges_cum[2],
                             cumper1k > cumjenks[3]  & cumper1k <= cumjenks[4] ~ ranges_cum[3],
                             cumper1k > cumjenks[4]  & cumper1k <= cumjenks[5] ~ ranges_cum[4],
                             cumper1k > cumjenks[5]  & cumper1k <= cumjenks[6] ~ ranges_cum[5],
                             cumper1k > cumjenks[6]  & cumper1k <= cumjenks[7] ~ ranges_cum[6])) %>%
  mutate(kat_roll = case_when(rollper1k == 0 ~ "0", 
                              rollper1k > rolljenks[1]  & rollper1k <= rolljenks[2] ~ ranges_roll[1],
                              rollper1k > rolljenks[2]  & rollper1k <= rolljenks[3] ~ ranges_roll[2],
                              rollper1k > rolljenks[3]  & rollper1k <= rolljenks[4] ~ ranges_roll[3],
                              rollper1k > rolljenks[4]  & rollper1k <= rolljenks[5] ~ ranges_roll[4],
                              rollper1k > rolljenks[5]  & rollper1k <= rolljenks[6] ~ ranges_roll[5],
                              rollper1k > rolljenks[6]  & rollper1k <= rolljenks[7] ~ ranges_roll[6])) %>% 
  mutate(kat_cum_fix = case_when(cumper1k == 0 ~ "0",
                                 cumper1k > 0 & cumper1k <= 0.5 ~ "0.001-0.5",
                                 cumper1k > 0.5 & cumper1k <= 1 ~ "0.5-1",
                                 cumper1k > 1 & cumper1k <= 5 ~ "1-5",
                                 cumper1k > 5 & cumper1k <= 10 ~ "5-10",
                                 cumper1k > 10 & cumper1k <= 50 ~ "10-50",
                                 cumper1k > 50 & cumper1k <= 100 ~ "50-100",
                                 cumper1k > 100  ~ "+100")) %>%
  mutate(kat_roll_fix = case_when(rollper1k == 0 ~ "0",
                                 rollper1k > 0 & rollper1k <= 0.5 ~ "0.001-0.5",
                                 rollper1k > 0.5 & rollper1k <= 1 ~ "0.5-1",
                                 rollper1k > 1 & rollper1k <= 5 ~ "1-5",
                                 rollper1k > 5 & rollper1k <= 10 ~ "5-10",
                                 rollper1k > 10 & rollper1k <= 50 ~ "10-50",
                                 rollper1k > 50 & rollper1k <= 100 ~ "50-100",
                                 rollper1k > 100  ~ "+100")) %>%
  select(fall_dt, gemeinde, Gemeindename, kat_cum, kat_roll, kat_cum_fix, kat_roll_fix)

head(data_publish)
#there sould be enough cases in every category

#cumulative
table(data_publish$kat_cum) #heavy concentration in lower categories
table(data_publish$kat_cum_fix) # better, 0.5 break not really necessary but reliant on the real data

#rolling
table(data_publish$kat_roll_fix) 
table(data_publish$kat_roll) #barely any cases in higher categories, better take fixed breaks

#check and send this back 
write_csv(data_publish, "publishable_data.csv")

