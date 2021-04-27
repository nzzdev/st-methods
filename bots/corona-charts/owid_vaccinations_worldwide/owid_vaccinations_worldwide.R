#### Script for Vaccinations ####

# prep
rm(list = ls(all = TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen = 999)
library(tidyverse)
library(clipr)
library(reticulate)

library(jsonlite)

update_chart <- function(id, title = "", subtitle = "", notes = "", data = list()) {
  qConfig <- fromJSON("../q.config.json", simplifyDataFrame = TRUE)
  for (item in qConfig$items) {
    index <- 0
    for (environment in qConfig$items$environments) {
      index <- index + 1
      if (environment$id == id) {
        if (title != "") {
          qConfig$items$item$title[[index]] <- title
        }
        if (subtitle != "") {
          qConfig$items$item$subtitle[[index]] <- subtitle
        }
        if (notes != "") {
          qConfig$items$item$notes[[index]] <- notes
        }
        if (length(data) > 0) {
          qConfig$items$item$data[[index]] <- rbind(names(data), as.matrix(data))
        }
        print(paste0("Successfully updated item with id ", id))
      }
    }
  }
  qConfig <- toJSON(qConfig, pretty = TRUE)
  write(qConfig, "../q.config.json")
}


# set working directory
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

# read-in
owid_raw <- read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv")
pop <- read_csv("countries_pop.csv") %>%
  add_row(name = "European Union", `2018` = 446777673, name_ger = "EU") %>%
  add_row(name = "World", `2018` = 7591945270.5, name_ger = "Welt")

# Adding missing nations
pop$name_ger[pop$name == "Seychelles"] <- "Seychellen"
pop$name[pop$name == "US"] <- "United States"
pop$name[pop$name == "Korea, South"] <- "South Korea"
pop$name[pop$name == "West Bank and Gaza"] <- "Palestine"
pop$name_ger[pop$name == "Palau"] <- "Palau"

owid_pop <- owid_raw %>%
  left_join(pop, by = c("location" = "name"))

owid_check <- owid_pop %>%
  select(location, name_ger, iso_code) %>%
  unique() %>%
  filter(is.na(name_ger))

owid_check # These are British overseas territories, British nations and conglomerates (world, EU). If "real"countries are here, add them above

solid_ctry <- owid_pop %>%
  filter(!is.na(total_vaccinations), !is.na(name_ger)) %>%
  group_by(location) %>%
  filter(last(date) >= Sys.Date() - 14 & first(date) <= Sys.Date() - 30) %>%
  summarise(n = n()) %>%
  filter(n >= 5) %>%
  select(location) %>%
  as_vector() %>%
  unname()

vacc_esti <- owid_pop %>%
  filter(location %in% solid_ctry, date >= last(date) - 14) %>%
  group_by(location) %>%
  summarise(
    max_iqr = quantile(daily_vaccinations, 0.75, na.rm = TRUE),
    min_iqr = quantile(daily_vaccinations, 0.25, na.rm = TRUE),
    mean = mean(daily_vaccinations, na.rm = TRUE)
  )

vacc_esti_lag <- owid_pop %>%
  filter(location %in% solid_ctry, date >= last(date) - 28 & date < last(date) - 14) %>%
  group_by(location) %>%
  summarise(mean = mean(daily_vaccinations, na.rm = TRUE))

vacc_proj_date <- tibble()

for (i in 1:length(solid_ctry)) {
  dates_proj <- seq(last(owid_pop$date[owid_pop$location == solid_ctry[i]]) + 1, as.Date("2099-12-31"), by = "days")
  dates_proj_lag <- seq(nth(owid_pop$date[owid_pop$location == solid_ctry[i]], -13), as.Date("2099-12-31"), by = "days")
  ndays_proj <- seq(1, length(dates_proj), by = 1)
  ndays_proj_lag <- seq(1, length(dates_proj_lag), by = 1)
  vacc_proj_mean <- ndays_proj * vacc_esti$mean[vacc_esti$location == solid_ctry[i]] + last(na.omit(owid_pop$total_vaccinations[owid_pop$location == solid_ctry[i]]))
  vacc_proj_mean_lag <- ndays_proj_lag * vacc_esti_lag$mean[vacc_esti_lag$location == solid_ctry[i]] + nth(na.omit(owid_pop$total_vaccinations[owid_pop$location == solid_ctry[i]]), -14)

  if (length(vacc_proj_mean_lag) < length(vacc_proj_mean)) {
    vacc_proj_mean_lag <- rep(NA, length(vacc_proj_mean))
  }
  # vacc_proj_max_iqr <- ndays_proj*vacc_esti$max_iqr[vacc_esti$location == "Switzerland"] + last(owid_pop$total_vaccinations[owid_pop$location == "Switzerland"])
  # vacc_proj_min_iqr <- ndays_proj*vacc_esti$min_iqr[vacc_esti$location == "Switzerland"] + last(owid_pop$total_vaccinations[owid_pop$location == "Switzerland"])

  proj_raw <- tibble(dates_proj, vacc_proj_mean)
  proj_raw_lag <- tibble(dates_proj_lag, vacc_proj_mean_lag)

  herd_immunity_140 <- first(owid_pop$`2018`[owid_pop$location == solid_ctry[i]] * 1.4)
  herd_immunity_70pct <- herd_immunity_140 / 2

  herd_immunity_date <- first(proj_raw$dates_proj[vacc_proj_mean > herd_immunity_140])
  herd_immunity_previous_date <- first(proj_raw_lag$dates_proj_lag[vacc_proj_mean_lag > herd_immunity_140])

  location <- solid_ctry[i]

  vacc_proj_temp <- tibble(location, herd_immunity_140, herd_immunity_70pct, herd_immunity_date, herd_immunity_previous_date)
  vacc_proj_date <- rbind(vacc_proj_date, vacc_proj_temp)
}

vacc_sum <- owid_pop %>%
  select(location, name_ger, iso_code, date, total_vaccinations, people_vaccinated, people_fully_vaccinated) %>%
  group_by(location) %>%
  summarise_all(last) %>%
  ungroup() %>%
  select(name_ger, location, iso_code, total_vaccinations, people_vaccinated, people_fully_vaccinated)

over65 <- read_csv("API_SP.POP.65UP.TO.ZS_DS2_en_csv_v2_1929265.csv", skip = 3) %>%
  select(`Country Code`, `2019`) %>%
  rename(iso_code = `Country Code`, percentage_above64 = `2019`) %>%
  mutate(percentage_above64 = round(percentage_above64, 1))

vacc_final <- vacc_sum %>%
  left_join(over65, by = "iso_code") %>%
  full_join(vacc_proj_date, by = "location") %>%
  filter(location %in% solid_ctry) %>%
  select(-location) %>%
  rename(location = name_ger)

vacc_final$iso_code[vacc_final$location == "Welt"] <- "Welt"
vacc_final$iso_code[vacc_final$location == "EU"] <- "EU"


vacc_final$people_fully_vaccinated[vacc_final$location == "Welt"] <- NA
vacc_final$people_fully_vaccinated[vacc_final$location == "EU"] <- NA

update_chart(id = "79af3c6593df15827ccb5268a7aff0be", data = vacc_final, notes = "Stand: 27. 4. 2021")