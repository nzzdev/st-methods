# NZZ Visuals, script that provides research results and data visualisation for the following article: 
# https://www.nzz.ch/ld.1422907
# questions and comments: marie-jose.kolly@nzz.ch



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### MISE EN PLACE ###

# Load libraries
library(dplyr)
library(tidyr)
library(ggplot2)
library(readxl)
library(stringr)
library(reshape)
library(countrycode)

# Set writing directory
setwd("mypath/graphics")



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### READ, CLEAN AND PROCESS WEAPON EXPORT DATA THIS PART IS A CITATION FROM THE SRF DATA SCRIPT ON WEAPON EXPORTS (AND THEREFORE IN GERMAN): https://srfdata.github.io/2017-02-kriegsmaterial/  ###


# Alle Exceltabellen liegen aufsteigend in einer Arbeitsmappe, so dass sheet1 = 2000, sheet2 = 2001 usw
# lade alle sheets der Arbeitsmappe als data frames in eine Liste sheets
sheets <- list()
for(i in 1:18){
  sheets[[i]] <- read_excel("yourpath/data/2000-2017.xlsx", sheet = i)
  k <- c(2000:2017)
  sheets[[i]]$Jahr <- k[i]
}
# Liste "sheets" enthält nun einzelne data frames, wobei sheets[[1]]= 2000, sheets[[2]]= 2001 usw. 

# einzelne dataframes zu einem einzigen frame mergen und durch leere Spalten in den Ausgangsdaten erzeugte NA's durch Nullen ersetzen
export <- do.call(rbind.data.frame, sheets)
export[is.na(export)] <- 0
rm(sheets, i ,k)

# # Daten kondensieren (breit nach lang)
export_restructured <- export %>% 
  as.data.frame() %>% 
  tidyr::gather(key = "variable", value = "value", 2:12)
rm(export)

# Wie viele Länder gibt es? 
laender <- arrange(export_restructured, Land) # nach Ländernamen sortieren
unique(laender$Land) # vorkommende Ländernamen anzeigen: gibt es Duplikate
length(unique(laender$Land)) # wie viele Länder gibt es insgesamt (mit Duplikaten)?

# Manuell umschreiben
export_restructured$Land[export_restructured$Land == "Aegypten / Egypte"|export_restructured$Land == "Aegypten"] <- "Ägypten"
export_restructured$Land[export_restructured$Land == "Andorra "] <- "Andorra"
export_restructured$Land[export_restructured$Land == "Arab. Emirate / Emirats Arabes"|export_restructured$Land == "Arabische Emirate"] <- "Vereinigte Arabische Emirate"
export_restructured$Land[export_restructured$Land == "Argentinien / Argentine"] <- "Argentinien"
export_restructured$Land[export_restructured$Land == "Australien / Australie"] <- "Australien"
export_restructured$Land[export_restructured$Land == "Bahrein"|export_restructured$Land =="Bahrein / Bahrein"] <- "Bahrain"
export_restructured$Land[export_restructured$Land == "Belgien "|export_restructured$Land =="Belgien / Belgique"] <- "Belgien"
export_restructured$Land[export_restructured$Land == "Benin "|export_restructured$Land == "Benin /Benin"|export_restructured$Land == "Benin / Bénin"] <- "Benin"
export_restructured$Land[export_restructured$Land == "Bosnien / Bosnie"|export_restructured$Land == "Bosnien"|export_restructured$Land == "Bosnien und Herzeg."] <- "Bosnien-Herzegowina"
export_restructured$Land[export_restructured$Land == "Botswana / Botswana"|export_restructured$Land == "Botwana"] <- "Botswana"
export_restructured$Land[export_restructured$Land == "Brasilien / Brésil"] <- "Brasilien"
export_restructured$Land[export_restructured$Land == "Bangladesh"] <- "Bangladesch"
export_restructured$Land[export_restructured$Land == "Brunei /Brunei"|export_restructured$Land == "Brunel"] <- "Brunei"
export_restructured$Land[export_restructured$Land == "Bulgarien / Bulgaarie"|export_restructured$Land == "Bulgarien / Bulgarie"] <- "Bulgarien"
export_restructured$Land[export_restructured$Land == "Burkina Fasso / Burkina Faso"|export_restructured$Land == "Burkin Fasso"|export_restructured$Land == "Burkina Fasso"] <- "Burkina Faso"
export_restructured$Land[export_restructured$Land == "Buthan / Bouthan"|export_restructured$Land =="Buthan"] <- "Bhutan"
export_restructured$Land[export_restructured$Land == "Chile / Chili"] <- "Chile"
export_restructured$Land[export_restructured$Land == "Costa Rica / Costa Rica"] <- "Costa Rica"
export_restructured$Land[export_restructured$Land == "Dänemark / Danemark"] <- "Dänemark"
export_restructured$Land[export_restructured$Land == "Deutschland / Allemagne"] <- "Deutschland"
export_restructured$Land[export_restructured$Land == "Dom. Rep. / Rep Dom."|export_restructured$Land == "Dom Rep"|export_restructured$Land == "Dominika Rep."] <- "Dominikanische Republik"
export_restructured$Land[export_restructured$Land == "Elfenbeinküste\r\n"] <- "Elfenbeinküste"
export_restructured$Land[export_restructured$Land == "Estland / Estonie"] <- "Estland"
export_restructured$Land[export_restructured$Land == "Finnland / Finlande"|export_restructured$Land == "Finnland "|export_restructured$Land == "Finnnland / Finiande"|export_restructured$Land == "Finnnland"] <- "Finnland"
export_restructured$Land[export_restructured$Land == "Frankreich "|export_restructured$Land == "Frankreich / France"] <- "Frankreich"
export_restructured$Land[export_restructured$Land == "Franz Polynesien"] <- "Französisch-Polynesien"
export_restructured$Land[export_restructured$Land == "Großbritannien"|export_restructured$Land == "Gossbritannien"|export_restructured$Land == "Gr. Britannien / Royaume Uni"] <- "Grossbritannien"
export_restructured$Land[export_restructured$Land == "Griechenland / Grece"|export_restructured$Land == "Griechenland / Grèce"] <- "Griechenland"
export_restructured$Land[export_restructured$Land == "Hongkong"|export_restructured$Land == "Hongkong / Hong Kong"] <- "Hong-Kong"
export_restructured$Land[export_restructured$Land == "Indien / Inde"] <- "Indien"
export_restructured$Land[export_restructured$Land == "Indonesien / Indonésie"|export_restructured$Land == "Indonesien / Indonesie"] <- "Indonesien"
export_restructured$Land[export_restructured$Land == "Irland / Irlande"] <- "Irland"
export_restructured$Land[export_restructured$Land == "Island "|export_restructured$Land == "Island / Islande"] <- "Island"
export_restructured$Land[export_restructured$Land == "Italien / Italie"] <- "Italien"
export_restructured$Land[export_restructured$Land == "Japan /Japon"] <- "Japan"
export_restructured$Land[export_restructured$Land == "Jordanien / Jordanie"] <- "Jordanien"
export_restructured$Land[export_restructured$Land == "Kamerun "|export_restructured$Land == "Kamerun / Cameroune"] <- "Kamerun"
export_restructured$Land[export_restructured$Land == "Kanada / Canada"|export_restructured$Land == "Kanada "] <- "Kanada"
export_restructured$Land[export_restructured$Land == "Kasachstan / Kzakhstan"] <- "Kasachstan"
export_restructured$Land[export_restructured$Land == "Kenia / Kenya"] <- "Kenia"
export_restructured$Land[export_restructured$Land == "Korea (Süd) "|export_restructured$Land == "Korea (Süd) / Corée du Sud"|export_restructured$Land == "Korea (Süd) / Corte du Sud"|export_restructured$Land == "Korea (Süd)"|export_restructured$Land == "Süd Korea"] <- "Südkorea"
export_restructured$Land[export_restructured$Land == "Kroatien / Croatie"] <- "Kroatien"
export_restructured$Land[export_restructured$Land == "Kuwait / Kowe'it"|export_restructured$Land == "Kuwait / Koweït"|export_restructured$Land == "Kuwait "] <- "Kuwait"
export_restructured$Land[export_restructured$Land == "Lettland / Letonie"|export_restructured$Land == "Lettland "] <- "Lettland"
export_restructured$Land[export_restructured$Land == "Libanon / Liban"|export_restructured$Land == "Lebanon"] <- "Libanon"
export_restructured$Land[export_restructured$Land == "Libyen / Libye"] <- "Libyen"
export_restructured$Land[export_restructured$Land == "Litauen / Lituanie"] <- "Litauen"
export_restructured$Land[export_restructured$Land == "Luxemburg / Luxembourg"] <- "Luxemburg"
export_restructured$Land[export_restructured$Land == "Macau / Macau"|export_restructured$Land == "Macao"] <- "Macau"
export_restructured$Land[export_restructured$Land == "Malaysia / Malaisie"] <- "Malaysia"
export_restructured$Land[export_restructured$Land == "Malta / Malte"] <- "Malta"
export_restructured$Land[export_restructured$Land == "Namibia / Namibie"] <- "Namibia"
export_restructured$Land[export_restructured$Land == "Neuseeland / Nvl. Zelande"|export_restructured$Land == "Neuseeland / Nouvelle Zélande"] <- "Neuseeland"
export_restructured$Land[export_restructured$Land == "Niederlände"|export_restructured$Land == "Niederlande / Pays-Bas"|export_restructured$Land == "Niederlände / Pays-Bas"] <- "Niederlande"
export_restructured$Land[export_restructured$Land == "Niger / Niger"] <- "Niger"
export_restructured$Land[export_restructured$Land == "Norwegen / Norvege"|export_restructured$Land == "Norwegen / Norvège"] <- "Norwegen"
export_restructured$Land[export_restructured$Land == "Oman / Oman"] <- "Oman"
export_restructured$Land[export_restructured$Land == "Österreich / Autriche"] <- "Österreich"
export_restructured$Land[export_restructured$Land == "Pakistan / Pakistan"] <- "Pakistan"
export_restructured$Land[export_restructured$Land == "Peru / Pérou"] <- "Peru"
export_restructured$Land[export_restructured$Land == "Philippinen / Philipinnes"] <- "Philippinen"
export_restructured$Land[export_restructured$Land == "Polen / Pologne"] <- "Polen"
export_restructured$Land[export_restructured$Land == "Portugal / Portugal"] <- "Portugal"
export_restructured$Land[export_restructured$Land == "Rumänien / Roumanie"] <- "Rumänien"
export_restructured$Land[export_restructured$Land == "Russland / Russie"] <- "Russland"
export_restructured$Land[export_restructured$Land == "San Marino / St Marin"] <- "San Marino"
export_restructured$Land[export_restructured$Land == "Saudi Arabien"|export_restructured$Land == "Saudi Arabien / Arab. Saoudite"|export_restructured$Land == "Saudi Arabien /Arab. Saoudite"|export_restructured$Land == "Saudi Arabien "] <- "Saudi-Arabien"
export_restructured$Land[export_restructured$Land == "Schweden / Suade"|export_restructured$Land == "Schweden / Suède" ] <- "Schweden"
export_restructured$Land[export_restructured$Land == "Singapur / Singapour"] <- "Singapur"
export_restructured$Land[export_restructured$Land == "Slowakai / Slovaquie"|export_restructured$Land == "Slowakai"] <- "Slowakei"
export_restructured$Land[export_restructured$Land == "Slowenien / Slovenie"] <- "Slowenien"
export_restructured$Land[export_restructured$Land == "Spanien / Espagne"] <- "Spanien"
export_restructured$Land[export_restructured$Land == "Südafrika / Afrique du Sud"] <- "Südafrika"
export_restructured$Land[export_restructured$Land == "Thailand / Thailande"] <- "Thailand"
export_restructured$Land[export_restructured$Land == "Tschechien / Rep. Tcheque"|export_restructured$Land == "Tschechien / Rép. Tchèque"] <- "Tschechien"
export_restructured$Land[export_restructured$Land == "Tunesien / Tunisie"] <- "Tunesien"
export_restructured$Land[export_restructured$Land == "Türkei / Turquie"|export_restructured$Land == "Türkei "] <- "Türkei"
export_restructured$Land[export_restructured$Land == "Ungarn / Hongrie"] <- "Ungarn"
export_restructured$Land[export_restructured$Land == "Uruguay / Uruguay"] <- "Uruguay"
export_restructured$Land[export_restructured$Land == "USA "|export_restructured$Land == "USA / Etats-Unis" | export_restructured$Land == "U.S.A"] <- "USA"
export_restructured$Land[export_restructured$Land == "Zypern / Chypre"] <- "Zypern"
export_restructured$Land[export_restructured$Land == "Antillen, Niederl."] <- "Niederländische Antillen"
export_restructured$Land[export_restructured$Land == "Kirgistan / Kirghistan"|export_restructured$Land == "Kirgistan"] <- "Kirgisistan"
export_restructured$Land[export_restructured$Land == "Ecuador "] <- "Ecuador"
export_restructured$Land[export_restructured$Land == "Madagascar"] <- "Madagaskar"
export_restructured$Land[export_restructured$Land == "Salvador"] <- "El Salvador"
export_restructured$Land[export_restructured$Land == "Surinam"] <- "Suriname"

# Wie viele Länder gibt es jetzt noch? 
length(unique(export_restructured$Land)) # Anzahl Länder
sort(unique(export_restructured$Land)) # Überblick über die Ländernamen, um eventuell übersehene Duplikate aufzuspüren

# Wie hat sich das Exportvolumen über die Jahre verändert?
Export <- export_restructured %>% 
  group_by(Jahr) %>% # ordnet die Daten nach Jahren an
  dplyr::summarise(value = sum(value)) # fasst Exportvolumen nach Jahren zusammen



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### READ, CLEAN AND PROCESS CONFLICT DATA ###

# Read uppsala conflict data: state-based dataset, UCDP/PRIO Armed Conflict Dataset version 18.1, cf. http://ucdp.uu.se/downloads/, 
conflictGov_orig<-read.csv("yourname/data/uppsalaCrisisData/state/ucdp-prio-acd-181.csv")

# define dates as dates
conflictGov_orig$start_date2<-as.Date(conflictGov_orig$start_date2, format="%Y-%m-%d")
conflictGov_orig$ep_end_date<-as.Date(conflictGov_orig$ep_end_date, format="%Y-%m-%d")

# if ep_end_date is NA (in 1795 cases), this means that either the conflict continued in the following year (following row) or, if year==2017, that it is possibly still ongoing (next data release: May 2018). leave NA in all the cases where year!=2017, add 2017-12-31 in all the cases where year==2017. Where we leave NA, ggplot2's geom_segment will disregard these rows, which is exactly what we want as these are intermediate stages and not the end of a conflict
conflictGov_orig$ep_end_date[is.na(conflictGov_orig$ep_end_date) & conflictGov_orig$year==2017]<-"2017-12-31"
conflictGov_orig[is.na(conflictGov_orig$ep_end_date),] %>% nrow()

# get rid of conflicts that ended before 2000 as our data does not go back further than that
conflictGov<-conflictGov_orig %>% 
  filter(!ep_end_date<"2000-01-01")

# view different conflict actors. we will keep governments of states only
unique(conflictGov$side_a)
unique(conflictGov$side_b)
unique(conflictGov$side_a_2nd) # sehr weit gefasst, sogar switzerland, im afghanistan-konflikt...sollten aber gucken, dass side_a und side_b immer gleich wie location, sonst ersetzen!
unique(conflictGov$side_b_2nd)



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### RENAME COUNTRIES FOR LATER MATCHING THEM WITH CONFLICT DATA ###

# Get German and English country names to match export data (German) with conflict data (English)
codelist_enDe<-data.frame("en"=as.character(codelist$country.name.en), "de"=as.character(codelist$country.name.de))
codelist_enDe$de<-as.character(codelist_enDe$de)

# Create duplicate of dataframe as we will going rename some countries
export_restructured_dup<-export_restructured

# Which levels of Land are not found in our country vector?
export_restructured_dup$Land[which(!(export_restructured_dup$Land %in% codelist_enDe$de))] %>% unique()

# Check how these should be written
codelist_enDe[grep("Poly", codelist_enDe$de),]

# Replace variants in variable "Land" to match codelist
export_restructured_dup$Land[export_restructured_dup$Land == "Grossbritannien"] <- "Großbritannien"
export_restructured_dup$Land[export_restructured_dup$Land == "Hong-Kong"] <- "Hongkong"
export_restructured_dup$Land[export_restructured_dup$Land == "Tschechien"] <- "Tschechische Republik"
export_restructured_dup$Land[export_restructured_dup$Land == "Tschechische Rep."] <- "Tschechische Republik"
export_restructured_dup$Land[export_restructured_dup$Land == "USA"] <- "Vereinigte Staaten"
export_restructured_dup$Land[export_restructured_dup$Land == "Saudi-Arabien"] <- "Saudi Arabien"
export_restructured_dup$Land[export_restructured_dup$Land == "Heiliger Stuhl"] <- "Vatikanstaat"
export_restructured_dup$Land[export_restructured_dup$Land == "Macau"] <- "Macao"
export_restructured_dup$Land[export_restructured_dup$Land == "Russland"] <- "Russische Föderation"
export_restructured_dup$Land[export_restructured_dup$Land == "Südkorea"] <- "Korea, Republik von"
export_restructured_dup$Land[export_restructured_dup$Land == "Brunei"] <- "Brunei Darussalam"
export_restructured_dup$Land[export_restructured_dup$Land == "Suriname"] <- "Surinam"
export_restructured_dup$Land[export_restructured_dup$Land == "Bosnien-Herzegowina"] <- "Bosnien und Herzegowina"
export_restructured_dup$Land[export_restructured_dup$Land == "Kap Verde"] <- "Cabo Verde"
export_restructured_dup$Land[export_restructured_dup$Land == "Trinidad Tobago"] <- "Trinidad und Tobago"
export_restructured_dup$Land[export_restructured_dup$Land == "Französisch-Polynesien"] <- "Französisch Polynesien"

# Join codelist to export data
export_restructured_augm<-export_restructured_dup %>%
  left_join(.,codelist_enDe, by=c("Land"="de"))

# Check if all english names are here
export_restructured_augm[which(is.na(export_restructured_augm$en)),]
data.frame(export_restructured_augm$Land, export_restructured_augm$en)



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### PROCESS DATA FRAMES AND COMBINE WEAPON EXPORT DATA WITH CONFLICT DATA ###

# Sometimes several states are primarily involved as well as several supporting co-actors; side_a and side_b are primary actors, side_a_2nd and side_b_2nd secondary/supporting actors in a conflict
conflictGov<-conflictGov %>%
  mutate(side_a_red=gsub("Government of ", "", side_a)) %>%
  mutate(side_b_red=ifelse(grepl("Gov", side_b)==T, paste0(gsub("Government of ", "", side_b)), NA)) %>%
  mutate(side_a_2nd_red=ifelse(grepl("Gov", side_a_2nd)==T, paste0(gsub("Government of ", "", side_a_2nd)), NA)) %>%
  mutate(side_b_2nd_red=ifelse(grepl("Gov", side_b_2nd)==T, paste0(gsub("Government of ", "", side_b_2nd)), NA)) %>%
  mutate(mainSides=ifelse(!is.na(side_b_red), paste(side_a_red, side_b_red, sep=", "),side_a_red)) %>%
  mutate(coSides=ifelse(!is.na(side_a_2nd_red) & !is.na(side_b_2nd_red), paste(side_a_2nd_red, side_b_2nd_red, sep=", "), 
                        ifelse(is.na(side_a_2nd_red) & !is.na(side_b_2nd_red), side_b_2nd_red,
                               ifelse(is.na(side_b_2nd_red) & !is.na(side_a_2nd_red), side_a_2nd_red, NA))))

# Check which levels are not matched in country name vector
conflictGov$mainSides[which(!(conflictGov$mainSides %in% codelist$country.name.en))] %>% unique()
conflictGov$coSides[which(!(conflictGov$coSides %in% codelist$country.name.en))] %>% unique() #15 non-matches,  most of them are groups of countries. we decided to pick russia (in syria, ukraine and georgia) and saudi arabia and the united arab emirates (in yemen) from the side_2nd-parts and not to show the others, as we (NZZ) regard these to be major actors in these conflicts. 

# Replace if spelling different from codelist; check how these should be written
codelist_enDe[grep("Yem", codelist_enDe$en),]

# Replace Land to match codelist, primary actors
conflictGov$mainSides<-as.character(conflictGov$mainSides)
conflictGov$mainSides[conflictGov$mainSides == "Yemen (North Yemen)"|conflictGov$mainSides == "South Yemen"] <- "Yemen"
conflictGov$mainSides[conflictGov$mainSides == "Cambodia (Kampuchea)"] <- "Cambodia"
conflictGov$mainSides[conflictGov$mainSides == "Russia (Soviet Union)"] <- "Russia"
conflictGov$mainSides[conflictGov$mainSides == "Serbia (Yugoslavia)"] <- "Serbia"
conflictGov$mainSides[conflictGov$mainSides == "Macedonia, FYR"] <- "Macedonia"
conflictGov$mainSides[conflictGov$mainSides == "Trinidad and Tobago"] <- "Trinidad & Tobago"
conflictGov$mainSides[conflictGov$mainSides == "Congo"] <- "Congo - Brazzaville"
conflictGov$mainSides[conflictGov$mainSides == "DR Congo (Zaire)"] <- "Congo - Kinshasa"
conflictGov$mainSides[conflictGov$mainSides == "United States of America"] <- "United States"
conflictGov$mainSides[conflictGov$mainSides == "Bosnia-Herzegovina"] <- "Bosnia & Herzegovina"
conflictGov$mainSides[conflictGov$mainSides == "Ivory Coast"] <- "Côte d’Ivoire"
conflictGov$mainSides[conflictGov$mainSides == "Zimbabwe (Rhodesia)"] <- "Zimbabwe"
conflictGov$mainSides[conflictGov$mainSides == "South Vietnam"|conflictGov$mainSides == "Vietnam (North Vietnam)"|conflictGov$mainSides == "South Vietnam, Vietnam (North Vietnam)"] <- "Vietnam"
# secondary actors
conflictGov$coSides<-as.character(conflictGov$coSides)
conflictGov$coSides[conflictGov$coSides == "Yemen (North Yemen)"|conflictGov$coSides == "South Yemen"] <- "Yemen"
conflictGov$coSides[conflictGov$coSides == "Cambodia (Kampuchea)"] <- "Cambodia"
conflictGov$coSides[conflictGov$coSides == "Russia (Soviet Union)"] <- "Russia"
conflictGov$coSides[conflictGov$coSides == "Serbia (Yugoslavia)"] <- "Serbia"
conflictGov$coSides[conflictGov$coSides == "Macedonia, FYR"] <- "Macedonia"
conflictGov$coSides[conflictGov$coSides == "Trinidad and Tobago"] <- "Trinidad & Tobago"
conflictGov$coSides[conflictGov$coSides == "Congo"] <- "Congo - Brazzaville"
conflictGov$coSides[conflictGov$coSides == "DR Congo (Zaire)"] <- "Congo - Kinshasa"
conflictGov$coSides[conflictGov$coSides == "United States of America"] <- "United States"
conflictGov$coSides[conflictGov$coSides == "Bosnia-Herzegovina"] <- "Bosnia & Herzegovina"
conflictGov$coSides[conflictGov$coSides == "Ivory Coast"] <- "Côte d’Ivoire"
conflictGov$coSides[conflictGov$coSides == "Zimbabwe (Rhodesia)"] <- "Zimbabwe"
conflictGov$coSides[conflictGov$coSides == "South Vietnam"|conflictGov$coSides == "Vietnam (North Vietnam)"|conflictGov$coSides == "South Vietnam, Vietnam (North Vietnam)"] <- "Vietnam"


# When there are several actors on one side, duplicate all the according rows and make country name unique (e.g. entries for india, entries for pakistan, in the case of location=="India, Pakistan")
# Strategy: create new dataframe with duplicate, replace country name, replace country name in original data frame, rbind

# Which levels are not matched yet?
conflictGov$mainSides[which(!(conflictGov$mainSides %in% codelist$country.name.en))] %>% unique()
conflictGov$coSides[which(!(conflictGov$coSides %in% codelist$country.name.en))] %>% unique()

codelist_enDe[grep("Mor", codelist_enDe$en),]

# India, Pakistan
indpak<-conflictGov[conflictGov$mainSides == "India, Pakistan",]
indpak$mainSides<-"Pakistan"
conflictGov$mainSides[conflictGov$mainSides == "India, Pakistan"]<-"India"
conflictGov<-rbind(conflictGov,indpak)

# Cambodia (Kampuchea), Thailand
camtha<-conflictGov[conflictGov$mainSides == "Cambodia (Kampuchea), Thailand",]
camtha$mainSides<-"Thailand"
conflictGov$mainSides[conflictGov$mainSides == "Cambodia (Kampuchea), Thailand"]<-"Cambodia"
conflictGov<-rbind(conflictGov,camtha)

# Eritrea, Ethiopia
erieth<-conflictGov[conflictGov$mainSides == "Eritrea, Ethiopia",]
erieth$mainSides<-"Ethiopia"
conflictGov$mainSides[conflictGov$mainSides == "Eritrea, Ethiopia"]<-"Eritrea"
conflictGov<-rbind(conflictGov,erieth)

# South Sudan, Sudan
sousud<-conflictGov[conflictGov$mainSides == "South Sudan, Sudan",]
sousud$mainSides<-"Sudan"
conflictGov$mainSides[conflictGov$mainSides == "South Sudan, Sudan"]<-"South Sudan"
conflictGov<-rbind(conflictGov,sousud)

# Djibouti, Eritrea
djieri<-conflictGov[conflictGov$mainSides == "Djibouti, Eritrea",]
djieri$mainSides<-"Eritrea"
conflictGov$mainSides[conflictGov$mainSides == "Djibouti, Eritrea"]<-"Djibouti"
conflictGov<-rbind(conflictGov,djieri)

# Afghanistan, United Kingdom, United States of America
afgkin<-conflictGov[conflictGov$mainSides == "Afghanistan, United Kingdom, United States of America",]
afgame<-conflictGov[conflictGov$mainSides == "Afghanistan, United Kingdom, United States of America",]
afgkin$mainSides<-"United Kingdom"
afgame$mainSides<-"United States"
conflictGov$mainSides[conflictGov$mainSides == "Afghanistan, United Kingdom, United States of America"]<-"Afghanistan"
conflictGov<-rbind(conflictGov,afgkin, afgame)

# Australia, United Kingdom, United States of America, Iraq
ausira<-conflictGov[conflictGov$mainSides == "Australia, United Kingdom, United States of America, Iraq",]
auskin<-conflictGov[conflictGov$mainSides == "Australia, United Kingdom, United States of America, Iraq",]
ausame<-conflictGov[conflictGov$mainSides == "Australia, United Kingdom, United States of America, Iraq",]
ausira$mainSides<-"Iraq"
auskin$mainSides<-"United Kingdom"
ausame$mainSides<-"United States"
conflictGov$mainSides[conflictGov$mainSides == "Australia, United Kingdom, United States of America, Iraq"]<-"Australia"
conflictGov<-rbind(conflictGov,ausira, auskin, ausame)

# As stated above, we will add several secondary actors and treat them as if they were main actors (rationale: see article, https://www.nzz.ch/ld.1422907).
# Get detailed date information from in conflictGov_orig, on saudi arabia and united arab emirates (yemen) and russia (syria, ukraine, georgia).
# Start and end date are not always equal to those of the general conflict, as some secondary actors started supporting a primary actor after a conflict had been going on for a while
# Add names, dates. If the data only provide date information at the year-level, we assume the conflict to have started on January 1st and ended on December 31st
conflictGov_orig[grep("Saudi", conflictGov_orig$side_a_2nd),] # Saudi arabia was part of the US-lead conflict against al-Qaida in 2004-2007 (with Afghanistan, Pakistan, UK), and against the "IS" in Irak in 2014-2017 (with 12 other states)
conflictGov_orig[grep("Saudi", conflictGov_orig$side_b_2nd),] # Saudi arabia fought against Kuwait on Iraq's side in 1991 along with many others, and was active in Yemen from 2015-2017 (with Bahrain, Egypt, Jordan, Kuwait, Morocco, Qatar, Sudan, Emirates, but as a leader of this coalition)
conflictGov_orig[grep("Emira", conflictGov_orig$side_a_2nd),] # The Emirates were part of conflicts in Afghanistan and Irak against the "IS" and the Taleban, along with many other countries 
conflictGov_orig[grep("Emira", conflictGov_orig$side_b_2nd),] # The Emirates are part of the Yemen conflict, along with Saudiarabia, Bahriain, Egypt, Jordan, Kuwait, Morocco, Qatar, Sudan.
conflictGov_orig[grep("Russ", conflictGov_orig$side_a_2nd),] # Russia is part of conflicts in Syria , with Iran, 2015-2017, against Syrian insurgents and IS", together with Syrian Government as a primary actor
conflictGov_orig[grep("Russ", conflictGov_orig$side_b_2nd),] # Ukraine (2014-2017), Georgia (2008)

# Saudi arabia: conflict_id 230 | Emirates: conflict_id 230 | Russia: 299, 13604 (Syria), 13246, 13247, 13306 (Ukraine)
conflictGov_coSides<-conflictGov[conflictGov$conflict_id %in% c(230, 299, 393, 13604, 13246, 13247, 13306),] #build rest from this and from grep saudi in conflictGov_orig
emirates<-conflictGov[conflictGov$conflict_id %in% c(230),]
emirates$mainSides<-"United Arab Emirates"
conflictGov_coSides<-rbind(conflictGov_coSides, emirates)
conflictGov_coSides[conflictGov_coSides$mainSides=="Yemen",]$mainSides<-"Saudi Arabia"
conflictGov_coSides[conflictGov_coSides$mainSides=="Ukraine" | conflictGov_coSides$mainSides=="Syria",]$mainSides<-"Russia"
conflictGov_coSides<-conflictGov_coSides[-which(conflictGov_coSides$mainSides=="Georgia" & conflictGov_coSides$year==2004),] # get rid of the part of the Georgia-conflict that did not involve Russia
conflictGov_coSides[conflictGov_coSides$mainSides=="Georgia",]$mainSides<-"Russia" # get rid of the part of the Georgia-conflict that did not involve Russia

# Adapt dates: start and end year: sideb2nd was not necessarily part for the entire time of the conflict, e.g. saudi arabia in yemen (conflict 230 has been going for longer).
conflictGov_coSides[conflictGov_coSides$mainSides %in% c("Saudi Arabia", "United Arab Emirates"),]$start_date2<-"2015-01-01"
conflictGov_coSides[conflictGov_coSides$mainSides %in% c("Saudi Arabia", "United Arab Emirates"),]$ep_end_date<-"2017-12-31"
conflictGov_coSides[conflictGov_coSides$conflict_id==299,]$start_date2<-"2015-01-01"
conflictGov_coSides[conflictGov_coSides$conflict_id==299,]$ep_end_date<-"2017-12-31"
conflictGov_coSides[conflictGov_coSides$conflict_id==393,]$start_date2<-"2008-08-08" # as this was a short war, detailed dates were added
conflictGov_coSides[conflictGov_coSides$conflict_id==393,]$ep_end_date<-"2008-08-16"
conflictGov_coSides[conflictGov_coSides$conflict_id==13604,]$start_date2<-"2015-01-01"
conflictGov_coSides[conflictGov_coSides$conflict_id==13604,]$start_date2<-"2015-01-01"
conflictGov_coSides[conflictGov_coSides$conflict_id==13246,] #already has the correct dates
conflictGov_coSides[conflictGov_coSides$conflict_id==13247,] #already has the correct dates
conflictGov_coSides[conflictGov_coSides$conflict_id==13306,] #already has the correct dates

# Bind to conflictGov
conflictGov<-rbind(conflictGov, conflictGov_coSides)

# Add columns with start year and end year
conflictGov<-conflictGov %>%
  mutate("start_year"=substr(start_date2, 1, 4), "end_year"=substr(ep_end_date, 1, 4))

# Add column where we adapt the start date to 2000-01-01 whenever a conflict started before that - as we are not able to show export data further back than 2000, and this is a step used for visualising the data with ggplot2
conflictGov<-conflictGov %>% 
  mutate("start_date3"=ifelse(start_date2<="2000-01-01", "2000-01-01", as.character(start_date2)))
conflictGov$start_date3<-as.Date(conflictGov$start_date3, format="%Y-%m-%d")

# Visualize conflicts
conflictGov$mainSides<-as.factor(conflictGov$mainSides)
ggplot(conflictGov)+#conflictGov_export_adapt
  geom_segment(aes(x=start_date2, xend=ep_end_date, y=mainSides, yend=mainSides, group=mainSides))
ggsave("conflict.pdf", height=12)

# subset confclit data by those countries that Switzerland exports weaopns to
conflictGov$mainSides[which((conflictGov$mainSides %in% export_restructured_augm$en))] %>% unique()
conflictGov_export<-conflictGov[which((conflictGov$mainSides %in% export_restructured_augm$en)),]
unique(conflictGov_export$mainSides)


## There are also one-sided conflicts where the Government of a country used arms against the population. Read and process these data ##
conflictOne<-read.csv("yourpath/data/uppsalaCrisisData/oneSided/ucdp-onesided-181.csv")
conflictOne<-conflictOne[grep("Government", conflictOne$actor_name_fulltext),] # get those conflicts that stem from the Government
conflictOne<-conflictOne %>% 
  filter(year>=2000)

# Check, by hand, if the actor is always the same government as stated in the column location
data.frame(conflictOne$actor_name, conflictOne$location)

# Adapt one instance:
conflictOne$mainSides<-conflictOne$location
conflictOne$mainSides[conflictOne$actor_name == "Government of Uganda"& conflictOne$year==2000]<-"Uganda"

# Check which of the conflict country names do not appear in the codelist english country names
conflictOne$mainSides[which(!(conflictOne$mainSides %in% codelist$country.name.en))] %>% unique()

# Replace if different spelling; check spelling
codelist_enDe[grep("Myan", codelist_enDe$en),]

# Replace elements of column "Land" to match codelist
conflictOne$mainSides<-as.character(conflictOne$mainSides)
conflictOne$mainSides[conflictOne$mainSides == "Yemen (North Yemen)"|conflictOne$mainSides == "South Yemen"] <- "Yemen"
conflictOne$mainSides[conflictOne$mainSides == "Russia (Soviet Union)"] <- "Russia"
conflictOne$mainSides[conflictOne$mainSides == "DR Congo (Zaire)"] <- "Congo - Kinshasa"
conflictOne$mainSides[conflictOne$mainSides == "Zimbabwe (Rhodesia)"] <- "Zimbabwe"
conflictOne$mainSides[conflictOne$mainSides == "Ivory Coast"] <- "Côte d’Ivoire"
conflictOne$mainSides[conflictOne$mainSides == "Madagascar (Malagasy)"] <- "Madagascar"

# When there are two Governments: Which government is the actor? Check and only include this country
conflictOne$mainSides[conflictOne$mainSides == "Central African Republic, Chad"] <- "Central African Republic"
conflictOne$mainSides[conflictOne$mainSides == "DR Congo (Zaire), Uganda"] <- "Congo - Kinshasa"
conflictOne$mainSides[conflictOne$mainSides == "Burundi, Tanzania"] <- "Burundi"
conflictOne$mainSides[conflictOne$mainSides == "DR Congo (Zaire), Rwanda"] <- "Rwanda"
conflictOne$mainSides[conflictOne$mainSides == "Ethiopia, Sudan"] <- "Ethiopia"
conflictOne$mainSides[conflictOne$mainSides == "Ethiopia, Somalia"] <- "Ethiopia"
conflictOne$mainSides[conflictOne$mainSides == "Chad, Sudan"] <- "Sudan"
conflictOne$mainSides[conflictOne$mainSides == "South Sudan, Sudan"] <- "Sudan"
conflictOne$mainSides[conflictOne$mainSides == "Lebanon, Syria"] <- "Syria"
conflictOne$mainSides[conflictOne$mainSides == "Israel, Lebanon"] <- "Israel"
conflictOne$mainSides[conflictOne$mainSides == "Bangladesh, Myanmar (Burma)"] <- "Myanmar (Burma)"

# Subset dataframe by those countries that are in the export countries
conflictOne$mainSides[which((conflictOne$mainSides %in% export_restructured_augm$en))] %>% unique()
conflictOne_export<-conflictOne[which((conflictOne$mainSides %in% export_restructured_augm$en)),]

# Compare structures of the two confict data frames and adapt their respective structures in order to be able to bind those data frames together
str(conflictOne)
str(conflictGov)

conflictOne_export_adapt<-conflictOne_export %>% 
  mutate("conflict_id"=conflict_id, "start_year"=year, "end_year"=year, "start_date2"=paste0(year, "-01-01"), "start_date3"=paste0(year, "-01-01"), "ep_end_date"=paste0(year,"-12-31"), "side_a"=actor_name, "side_b"="none", "mainSides"=mainSides) %>%
  select(conflict_id, location, mainSides, side_a, side_b, year, start_date2, start_date3, ep_end_date, start_year, end_year)

conflictGov_export_adapt<-conflictGov_export %>%
  select(conflict_id, location, mainSides, side_a, side_b, year, start_date2, start_date3, ep_end_date, start_year, end_year)

summary(conflictGov_export_adapt)
summary(conflictOne_export_adapt)

conflict_export<-rbind(conflictGov_export_adapt,conflictOne_export_adapt)

# Find countries that were in conflict as well as exported weapons to from 2000 on
intersect(conflict_export$mainSides, export_restructured_augm$en)

# Now find countries that were in conflict *in same year* as weapon exports happened

# For this, first summarize export data in order to get one value per year (pool over weapon type variable)
countryXtime_augm<-export_restructured_augm %>%
  group_by(Land, en, Jahr) %>%
  summarize(value = sum(value)) %>%
  arrange(Land,en, Jahr)

# Merge the conflict and the weapon export data using the English codelist column
conflict_export_merged<-conflict_export %>%
  left_join(.,countryXtime_augm, by=c("mainSides"="en"))

# How many countries were sold weapons in years where they were in conflict?
cntries_export_conflict_sametime<-conflict_export_merged %>%
  filter(!is.na(conflict_export_merged$Land)) %>%
  filter(value!=0 & Jahr >= start_year & Jahr <= end_year)
unique(cntries_export_conflict_sametime$Land)



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### RESULTS AND VISUALIZATION ###

# To find out how weapon exports to conflict parties developed over time, we need unique country-year-combinations
cntries_export_conflict_sametime
conflictGov_export_conflictCntryTime_red<-cntries_export_conflict_sametime %>%
  group_by(Land, Jahr)%>%
  slice(1L)%>%
  arrange(Land, Jahr)

conflictGov_export_conflictCntryTime_red$Land%>%unique() # check number of states
conflictGov_export_conflictCntryTime_red

# How many years did we export arms to a country that was in conflict at the same time?
article_table<-conflictGov_export_conflictCntryTime_red %>%
  group_by(Land) %>%
  summarise(nYears=n()) %>%
  arrange(desc(nYears))

# And how much did we export to such countries, per year?
exportvolumeXconflictYearCountry<-conflictGov_export_conflictCntryTime_red %>%
  group_by(Land)%>%
  summarize(totalExportVolume=sum(value))%>%
  arrange(desc(totalExportVolume))

ggplot(conflictGov_export_conflictCntryTime_red, aes(x=Jahr, y=value))+
  geom_bar(stat="identity")

ggplot(conflictGov_export_conflictCntryTime_red, aes(x=Jahr, y=value, fill=Land))+
  geom_bar(stat="identity")

# Write absolute numbers
article<-cntries_export_conflict_sametime %>%
  group_by(Land, Jahr)%>%
  slice(1L)%>%
  group_by(Jahr)%>%
  summarise(total=sum(value))%>%
  arrange(Jahr)
write.table(article, file="yourpath/data/output/exportWhileConflict_cntries.txt", sep="\t", row.names=F, quote=F)

# Write numbers relative to total weapon exports
export_conflictVsAll<-data.frame(article, Export)
export_conflictVsAll_rel<-export_conflictVsAll %>%
  mutate(proportion=100*total/value)
export_conflictVsAll_rel
write.table(export_conflictVsAll_rel, file="yourpath/data/exportWhileConflict_cntries_prop.txt", sep="\t", row.names=F, quote=F)

# Write numbers relative to total weapon exports, by country, for the 5 countries where Switzerland exported weapons during conflicts during the most years
countries<-c("Vereinigte Staaten", "Pakistan", "Indien", "Thailand", "Türkei")
export_conflictCntriesVsAll_selection<-conflictGov_export_conflictCntryTime_red %>%
  left_join(Export[-19,], by=("Jahr"="Jahr")) %>%
  mutate(proportion=100*value.x/value.y)%>%
  filter(Land %in% countries)%>%
  select(Jahr, Land, proportion)

export_conflictCntriesVsAll_andere <- conflictGov_export_conflictCntryTime_red %>%
  left_join(Export[-19,], by=("Jahr"="Jahr")) %>%
  filter(!Land %in% countries) %>%
  group_by(Jahr, value.y) %>%
  summarize(value = sum(value.x)) %>%
  mutate(proportion=100*value/value.y, Land="Andere")%>%
  select(Jahr, Land, proportion)

# Bind countries and others, reshape and write
export_conflictCntriesVsAll_article<-rbind(export_conflictCntriesVsAll_selection, export_conflictCntriesVsAll_andere)
export_conflictCntriesVsAll_article_wide<-export_conflictCntriesVsAll_article %>%
  spread(Land, proportion)
export_conflictCntriesVsAll_article_wide[is.na(export_conflictCntriesVsAll_article_wide)] <- 0
write.table(export_conflictCntriesVsAll_article_wide, file="yourpath/data/exportWhileConflict_cntries_prop_byCountry.txt", sep="\t", row.names=F, quote=F)

# Merge number of years and export volume per country for table in article
article_table_augm<-merge(exportvolumeXconflictYearCountry, article_table, by.x="Land", by.y="Land") %>%
  arrange(desc(nYears))
write.table(article_table_augm, file="/Users/marie-jose/Documents/a_NZZ/projects/a_2018/waffenexporte/data/output/exportWhileConflict_YearXCntry_V2.txt", sep="\t", row.names=F,quote=F, fileEncoding = "UTF-8")

## Small multiples of export volume and conflict ##

# Augment the export data with more pseudo-detailed date indication for ggplot to accept it
countryXtime_augm$Jahr_augm<-rep(1,nrow(countryXtime_augm))

# Set July 1st as mid-point of the bar
for (i in 1:nrow(countryXtime_augm)) countryXtime_augm$Jahr_augm[i]<-paste(countryXtime_augm$Jahr[i],"07","01",sep="-")
countryXtime_augm$Jahr_augm<-as.Date(countryXtime_augm$Jahr_augm, format="%Y-%m-%d")

# Subset countryXtime_augm to keep only those countries that were in a conflict sometime from 2000 on
countryXtime_augm_conflict<-countryXtime_augm[countryXtime_augm$Land %in% cntries_export_conflict_sametime$Land,]
conflict_export_red<-conflict_export_merged[conflict_export_merged$Land %in% cntries_export_conflict_sametime$Land,]

# Relevel for order of facets
countryXtime_augm_conflict$Land_neu = factor(countryXtime_augm_conflict$Land, levels=c('Vereinigte Staaten','Türkei','Indien','Pakistan', 'Thailand', 'Russische Föderation', 'Israel', 'Philippinen', 'Indonesien', 'Kenia', 'Libanon', 'Mali', 'Saudi Arabien', 'Sudan', 'Vereinigte Arabische Emirate', 'Elfenbeinküste', 'Großbritannien', 'Guinea', 'Niger', 'Ägypten', 'Algerien', 'Australien', 'Bahrain', 'Bangladesch', 'Brasilien', 'Jordanien', 'Kolumbien', 'Malaysia', 'Tunesien', 'Uganda', 'Ukraine', 'Venezuela'))
conflict_export_red$Land_neu = factor(conflict_export_red$Land, levels=c('Vereinigte Staaten','Türkei','Indien','Pakistan', 'Thailand', 'Russische Föderation', 'Israel', 'Philippinen', 'Indonesien', 'Kenia', 'Libanon', 'Mali', 'Saudi Arabien', 'Sudan', 'Vereinigte Arabische Emirate', 'Elfenbeinküste', 'Großbritannien', 'Guinea', 'Niger', 'Ägypten', 'Algerien', 'Australien', 'Bahrain', 'Bangladesch', 'Brasilien', 'Jordanien', 'Kolumbien', 'Malaysia', 'Tunesien', 'Uganda', 'Ukraine', 'Venezuela'))

# Plot small multiples
ggplot(countryXtime_augm_conflict, aes(x=Jahr_augm, y=value))+
  geom_segment(data=conflict_export_red, aes(x=start_date3, xend=ep_end_date, y=125000000, yend=125000000, col="darkgray"))+ #use start_date3, here, as a trick to show all the data!
  geom_bar(stat="identity") + 
  facet_wrap(~Land_neu)+
  scale_x_date(breaks=as.Date(c("2000-01-01","2017-12-31")),labels=c("2000", "2017"),
               limits = as.Date(c('2000-01-01','2017-12-31')))+
  scale_y_continuous(breaks=c(0, 60000000, 120000000), labels=c("0", "60000000", "120000000"))+
  theme_minimal()+
  theme(axis.text.x=element_text(family="GT America", color="#05032d", size=11),
        axis.text.y=element_text(family="GT America", color="#05032d", size=11),
        legend.position="none",
        axis.title.x=element_blank(),
        axis.title.y=element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.minor.y = element_blank())
ggsave("conflict_export.svg", width=12)
ggsave("conflict_export.pdf", width=12)

#now just plot the export with free scales
ggplot(countryXtime_augm_conflict, aes(x=Jahr_augm, y=value))+
  geom_segment(data=conflict_export_red, aes(x=start_date3, xend=ep_end_date, y=2, yend=2, col="darkgray"))+
  geom_bar(stat="identity") + 
  facet_wrap(~Land_neu, scales="free_y")+
  scale_x_date(breaks=as.Date(c("2000-01-01","2017-12-31")),labels=c("2000", "2017"),
               limits = as.Date(c('2000-01-01','2017-12-31')))+
  theme_minimal()+
  theme(axis.text.x=element_text(family="GT America", color="#05032d", size=11),
        axis.text.y=element_text(family="GT America", color="#05032d", size=11),
        legend.position="none",
        axis.title.x=element_blank(),
        axis.title.y=element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.minor.y = element_blank())
ggsave("conflict_export_freeY_V2.svg", width=12)
ggsave("conflict_export_freeY_V2.pdf", width=12)

# Plot small multiples with flexible Y-axis
countries<-c("Vereinigte Arabische Emirate", "Saudi Arabien", "Indien", "Pakistan", "Russische Föderation", "Thailand", "Türkei", "Vereinigte Staaten")
for (i in countries){
  countryi<-subset(countryXtime_augm_conflict, countryXtime_augm_conflict$Land_neu==i)
  countryi_conflicti<-subset(conflict_export_red,conflict_export_red$Land_neu==i)
  ggplot(countryi, aes(x=Jahr_augm, y=value))+
    geom_segment(data=countryi_conflicti, aes(x=start_date3, xend=ep_end_date, y=2, yend=2, col="darkgray"))+
    geom_bar(stat="identity") + 
    facet_wrap(~Land_neu, scales="free_y")+
    #scale_x_date(breaks=as.Date(c("2000-01-01","2017-12-31")),labels=c("2000", "2017"),
    #              limits = as.Date(c('2000-01-01','2017-12-31')))+
    theme_minimal()+
    theme(axis.text.x=element_text(family="GT America", color="#05032d", size=11),
          axis.text.y=element_text(family="GT America", color="#05032d", size=11),
          legend.position="none",
          axis.title.x=element_blank(),
          axis.title.y=element_blank(),
          panel.grid.minor.x = element_blank(),
          panel.grid.minor.y = element_blank())
  ggsave(paste0("conflict_exportXtime_cntry_selection", "_", i, ".svg"), width=12)
}

# Plot only India and Pakistan side by side
countryXtime_augm_conflict_indiaPakistan<-countryXtime_augm_conflict[countryXtime_augm_conflict$Land_neu %in% c("Indien", "Pakistan"),]
conflict_export_red_indiaPakistan<-conflict_export_red[conflict_export_red$Land_neu %in% c("Indien", "Pakistan"),]

ggplot(countryXtime_augm_conflict_indiaPakistan, aes(x=Jahr_augm, y=value))+
  geom_segment(data=conflict_export_red_indiaPakistan, aes(x=start_date3, xend=ep_end_date, y=125000000, yend=125000000, col="darkgray"))+ #use start_date3, here, as a trick to show all the data!
  geom_bar(stat="identity") + 
  facet_wrap(~Land_neu)+
  scale_x_date(breaks=as.Date(c("2000-01-01","2017-12-31")),labels=c("2000", "2017"),
               limits = as.Date(c('2000-01-01','2017-12-31')))+
  scale_y_continuous(breaks=c(0, 50000000, 100000000), labels=c("0", "50000000", "100000000"))+
  theme_minimal()+
  theme(axis.text.x=element_text(family="GT America", color="#05032d", size=11),
        axis.text.y=element_text(family="GT America", color="#05032d", size=11),
        legend.position="none",
        axis.title.x=element_blank(),
        axis.title.y=element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.minor.y = element_blank())
ggsave("conflict_export_indienPakistan.svg", width=12)
ggsave("conflict_export_indienPakistan.pdf", width=12)

# Visualize each and every conflict for each of those countries
countries<-c("Vereinigte Arabische Emirate", "Saudi Arabien", "Indien", "Pakistan", "Russische Föderation", "Thailand", "Türkei", "Vereinigte Staaten")
for (i in countries){
  countryi_conflicti<-subset(conflict_export_red,conflict_export_red$Land_neu==i)
  ggplot(countryi_conflicti, aes(x=Jahr_augm))+
    geom_segment(data=countryi_conflicti, aes(x=start_date3, xend=ep_end_date, y=2, yend=2, col="darkgray"))+
    facet_wrap(~conflict_id, scales="free_y")+
    theme_minimal()+
    theme(axis.text.x=element_text(family="GT America", color="#05032d", size=11),
          axis.text.y=element_text(family="GT America", color="#05032d", size=11),
          legend.position="none",
          axis.title.x=element_blank(),
          axis.title.y=element_blank(),
          panel.grid.minor.x = element_blank(),
          panel.grid.minor.y = element_blank())
  ggsave(paste0("conflictXtime_cntry_selection", "_", i, ".png"), width=12)
}



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### VISUALIZE WHICH WEAPON TYPES WERE EXPORTED IN WHICH YEARS ###

# recategorize weapon types
export_restructured_recoded<-export_restructured
export_restructured_recoded$variable <-recode(export_restructured$variable, "KM1"="KM2") #waffen jeglichen kalibers, inkl Hand- und Faustfeuerwaffen
export_restructured_recoded$variable <-recode(export_restructured_recoded$variable, "KM4"="Andere") 
export_restructured_recoded$variable <-recode(export_restructured_recoded$variable, "KM7"="Andere")
export_restructured_recoded$variable <-recode(export_restructured_recoded$variable, "KM8"="Andere")
export_restructured_recoded$variable <-recode(export_restructured_recoded$variable, "KM16"="Andere")
summary(as.factor(export_restructured_recoded$variable))

export_restructured_recoded %>%
  group_by(variable)%>%
  summarize(value=sum(value))%>%
  arrange(value)

# Calculate proportions
cntryMaterial_prop <- export_restructured_recoded %>%
  group_by(Land, Jahr, variable) %>%
  summarize(value=sum(value)) %>%
  group_by(Land, Jahr) %>%
  mutate("sum" = sum(value)) %>%
  group_by(variable) %>%
  mutate("proportion"=100*value/sum)

countries<-c("Indien", "Saudi-Arabien", "Vereinigte Arabische Emirate", "Pakistan", "Russland", "Thailand", "Türkei", "USA")
weapondata_article<-cntryMaterial_prop %>% 
  select(Jahr, Land, variable, proportion)%>%
  spread(variable, proportion)%>%
  arrange(Land, Jahr) %>%
  select(Land, Jahr, KM2, KM3, KM6, KM10, KM5, Andere) %>%
  rename(`Waffen`=KM2, Munition=KM3, Panzer=KM6, Feuerleiteinrichtungen=KM5, Luftfahrzeuge=KM10)

# Plot for each country
for (i in countries){
  countryi<-subset(weapondata_article, weapondata_article$Land==i)
  ggplot(gather(countryi, key=variable, value=proportion, Waffen:Andere), aes(x=Jahr, y=proportion, group=variable, fill=variable))+
    geom_bar(stat="identity", width=.9)+
    scale_x_discrete(name="Jahr", breaks=c(2000,2017), labels=c("2000", "2017"), limits=c(2000, 2017))+
    theme_minimal()+
    ggsave(paste0("weaponXtime_cntry_selection", "_", i, ".svg"), width=12)
}

# Write the data, too
for (i in countries){
  countryi<-subset(weapondata_article, weapondata_article$Land==i)
  write.table(countryi, file=paste0("/Users/marie-jose/Documents/a_NZZ/projects/a_2018/waffenexporte/design/R-output/weapontXtime_8conflictCntries_", i, ".txt"), sep="\t", row.names=F, quote=F)
}

