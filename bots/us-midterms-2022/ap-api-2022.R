#### API AP US Elections 2022 ####

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
# #if tidyverse causes github error
# update.packages(ask = F)

options(scipen=999)
library(tidyverse)
library(jsonlite)
# # setwd for fixes
# setwd("~/Documents/GitHub/st-methods/bots/us-midterms-2022")
# #renv
# library(renv)
# renv::init()
# renv::snapshot()

# API Access 

api <- fromJSON("https://api.ap.org/v3/elections/2022-11-08?apikey=RM9PsVHsJzKBniAlAn6movmTgxTFRwdS&format=json&resultsType=l") 

# api_fips <- fromJSON("https://api.ap.org/v3/elections/2022-11-08?level=fipscode&apikey=RM9PsVHsJzKBniAlAn6movmTgxTFRwdS&format=json&resultsType=t") 

# api_fips2 <- api_fips$races
# saveRDS(api, file = "api-testing1.rds")
# api <- readRDS(file = "api-testing1.rds")

#### House ####
#exclude IN special election for rest of current term, exclude Ranked Choice Elections (RCV)

house <- api$races %>%
  filter(officeName == "U.S. House" & 
           raceType %in% c("General", "Open Primary"))

house_tab <- data.frame()

for (i in 1:nrow(house)) {
  
state <- house$reportingUnits[[i]]$statePostal
cands <- house$reportingUnits[[i]]$candidates %>% bind_rows() %>% as.data.frame()
state_id <- paste0(house$reportingUnits[[i]]$statePostal,"-", house$seatNum[i])

if("winner" %in% colnames(cands))
{
  if("X" %in% cands$winner)
  {
    winners <- cands %>% filter(winner == "X") %>% select(party) %>% as.vector()
    } else
    {
      winners <- "NA"
    }
} else {
  winners <- "NA"
}

house_row <- cbind(state, state_id, winners) %>% as_tibble()
house_tab <- rbind(house_tab, house_row) %>% as_tibble()

}

row.names(house_tab) <- NULL

# AK RCV RESULTS
house_rcv <- api$races %>%
  filter(officeName == "U.S. House" & 
           raceType == "RCV General Election")

house_rcv_ak <- house_rcv$reportingUnits[[1]]$candidates %>% as.data.frame()

if("winner" %in% colnames(house_rcv_ak))
{
  if("X" %in% house_rcv_ak$winner)
  {
    house_tab$winners[house_tab$state_id == "AK-1"] <- house_rcv_ak %>% filter(winner == "X") %>% select(party) %>% as.vector()
  } else
  {
    house_tab$winners[house_tab$state_id == "AK-1"] <- "NA"
  }
} else {
  house_tab$winners[house_tab$state_id == "AK-1"] <- "NA"
}

house_tab$state <- unlist(house_tab$state)
house_tab$winners <- unlist(house_tab$winners)
house_tab$state_id <- unlist(house_tab$state_id)

house_tab$winners[house_tab$winners == "GOP"] <- "republicans"
house_tab$winners[house_tab$winners == "Dem"] <- "democrats"
house_tab$winners[house_tab$winners != "republicans" & 
                    house_tab$winners != "democrats" & 
                    house_tab$winners != "NA"] <- "others"

house_tab$winners[house_tab$state_id == "CA-15"] <- "democrats"
house_tab$winners[house_tab$state_id == "CA-34"] <- "democrats"
house_tab$winners[house_tab$state_id == "ME-2"] <- "democrats"

house_tab <- house_tab %>% select(-state_id)

table(house_tab$winners)

#write_csv(house_tab, "house-election.csv")

#### Senate ####
#INCLUDE special election in OK (4 years) and "Primary" in LA, EXCLUDE special eletion in CA (only rest of 2022), exclude Ranked Choice Elections (RCV)

senate <- api$races %>%
  filter(officeName == "U.S. Senate" & raceID != 8964 & raceID != 3153)

senate_tab <- data.frame()

for (j in 1:nrow(senate)) {
  
  state <- senate$reportingUnits[[j]]$statePostal
  incumbent_name <- paste0(senate$incumbents[[j]]$first, " ",senate$incumbents[[j]]$last)
  incumbent_party <- senate$incumbents[[j]]$party
  cands <- senate$reportingUnits[[j]]$candidates %>% bind_rows() %>% as.data.frame()
  cands$fullname <- paste0(cands$first, " ", cands$last)
  
  if("winner" %in% colnames(cands))
  {
    if("X" %in% cands$winner)
    {
      winners_party <- cands %>% filter(winner == "X") %>% select(party) %>% as.vector()
      winners_name <- cands %>% filter(winner == "X") %>% select(fullname) %>% as.vector()
    } else
    {
      winners_party <- "NA"
      winners_name <- "NA"
    }
  } else {
    winners_party <- "NA"
    winners_name <- "NA"}
  
  senate_row <- cbind(state, incumbent_party, incumbent_name, winners_party, winners_name) %>% as_tibble()
  senate_tab <- rbind(senate_tab, senate_row) %>% as_tibble()
  
}

row.names(senate_tab) <- NULL

senate_tab$state <- unlist(senate_tab$state)
senate_tab$incumbent_party <- unlist(senate_tab$incumbent_party)
senate_tab$incumbent_name <- unlist(senate_tab$incumbent_name)
senate_tab$winners_party <- unlist(senate_tab$winners_party)
senate_tab$winners_name <- unlist(senate_tab$winners_name)

senate_tab$winners_party[senate_tab$winners_party == "GOP"] <- "republicans"
senate_tab$winners_party[senate_tab$winners_party == "Dem"] <- "democrats"
senate_tab$winners_party[senate_tab$winners_party != "republicans" & 
                    senate_tab$winners_party != "democrats" & 
                    senate_tab$winners_party != "NA"] <- "others"


senate_tab$incumbent_party[senate_tab$incumbent_party == "GOP"] <- "republicans"
senate_tab$incumbent_party[senate_tab$incumbent_party == "Dem"] <- "democrats"
senate_tab$incumbent_party[senate_tab$incumbent_party != "republicans" & 
                             senate_tab$incumbent_party != "democrats" & 
                             senate_tab$incumbent_party != "NA"] <- "others"


senate_tab$winners_party[senate_tab$state == "AK"] <- "republicans"
senate_tab$winners_name[senate_tab$state == "AK"]  <- "Lisa Murkowski"

senate_tab$winners_party[senate_tab$state == "GA"] <- "democrats"
senate_tab$winners_name[senate_tab$state == "AK"]  <- "Raphael Warnock"

table(senate_tab$winners_party)

#write_csv(senate_tab, "senate-election.csv")

#### TABLE for Bars ####

bars_tab <- data.frame(matrix(ncol = 9, nrow = 2))
colnames(bars_tab) <- c("","democratsNoElection",	"democratsWinners",	"others",	"contested",	"open",	
                        "republicansWinners",	"republicansNoElection",	"total")

bars_tab[,1] <- c("house", "senate")
bars_tab$democratsNoElection <- c(0, 36)
bars_tab$republicansNoElection <- c(0, 29)
bars_tab$total <- c(435, 100)

win_sen <- table(senate_tab$winners_party) %>% as.data.frame()

bars_tab$open[2] <- win_sen %>% filter(Var1 == "NA") %>% select(Freq)
bars_tab$contested[2] <- 0

if("democrats" %in% win_sen$Var1)
{
  bars_tab$democratsWinners[2] <- win_sen %>% filter(Var1 == "democrats") %>% select(Freq)
} else {
  bars_tab$democratsWinners[2] <- 0
}

if("republicans" %in% win_sen$Var1)
{
  bars_tab$republicansWinners[2] <- win_sen %>% filter(Var1 == "republicans") %>% select(Freq)
} else {
  bars_tab$republicansWinners[2] <- 0
}

if("others" %in% win_sen$Var1)
{
  bars_tab$others[2] <- win_sen %>% filter(Var1 == "others") %>% select(Freq)
} else {
  bars_tab$others[2] <- 0
}

win_hou <- table(house_tab$winners) %>% as.data.frame()

bars_tab$open[1] <- win_hou %>% filter(Var1 == "NA") %>% select(Freq)
bars_tab$contested[1] <- 0

if("democrats" %in% win_hou$Var1)
{
  bars_tab$democratsWinners[1] <- win_hou %>% filter(Var1 == "democrats") %>% select(Freq)
} else {
  bars_tab$democratsWinners[1] <- 0
}

if("republicans" %in% win_hou$Var1)
{
  bars_tab$republicansWinners[1] <- win_hou %>% filter(Var1 == "republicans") %>% select(Freq)
} else {
  bars_tab$republicansWinners[1] <- 0
}

if("others" %in% win_hou$Var1)
{
  bars_tab$others[1] <- win_hou %>% filter(Var1 == "others") %>% select(Freq)
} else {
  bars_tab$others[1] <- 0
}

bars_tab

#### Senat No Election ####
#
# senate_noelection <- read_csv("https://raw.githubusercontent.com/CivilServiceUSA/us-senate/master/us-senate/data/us-senate.csv") %>%
#   select(state_code, name, party, class, term_end) %>% filter(class != "III" & name != "James Inhofe") %>%
#   select(state = state_code, incumbent_party = party, incumbent_name = name)
# 
# senate_noelection$incumbent_party[senate_noelection$incumbent_party == "democrat"] <- "democrats"
# senate_noelection$incumbent_party[senate_noelection$incumbent_party == "independent"] <- "democrats"
# senate_noelection$incumbent_party[senate_noelection$incumbent_party == "republican"] <- "republicans"
# 
# table(senate_noelection$incumbent_party)¨
# 
# write_csv(senate_noelection, "senate_noelection.csv")

#### Q CLI WRITE ####

# import helper functions

source("./helpers.R")

time <- paste0(as.numeric(str_sub(Sys.time(), 12, 13))+1,".", str_sub(Sys.time(), 15, 16), " Uhr")

update_chart(id = "8a89ec29d240ad709dc0c77b7f861387", 
             data = senate_tab,
             updateTime = time)

update_chart(id = "ff8b50a1d393a0b526b98d8f72ef9884", 
             data = senate_tab,
             updateTime = time)

update_chart(id = "ff8b50a1d393a0b526b98d8f72ef9d05", 
             data = house_tab,
             updateTime = time)

update_chart(id = "8a89ec29d240ad709dc0c77b7f85e083", 
             data = house_tab,
             updateTime = time)

update_chart(id = "85c9e635bfeae3a127d9c9db9073107d", 
             data = bars_tab,
             updateTime = time)
