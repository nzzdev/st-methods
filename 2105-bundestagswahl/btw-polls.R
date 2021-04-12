#### BTW 2021 Polls ####

# prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(clipr)
library(coalitions)
library(jsonlite)

setwd("~/NZZ-Mediengruppe/NZZ Visuals - Dokumente/Projekte/_2021/2105 Bundestagswahl/data")

# read in polls
# quick and dirty, get "real date" and maybe error margins from respondents
pollsters <- coalitions:::.pollster_df %>%
  add_row(pollster = "yougov", address = "https://www.wahlrecht.de/umfragen/yougov.htm")

# combine pollsters with loop
polls_btw_all <- tibble()

for (i in 1:8){
polls_btw_temp <- scrape_wahlrecht(address = pollsters$address[i]) %>%
  select(-start, -end) %>% #adjust: better dates, use respondents for margins
  mutate(polnr = row_number()) %>% #get identifiers for multiple polls on one day
  gather(party, value, 2:(ncol(.)-2)) %>%
  filter(party != "pirates" & party != "fw") %>% #adjust: put fw and pirates in others
  add_column(pollster = pollsters$pollster[i])

polls_btw_all <- rbind(polls_btw_all, polls_btw_temp)
}

table(polls_btw_all$party)

polls_btw <- polls_btw_all %>%
  select(-respondents)%>% 
  filter(date > "2017-09-24") #only dates after last election

moe <- polls_btw_all %>%
  arrange(date) %>%
  filter(date >= last(date)-30) %>%
  mutate(ci = 100*1.96*sqrt((value/100)*(1-(value/100)))/sqrt((60400000-1)*respondents/(60400000-respondents))) %>%
  group_by(party) %>%
  summarise(mean_ci = mean(ci))

# moe formula derived from https://goodcalculators.com/margin-of-error-calculator/
# population size (german eligible voters) derived from https://www.bundeswahlleiter.de/info/presse/mitteilungen/bundestagswahl-2021/01_21_wahlberechtigte-geschaetzt.html

#### Line Chart ####

party_colors_de_nzz <- c("#0a0a0a", "#c31906","#66a622", "#d1cc00", "#8440a3","#d28b00" ,"#0084c7", "#616161")
names(party_colors_de_nzz) <- names(party_colors_de)

# quick and dirty ggplot w/ loess estimations - look into mcp and bcp, kalman
ggplot(polls_btw, aes(date, value, color = party)) +
  geom_point(alpha = 0.2, size = 0.5) +
  geom_smooth(method="loess", span = .05, se = F, size = 0.5) +
  scale_color_manual(breaks = names(party_colors_de_nzz), values=unname(party_colors_de_nzz)) + 
  theme_minimal() + theme(legend.position="top")

#prep for json, add last election values
polls_btw_json <- polls_btw %>%
  spread(party, value) %>%
  select(pollster, date, cdu, spd, greens, fdp, left, afd, others)
# %>%
#   add_row(pollster = "lastElection", 
#           date = as.Date("2017-09-24"), 
#           cdu = 32.9, 
#           spd = 20.5, 
#           greens = 8.9, 
#           fdp = 10.7, 
#           left = 9.2, 
#           afd = 12.6, 
#           others = 5)

#add loess estimation to json in loop
polls_loess <- tibble()

for (j in 1:length(unique(polls_btw$party))){
  
polls_loess_temp <- polls_btw %>% 
  filter(party == unique(polls_btw$party)[j], pollster != "lastElection") %>%
  mutate(date_num = as.numeric(date)) %>%
  mutate(loess = predict(loess(value ~ date_num, data =., span = 0.05))) %>%
  select(date, party, loess) %>%
  unique() %>%
  mutate(pollster = "average") %>%
  rename(value = loess) 

polls_loess <- rbind(polls_loess, polls_loess_temp)
}
  
# plot loess only for comparison
ggplot(polls_loess, aes(date, value, color = party)) +
  geom_line() +   
  scale_color_manual(breaks = names(party_colors_de_nzz), values=unname(party_colors_de_nzz)) + 
  theme_minimal() + theme(legend.position="top")

#add loess to json
polls_loess_json <- polls_loess %>% 
  spread(party, value) %>%
  select(pollster, date, cdu, spd, greens, fdp, left, afd, others)

polls_btw_finaljson <- rbind(polls_btw_json, polls_loess_json) %>%
  arrange(date)

polls_btw_finaljson_eng <- rbind(polls_btw_json, polls_loess_json) %>%
  arrange(date)
#rename
colnames(polls_btw_finaljson) <- c("institute", "date", "Union", "SPD", "Grüne", "FDP", "Linke", "AfD", "Übrige")

#write to file
write_json(polls_btw_finaljson, "lineChart.json", pretty = F)

#### Comparison Chart ####

#reformat line chart data
polls_bars_json <- polls_btw_finaljson_eng %>%
    add_row(pollster = "lastElection",
            date = as.Date("2017-09-24"),
            cdu = 32.9,
            spd = 20.5,
            greens = 8.9,
            fdp = 10.7,
            left = 9.2,
            afd = 12.6,
            others = 5) %>%
  gather(party, value, 3:9) %>%
  filter(pollster  %in% c("lastElection", "average")) %>%
  arrange(date) %>%
  filter(date == first(date) | date == last(date)) %>% 
  select(-date) %>%
  spread(pollster, value) %>%
  full_join(moe, by = "party") %>%
  mutate(upperBound = average + mean_ci) %>% 
  mutate(lowerBound = average - mean_ci) %>%
  select(party, lastElection, lowerBound, average, upperBound)

polls_bars_json$party[polls_bars_json$party == "spd"] <- "SPD"
polls_bars_json$party[polls_bars_json$party == "cdu"] <- "Union"
polls_bars_json$party[polls_bars_json$party == "greens"] <- "Grüne"
polls_bars_json$party[polls_bars_json$party == "left"] <- "Linke"
polls_bars_json$party[polls_bars_json$party == "fdp"] <- "FDP"
polls_bars_json$party[polls_bars_json$party == "afd"] <- "AfD"
polls_bars_json$party[polls_bars_json$party == "others"] <- "Übrige"
#write
write_json(polls_bars_json, "projectionChart.json", pretty = F)


#Koalitionen

#get best guess from loess
koalitionen <- polls_loess %>%
  filter(date == max(date)) %>%
  filter(party != "others" & value > 5) %>% #remove parties < 5%
  mutate(value_5pct = 100*value/sum(value)) %>%
  mutate(seats = round(value_5pct*709/100, 0)) %>% #project to 598 seats
  select(party, seats)

#enter to q manually
koalitionen
browseURL("https://q.st.nzz.ch/editor/coalition_calculation/5a185919e8abb7921435a6114ddc04be")
browseURL("https://q.st.nzz.ch/editor/coalition_calculation/4d49811bb12bc13788c30c9a190f6ed1")

#fin
