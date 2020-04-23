##### Script for Coronacases #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(clipr)

# setwd("~/Folder") #your working directory, cont - match.csv, pop_kant.csv, coord.csv and countries_pop.csv have to be in it

#get data from JHU
cases <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
dead <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
cured <- read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

#from Open Data Kanton Zürich
kant <- read_csv("https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total.csv")


#### remodel and add recent cured data####

# For chinese regions, choose region, for everyone else choose country

cases$place <- if_else(cases$`Country/Region` == "China", 
                       cases$`Province/State`, 
                       cases$`Country/Region`)

dead$place <- if_else(dead$`Country/Region` == "China", 
                      dead$`Province/State`, 
                      dead$`Country/Region`)

cured$place <- if_else(cured$`Country/Region` == "China", 
                      cured$`Province/State`, 
                      cured$`Country/Region`)

#to long, get total per date and place

cases_crty <- cases %>% 
  gather(date, value, 5:(ncol(cases)-1)) %>% 
  group_by(date, place) %>% 
  summarise(first(`Country/Region`), cases = sum(value, na.rm = T))

dead_ctry <- dead %>% 
  gather(date, value, 5:(ncol(dead)-1)) %>% 
  group_by(date, place) %>%
  summarise(first(`Country/Region`), dead = sum(value, na.rm = T))

cured_ctry <- cured %>% 
  gather(date, value, 5:(ncol(cured)-1)) %>% 
  group_by(date, place) %>%
  summarise(first(`Country/Region`), cured = sum(value, na.rm = T))


#merge, get sick from total, rename, reader
all_ctry <- cbind(as_tibble(dead_ctry), cases_crty$cases)
all_ctry <- left_join(all_ctry, cured_ctry, by = c("date" = "date", "place" = "place")) %>%
  select(-6)

all_ctry$sick <- all_ctry$`cases_crty$cases`-all_ctry$dead-all_ctry$cured
colnames(all_ctry) <- c("Datum","Ort", "Land", "Tote", "alle Fälle", "Genesene", "gegenwärtig Infizierte")

#adapt for Q date format
all_ctry$Datum <- as.Date(all_ctry$Datum, format = "%m/%d/%y")
all_ctry <- arrange(all_ctry, Datum)

#rename Trumpland and correct chinese propaganda
all_ctry$Ort[all_ctry$Ort == "US"] <- "USA"
all_ctry$Land[all_ctry$Ort == "Macau"] <- "Macau"
all_ctry$Land[all_ctry$Ort == "Hong Kong"] <- "Hong Kong"
all_ctry$Ort[all_ctry$Ort == "Taiwan*"] <- "Taiwan"
all_ctry$Land[all_ctry$Land == "Taiwan*"] <- "Taiwan"

#Check for the newsroom, how many countries are involved atm, and tell them 	
aff <- unique(all_ctry$Land[all_ctry$Datum == last(all_ctry$Datum)])
aff #list printed because some spellings are really special AND JHU CHANGES THEM EVERY DAY
length(aff)-1 # This number minus 1 (because of others, this is the Diamond Princess)

#### Country-specific graphics####

# SCHWEIZ (NEW PROCESS)

jhu_ch <- filter(all_ctry, Ort == "Switzerland")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

kant_dec <- kant %>%
  select(date, abbreviation_canton_and_fl, ncumul_deceased) %>%
  spread(abbreviation_canton_and_fl, ncumul_deceased) %>%
  fill(2:28) %>%
  gather(Kanton, Tote, 2:28) %>%
  group_by(date) %>%
  summarise(Tote = sum(Tote, na.rm = T)) %>%
  filter(date > "2020-03-23")

#check how many cantons have reported in the last few days
kant_check <- kant %>%
  select(date, abbreviation_canton_and_fl, ncumul_conf) %>%
  spread(abbreviation_canton_and_fl, ncumul_conf)

tail(kant_check) #if there are cantons that have not reported yesterday, add disclaimer in graphic below
table(is.na(kant_check[nrow(kant_check)-1,])) #how many NAs are there exactly?

kant_conf <- kant %>%
  select(date, abbreviation_canton_and_fl, ncumul_conf) %>%
  spread(abbreviation_canton_and_fl, ncumul_conf) %>%
  fill(2:28) %>%
  gather(Kanton, Infizierte, 2:28) %>%
  filter(Kanton != "FL") %>%
  group_by(date) %>%
  summarise(Infizierte = sum(Infizierte, na.rm = T)) %>%
  filter(date > "2020-03-23")

kant_hosp <- kant %>%
  select(date, abbreviation_canton_and_fl, ncumul_hosp) %>%
  spread(abbreviation_canton_and_fl, ncumul_hosp) %>%
  fill(2:28) %>%
  gather(Kanton, Hospitalisierte, 2:28) %>%
  filter(Kanton != "FL") %>%
  group_by(date) %>%
  summarise(Hospitalisierte = sum(Hospitalisierte, na.rm = T)) %>%
  filter(date > "2020-03-23")

kant_com <- cbind(kant_dec, kant_conf$Infizierte-kant_dec$Tote)
colnames(kant_com) <- c("Datum", "Tote", "Infizierte")

jhu_ch_mod <- jhu_ch %>% 
  filter(Datum < "2020-03-24") %>%
  mutate(Infizierte = Genesene+`gegenwärtig Infizierte`) %>%
  select(Datum, Tote, Infizierte)

ch <- rbind(jhu_ch_mod, kant_com) %>%
  filter(Datum != last(Datum)) %>% #filter today, many cantons have not reported current day. very early, there will not be data for today, if so, edit this out
  mutate(`Genesene (Schätzung)` = ((lag(Infizierte,14, default = 0)) * 0.75) + 
                                             ((lag(Infizierte ,21, default = 0)) * 0.10) + 
                                             ((lag(Infizierte,28, default = 0)) * 0.10) +
                                             ((lag(Infizierte,42, default = 0)) * 0.05)) %>%
  mutate(`gegenwärtig Infizierte` = Infizierte-`Genesene (Schätzung)`) %>%
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene (Schätzung)")

tail(ch)

#copy the data frame to clipboard, just paste it to your favorite graphics tool data entry field, we suggest q.tools
write_clip(ch)
browseURL("https://q.tools/") #in our daily use, this links directly to the data entry page

#cantonal prevalence

kant_pop <- read_csv("pop_kant.csv")

kant_conf2 <- kant %>%
  select(date, abbreviation_canton_and_fl, ncumul_conf) %>%
  spread(abbreviation_canton_and_fl, ncumul_conf) %>%
  fill(2:28) %>%
  gather(Kanton, Infizierte, 2:28) %>%
  filter(date == last(date), Kanton != "FL") %>%
  left_join(kant_pop, by = c("Kanton" = "ktabk")) %>%
  mutate(per_100k = round((100000*Infizierte)/pop, 1)) %>%
  select(kt, per_100k) %>%
  arrange(desc(per_100k))

colnames(kant_conf2) <- c("Kanton", "per100k")

write_clip(kant_conf2) #paste this somewhere

#open observable & download graphics, they should already up to date, link to map Q element is on there too
browseURL("https://observablehq.com/d/0efc001797b68968")

#ITALY
italien <- filter(all_ctry, Ort == "Italy")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")
tail(italien)

tail(italien)
write_clip(italien,  row.names = F) #paste this somewhere


# SPAIN
spanien <- filter(all_ctry, Ort == "Spain")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

tail(spanien) 
write_clip(spanien,  row.names = F) #paste this somewhere

# GERMANY
ger <- filter(all_ctry, Ort == "Germany")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene") %>%
  mutate(`Genesene (Schätzung)` = ((lag((`gegenwärtig Infizierte`+Genesene),14, default = 0)) * 0.75) + 
           ((lag((`gegenwärtig Infizierte`+Genesene) ,21, default = 0)) * 0.10) + 
           ((lag((`gegenwärtig Infizierte`+Genesene),28, default = 0)) * 0.10) +
           ((lag((`gegenwärtig Infizierte`+Genesene),42, default = 0)) * 0.05)) %>%
  mutate(`gegenwärtig Infizierte` = (`gegenwärtig Infizierte`+Genesene)-`Genesene (Schätzung)`) %>%
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene (Schätzung)")

tail(ger)
write_clip(ger,  row.names = F) #paste this somewhere

# FRANCE
france <- filter(all_ctry, Ort == "France")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

#adjust date with time for step-after area chart
france$Datum <- paste0(france$Datum," 00:00")
france <- rbind(france, france[nrow(france),])
france$Datum[nrow(france)] <- paste0(substr(france$Datum[nrow(france)],1,10), " 23:59")

tail(france)
write_clip(france,  row.names = F) #paste this somewhere

# IRAN
iran <- filter(all_ctry, Ort == "Iran")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")
tail(iran)
write_clip(iran,  row.names = F) #paste this somewhere

# SINGAPUR 

singapur <- filter(all_ctry, Ort == "Singapore")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

#adjust date with time for step-after area chart
singapur$Datum <- paste0(singapur$Datum," 00:00")
singapur <- rbind(singapur, singapur[nrow(singapur),])
singapur$Datum[nrow(singapur)] <- paste0(substr(singapur$Datum[nrow(singapur)],1,10), " 23:59")

write_clip(singapur,  row.names = F) #paste this somewhere


#JAPAN

japan <- filter(all_ctry, Ort == "Japan")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

#adjust date with time for step-after area chart
japan$Datum <- paste0(japan$Datum," 00:00")
japan <- rbind(japan, japan[nrow(japan),])
japan$Datum[nrow(japan)] <- paste0(substr(japan$Datum[nrow(japan)],1,10), " 23:59")


write_clip(japan,  row.names = F) #paste this somewhere

#HUBEI NO TIMESTAMP (stable development)

hubei <- filter(all_ctry, Ort == "Hubei")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

write_clip(hubei,  row.names = F) #paste this somewhere

#CHINA NO TIMESTAMP (stable development)

all_china <- all_ctry %>% 
  filter(Land == "China") %>%
  group_by(Datum) %>% 
  summarise(Tote = sum(Tote),
            Genesene = sum(Genesene),
            `alle Fälle` = sum(`alle Fälle`),
            `gegenwärtig Infizierte` = sum (`gegenwärtig Infizierte`)) %>%
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

write_clip(all_china,  row.names = F) #paste this somewhere
## SOUTH KOREA

korea <- filter(all_ctry, Ort == "Korea, South")  %>% 
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

write_clip(korea,  row.names = F) #paste this somewhere

#### COMBOS ####

## ITALY/SOUTH KOREA/IRAN/ COMBO (CASES)
## also just add latest figure from JHU CSSE

koit <- filter(all_ctry, Land %in% c("China","Italy", "Iran", "Korea, South", "Germany", "US", "Switzerland")) %>% 
  select("Datum", "Land", "alle Fälle") %>% 
  group_by(Datum, Land) %>%
  summarise(`alle Fälle` = sum(`alle Fälle`)) %>%
  spread("Land", "alle Fälle")

colnames(koit)
colnames(koit) <- c("Datum","China", "Deutschland", "Iran", "Italien", "Südkorea", "Schweiz", "USA")

write_clip(koit,  row.names = F) #paste this somewhere

#### IT/ESP/BEL

koit2 <- filter(all_ctry, Land %in% c("Italy", "Spain", "Germany", "Belgium", "Switzerland")) %>% 
  select("Datum", "Land", "alle Fälle") %>% 
  group_by(Datum, Land) %>%
  summarise(`alle Fälle` = sum(`alle Fälle`)) %>%
  spread("Land", "alle Fälle")

colnames(koit2)
colnames(koit2) <- c("Datum","Belgien", "Deutschland", "Italien", "Spanien", "Schweiz")

write_clip(koit2,  row.names = F) #paste this somewhere

#### FT-style relative chart WORK IN PROGRESS ####
#this could be done more beautifully with apply/lapply/sapply (if someone is the expert here, feel free)

ftit <- filter(all_ctry, Ort == "Italy" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftch <- filter(all_ctry, Ort == "Switzerland" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftde <- filter(all_ctry, Ort == "Germany" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftsg <- filter(all_ctry, Ort == "Singapore" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftjp <- filter(all_ctry, Ort == "Japan" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftsk <-  filter(all_ctry, Ort == "Korea, South" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftus <-  filter(all_ctry, Ort == "USA" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
ftes <-  filter(all_ctry, Ort == "Spain" & `alle Fälle` > 99) %>% select(`alle Fälle`) %>% deframe()
# ftcn <-  filter(all_ctry, Land == "China") %>% 
#    group_by(Datum) %>%
#    summarise(`alle Fälle` = sum(`alle Fälle`)) %>%
#    filter(`alle Fälle` > 99) %>%
#    select(`alle Fälle`) %>%
#    deframe()

#add china/sweden/spain ????

lmax <- max(length(ftch), 
            length(ftit),
            length(ftde),
            length(ftsg),
            length(ftjp),
            length(ftsk),
            length(ftus),
            length(ftes))

ftit <- c(ftit, rep(NA, lmax-length(ftit)))
ftch <- c(ftch, rep(NA, lmax-length(ftch)))
ftde <- c(ftde, rep(NA, lmax-length(ftde)))
ftsg <- c(ftsg, rep(NA, lmax-length(ftsg)))
ftjp <- c(ftjp, rep(NA, lmax-length(ftjp)))
ftsk <- c(ftsk, rep(NA, lmax-length(ftsk)))
ftus <- c(ftus, rep(NA, lmax-length(ftus)))
ftes <- c(ftes, rep(NA, lmax-length(ftes)))

ft <- cbind((1:lmax)-1 ,ftit, ftch, ftde, ftsg, ftjp, ftsk, ftus, ftes) %>% as.data.frame()

colnames(ft) <- c("Tag", "Italien", "Schweiz", "Deutschland", "Singapur", 
                  "Japan", "Südkorea", "USA", "Spanien")

ft_plot <- gather(ft, Land, Wert, 2:ncol(ft))

ggplot(ft_plot, aes(Tag, Wert, color = Land)) +
  geom_line() + 
  geom_point() + 
  # geom_abline(intercept = log10(100), slope = log10(1.33),linetype="dashed", color = "gray40") + #33% daily growth
  # geom_abline(intercept = log10(100), slope = log10(1.10),linetype="dashed", color = "gray40") + #10% daily growth
  # geom_abline(intercept = log10(100), slope = log10(1.05),linetype="dashed", color = "gray40") + #05% daily growth
  theme_minimal() + 
  theme(legend.position="bottom") +
  scale_color_brewer(palette="Set2") + 
  scale_y_continuous(trans = 'log10', breaks = c(100, 500, 1000, 5000, 10000,50000, 100000, 500000)) + 
  xlab("Tage seit Fall 100")

#write for observable
write_csv(ft, paste0("log-chart-",Sys.Date(),".csv"))

#go to observable
browseURL("https://observablehq.com/@jonasoesch/log-chart")

#replace graphics in these
browseURL("https://q.st.nzz.ch/item/073f7d6543ca8b0496df6a2c29891e39") #CH version
browseURL("https://q.st.nzz.ch/item/8f00e93a18f4425cb353feb870b44199") #DE version

### FT STYLE LOG CHART WITH DEATHS
# Italien, Spanien, USA, Frankreich, UK, Deutschland, Schweiz, Südkorea
fttit <- filter(all_ctry, Ort == "Italy" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttsp <- filter(all_ctry, Ort == "Spain" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttus <-  filter(all_ctry, Ort == "USA" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttfr <- filter(all_ctry, Ort == "France" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttuk <- filter(all_ctry, Ort == "United Kingdom" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttde <- filter(all_ctry, Ort == "Germany" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttch <- filter(all_ctry, Ort == "Switzerland" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
fttsk <-  filter(all_ctry, Ort == "Korea, South" & `Tote` > 20) %>% select(`Tote`) %>% deframe()
#add china????
lmax <- max(length(fttit), 
            length(fttsp), 
            length(fttus),
            length(fttfr),
            length(fttuk),
            length(fttde),
            length(fttch),
            length(fttsk))
fttit <- c(fttit, rep(NA, lmax-length(fttit)))
fttsp <- c(fttsp, rep(NA, lmax-length(fttsp)))
fttch <- c(fttch, rep(NA, lmax-length(fttch)))
fttde <- c(fttde, rep(NA, lmax-length(fttde)))
fttfr <- c(fttfr, rep(NA, lmax-length(fttfr)))
fttuk <- c(fttuk, rep(NA, lmax-length(fttuk)))
fttsk <- c(fttsk, rep(NA, lmax-length(fttsk)))
fttus <- c(fttus, rep(NA, lmax-length(fttus)))
ftt <- cbind((1:lmax)-1 ,fttit, fttsp, fttus, fttfr, fttuk, fttde, fttch, fttsk) %>% as.data.frame()
colnames(ftt) <- c("Tag", "Italien", "Spanien", "USA", "Frankreich", 
                   "Grossbritannien", "Deutschland", "Schweiz", "Südkorea")

# #write here for Q if necessary (it is not pretty/readable)
# clip <- pipe("pbcopy", "w")
# write.table(ft, sep="\t", quote = FALSE, row.names = FALSE, file=clip, na = "")
# close(clip)

ftt_plot <- gather(ftt, Land, Wert, 2:ncol(ftt))
tail(ftt)
ggplot(ftt_plot, aes(Tag, Wert, color = Land)) +
  geom_line() + 
  geom_point() + 
  # geom_abline(intercept = log10(100), slope = log10(1.33),linetype="dashed", color = "gray40") + #33% daily growth
  # geom_abline(intercept = log10(100), slope = log10(1.10),linetype="dashed", color = "gray40") + #10% daily growth
  # geom_abline(intercept = log10(100), slope = log10(1.05),linetype="dashed", color = "gray40") + #05% daily growth
  theme_minimal() + 
  theme(legend.position="bottom") +
  scale_color_brewer(palette="Set2") + 
  scale_y_continuous(trans = 'log10', breaks = c(100, 500, 1000, 5000, 10000,50000, 100000)) + 
  xlab("Tage seit 20 Toten")

#write for observable
write_csv(ftt, paste0("log-chart-dead-",Sys.Date(),".csv"))

# goto observable
browseURL("https://observablehq.com/@xeophin/log-chart-fur-tote")

# use image file it in Q / chart tool

#### Total area chart & China vs. the World ####

all_global <- all_ctry %>% 
  group_by(Datum) %>% 
  summarise(Tote = sum(Tote, na.rm = T),
            Genesene = sum(Genesene, na.rm = T),
            `alle Fälle` = sum(`alle Fälle`, na.rm = T),
            `gegenwärtig Infizierte` = sum (`gegenwärtig Infizierte`, na.rm = T)) %>%
  select("Datum", "Tote", "gegenwärtig Infizierte", "Genesene")

#all
sum(all_global[nrow(all_global),2:4])
#cured
all_global$Genesene[nrow(all_global)]
#Gesunde in Prozent
all_global$Genesene[nrow(all_global)]/sum(all_global[nrow(all_global),2:4])*100

#double time global 
glob_all <- all_global$Genesene+all_global$`gegenwärtig Infizierte`+all_global$Tote
log(2)/(log(last(glob_all)/nth(glob_all, -7))/7)
                
#Tote in Prozent
all_global$Tote[nrow(all_global)]
all_global$Tote[nrow(all_global)]/sum(all_global[nrow(all_global),2:4])*100

write_clip(all_global,  row.names = F) #paste this somewhere

#BUBBLE CHART & write for observable

coord <- read_csv("coord.csv")

all_ctry_land <- all_ctry %>% 
  group_by(Land, Datum) %>% 
  summarise(`alle Fälle` = sum(`alle Fälle`),
            Tote = sum(Tote),
            Genesene = sum(Genesene),
            `gegenwärtig Infizierte` = sum(`gegenwärtig Infizierte`))

#what is in the data, but not coordinate file?
setdiff(coord$Land, all_ctry_land$Land)

#what is in the coordinate, but not data file?
setdiff(all_ctry_land$Land, coord$Land)

#add missings
coord$Land[coord$Land == "Taiwan*"] <- "Taiwan"
  
bubble <- left_join(all_ctry_land, coord, by = c("Land" = "Land"),  na.rm = T)

write_csv(bubble, paste0("corona-bubble-new-",Sys.Date(),".csv"))

#update the data, download and insert GIF somewhere
browseURL("https://observablehq.com/@jonasoesch/covid-19-in-the-world")

#per 100'000
pop <- read_csv("countries_pop.csv")

counts <- all_ctry %>% 
  filter(Datum == last(all_ctry$Datum)) %>%
  group_by(Land, Datum) %>% 
  summarise(fallzahl = sum(`alle Fälle`),
            tote = sum(Tote))

#DIESE MISSINGS IM POPULATIONS-DATENSATZ ERGÄNZEN/LÄNDERNAME ANPASSEN
setdiff(unique(counts$Land), unique(pop$name))

#DOUBLING TIME
lastgr <- all_ctry %>%
  group_by(Land, Datum) %>%
  summarise(fallzahl = sum(`alle Fälle`)) %>% 
  arrange(Land) %>% 
  mutate(daysago = lag(fallzahl, 6)) #letzte 7 Tage

lastgr$daysago[lastgr$Datum < "2020-01-30" ] <- NA

lastgr <- lastgr %>% 
  arrange(Datum) %>%
  mutate(dtime = log(2)/(log(fallzahl/daysago)/7)) #this caluclates doubling time according to method by J.M. Spicer http://rstudio-pubs-static.s3.amazonaws.com/10369_9e0e4a116538489baa18908c1690293c.html
  
lastgr_m <- filter(lastgr,Datum == last(all_ctry$Datum)) #comment out for all dates

#JOIN W Population Size
per_pop <- 
  full_join(pop, lastgr_m, by = c("name" = "Land"))
colnames(per_pop)[2] <-"Popul."

per_pop1 <- per_pop %>%
  filter(Popul. > 999999)  %>%
  mutate(per_100000 = round(100000*fallzahl/Popul., 2)) %>% 
  arrange(desc(per_100000)) %>%
  slice(1:21) %>%
  select(name_ger, per_100000, dtime)

#put in cols for stacked bar chart
per_pop1$`schnelle, ungebremste`<- if_else(per_pop1$dtime < 4, per_pop1$per_100000, 0)
per_pop1$`moderate, ungebremste` <- if_else(per_pop1$dtime < 8 & per_pop1$dtime >= 4, per_pop1$per_100000, 0)
per_pop1$`gebremste` <- if_else(per_pop1$dtime < 30 & per_pop1$dtime >= 8, per_pop1$per_100000, 0)
per_pop1$`stark gebremste oder gestoppte Ausbreitung` <- if_else(per_pop1$dtime >= 30, per_pop1$per_100000, 0)

per_pop2 <- select(per_pop1, -c(2:3))

#WARNING: YOU NEED TO ADJUST TIMESTAMP (STAND) IN Q
write_clip(per_pop2,  row.names = F) #paste this somewhere

#Verstorbenen-Rangliste
per_pop_tote <- 
  full_join(pop, counts, by = c("name" = "Land"))
colnames(per_pop_tote)[2] <-"Popul."

per_pop_tote1 <- per_pop_tote %>%
  filter(Popul. > 999999)  %>%
  mutate(per_100000 = round(100000*tote/Popul., 2)) %>% 
  arrange(desc(per_100000)) %>%
  slice(1:21) %>%
  select(name_ger, per_100000)

write_clip(per_pop_tote1,  row.names = F) #paste this somewhere

## doubling time comp
dsel <- lastgr %>% filter(Land %in% c("Switzerland", "Germany", "US", "Italy", "Korea, South")) %>%
  filter(fallzahl > 99, dtime < 101) %>%
  select(-daysago, -fallzahl) %>%
  spread(Land, dtime)

dbch <- dsel$Switzerland[!is.na(dsel$Switzerland)]
dbde <- dsel$Germany[!is.na(dsel$Germany)]
dbus <- dsel$US[!is.na(dsel$US)]
dbit <- dsel$Italy[!is.na(dsel$Italy)]
dbsk <- dsel$`Korea, South`[!is.na(dsel$`Korea, South`)]

dbmax <- max(length(dbch), 
            length(dbit),
            length(dbde),
            length(dbsk),
            length(dbus))

dbit <- c(dbit, rep(NA, dbmax-length(dbit)))
dbch <- c(dbch, rep(NA, dbmax-length(dbch)))
dbde <- c(dbde, rep(NA, dbmax-length(dbde)))
dbsk <- c(dbsk, rep(NA, dbmax-length(dbsk)))
dbus <- c(dbus, rep(NA, dbmax-length(dbus)))

#this could be done more beautifully with apply/lapply/sapply (if someone is the expert here, feel free)

db <- cbind((1:dbmax)-1 ,dbde, dbit, dbsk, dbch, dbus) %>% as.data.frame()

colnames(db) <- c("Tage seit dem 100. Fall", "Deutschland", "Italien", "Südkorea", "Schweiz", "USA")


write_clip(db,  row.names = F) #paste this somewhere

##Most affected European countries by status
match <- read_csv("match - cont.csv")
eur <- left_join(all_ctry, match, by = "Ort") %>% 
  filter(Continent == "Europa" & Datum == last(Datum)) %>%
  arrange(desc(`alle Fälle`)) %>%
  unique() %>%
  slice(1:21) %>%
  left_join(pop,by = c("Land.x" = "name")) %>%
  select(name_ger, Tote, "gegenwärtig Infizierte", "Genesene")

colnames(eur)[1] <- "Land"

#WARNING: YOU NEED TO ADJUST TIMESTAMP (STAND) IN Q
write_clip(eur) #paste this somewhere

## USA BUBBLE (just for verification purposes)
americafirst <- read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv")
unk <- americafirst %>% filter(county == "Unknown", date == last(date)) %>% arrange(desc(cases))
sum(unk$cases)

#download latest gif (data updates automatically from nyt repo)
browseURL("https://observablehq.com/d/dc4b219b7b2c69ea")

#### Rolling average deaths ####

most_dead <- all_ctry %>%
  select (Datum, Land, Tote) %>%
  filter (Datum == last(Datum)) %>%
  arrange(desc(Tote)) %>%
  slice(1:30)

rolling_average <- all_ctry %>%
  group_by(Land, Datum) %>%
  summarise(Tote = sum(Tote, na.rm = T)) %>% 
  arrange(Land) %>% 
  mutate(tmin7 = lag(Tote, 7)) %>% # 7 Tage zurück
  mutate(delta7 = Tote-tmin7) %>%
  mutate(ravg_deaths = delta7/7) %>%
  left_join(pop, by = c("Land"= "name")) %>%
  select(Datum, Land, name_ger, ravg_deaths) %>%
  filter(Land %in% most_dead$Land) %>%
  mutate(steigung = case_when 
         (lag(ravg_deaths, 3) < ravg_deaths ~ "steigend", 
           lag(ravg_deaths, 3) >= ravg_deaths ~ "sinkend"))

tail(rolling_average)

#colnames(rolling_average)[3] <- "Land_ger"
write_csv(rolling_average, paste0("rolling_average-", Sys.Date(),".csv"))

# open Observable, and upload new csv there and generate pngs.
browseURL("https://observablehq.com/d/03813f210bf24b22")


#fin
