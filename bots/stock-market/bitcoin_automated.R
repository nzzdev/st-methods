### Bitcoin charts ###

rm(list = ls(all = TRUE))
options(scipen = 999)
library(coindeskr)
library(lubridate)
library(tidyverse)
library(readr)
library(rvest)
library(stringr)
library(coinmarketcapr)


# import helper functions
source("./helpers.R")

date <- Sys.Date()
teny_back <- ymd(date) - years(10)
oney_back <- ymd(date) - years(1)
onem_back <- ymd(date) - months(1)

current_price <- get_current_price() %>%
  select(bpi.USD.rate_float) %>%
  mutate(date = date) %>%
  dplyr::rename(Price = 1) %>%
  select(2, 1)

historic_price_ten <- get_historic_price("USD", teny_back, date - 1) %>%
  tibble::rownames_to_column("date") %>%
  mutate(date = as.Date(date, "%Y-%m-%d")) %>%
  rbind(current_price) %>%
  mutate(Price = round(Price, 1))

update_chart(
  id = "3ae57b07ddc738d6984ae6d72c027d3d",
  data = historic_price_ten
)

historic_price_one <- get_historic_price("USD", oney_back, date - 1) %>%
  tibble::rownames_to_column("date") %>%
  mutate(date = as.Date(date, "%Y-%m-%d")) %>%
  rbind(current_price) %>%
  mutate(Price = round(Price, 1))

update_chart(
  id = "3ae57b07ddc738d6984ae6d72c0285f7",
  data = historic_price_one
)

historic_price_onem <- get_historic_price('USD', onem_back, date-1) %>%
  tibble::rownames_to_column("date") %>%
  mutate(date = as.Date(date, "%Y-%m-%d")) %>%
  rbind(current_price) %>%
  mutate(Price = round(Price, 1))

update_chart(
  id = "80a5f74298f588521786f9061c21d472",
  data = historic_price_onem
  )


###########################

coinmarketcapr::setup(Sys.getenv("COINMARKETCAPR_API_KEY"))

market_cap <- get_crypto_listings() %>%
  slice(1:10) %>%
  select(name, USD_market_cap)

update_chart(
  id = "9640becc888e8a5d878819445105edce",
  data = market_cap,
  notes = paste0("Stand: ", format(Sys.Date(), format = "%d. %m. %Y"))
)




############################

energy <- read_csv("https://static.dwcdn.net/data/cFnri.csv") %>%
  select(1, 2) %>%
  mutate(Date = as.Date(Date, format = "%Y/%m/%d"))

update_chart(
  id = "b6873820afc5a1492240edc1b101cdd9",
  data = energy,
  notes = paste0("Stand: ", format(last(energy$Date), format = "%d. %m. %Y"))
)


############################
