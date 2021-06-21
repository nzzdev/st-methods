#### Corona-Script SWITZERLAND (automated version) #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)

# import helper functions
source("./helpers.R")

# read in additional data
# pop <- read_csv("./corona-auto-ch/pop_kant.csv")
pop <- read_csv("pop_kant.csv")

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
  select(region, median_R_highHPD,median_R_lowHPD,median_R_mean) %>%
  arrange (desc(median_R_mean)) %>%
  left_join(pop[,1:2], by = c("region" = "ktabk"))

eth_cantons_title <- paste0("Der Kanton ", eth_cantons[1,5], " verzeichnet den höchsten R-Wert")
eth_cantons_notes <- paste0("Die Daten liegen in einem 95%-Konfidenzintervall. Wir zeigen nur die R-Werte für die zehn grössten Kantone.",
                            " In kleinen Kantonen ist der Unsicherheitsbereich teilweise sehr gross, so dass keine verlässlichen Aussagen möglich sind.",
                            " Die neusten Schätzungen der Kantone liegen in der Regel einige Tage hinter der nationalen Schätzung.<br> Stand: ",
                            format(nth(eth$Datum, -2)-4, format = "%d. %m. %Y"))

colnames(eth_cantons) <- c("Kanton", "", "Unsicherheitsbereich", "Median")

#q-cli update
update_chart(id = "f649302cbf7dd462f339d0cc35d9695a", 
             data = eth_cantons, 
             notes = eth_cantons_notes,
             title = eth_cantons_title)


