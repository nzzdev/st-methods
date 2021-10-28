#### Corona-Script INTERNATIONAL (automated version) #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(zoo)
library(countrycode)


setwd("~/Documents/GitHub/st-methods/bots/corona-charts") #delete later

# import helper functions
#source("./helpers.R")

#read-in
# get data from JHU
cases <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
dead <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

# get population figures (2019)
wdi <- read_csv("wdi.csv") %>%
  add_row(country = "Taiwan", Land = "Taiwan", pop = 23570000)

wdi$Region <- wdi$region

cases$Land[cases$Region == "Macau"] <- "Macau"
cases$Land[cases$Region == "Hongkong"] <- "Hongkong"
dead$Land[dead$Region == "Macau"] <- "Macau"
dead$Land[dead$Region == "Hongkong"] <- "Hongkong"

#to long, get total per date and place
cases_crty <- cases %>% 
  gather(date, value, 5:(ncol(cases)-2)) %>% 
  group_by(date, Land) %>% 
  summarise(first(`Country/Region`), cases = sum(value, na.rm = T))

dead_ctry <- dead %>% 
  gather(date, value, 5:(ncol(dead)-2)) %>% 
  group_by(date, Land) %>%
  summarise(first(`Country/Region`), dead = sum(value, na.rm = T))




