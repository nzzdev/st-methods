#UK Polls

#prep
rm(list=ls(all=TRUE))
options(scipen=999)
library(tidyverse)
library(rvest)

# comment out for editing
# setwd("~/Documents/GitHub/st-methods/bots/polls")
# install.packages("renv")
# renv::init()
# renv::snapshot()
# renv::restore()

# import helper functions
source("./helpers.R")

#read-in
url <- read_html("https://datawrapper.dwcdn.net/Jvco9/") %>%
  as.character() %>%
  str_extract_all("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+") %>%
  unlist()

#mutating
labcon <- read.csv(paste0(url[3],"dataset.csv")) %>%
  select(Date, Con, Lab) %>%
  filter(Date <= Sys.Date()) %>%
  rename(Datum = Date, Labour = Lab, Konservative = Con)

#send to q-cli
update_chart(id = "45462491574f55ca247d51fd58dbceaf", 
             data = labcon)