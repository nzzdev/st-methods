#Lucien Baugmartner and Marie-José Kolly via NZZ Storytelling, September 2017
#Feedback welcome by e-mail marie-jose.kolly[at]nzz.ch or twitter [at]NZZStorytelling

#Articles presenting results: 
#https://nzz.ch/ld.1316249
#https://nzz.ch/ld.1316297
#https://nzz.ch/ld.1318290
#https://nzz.ch/ld.1318264
#https://nzz.ch/ld.1316942

################################################################################################################################################
### SETUP, SHAPEFILE, COLOR DEFINITIONS ###
################################################################################################################################################

rm(list=ls()) # clean env

# Source for shapefiles: https://www.bundeswahlleiter.de/bundestagswahlen/2017/wahlkreiseinteilung/downloads.html

# Download shape (version: utm32, generalisiert), unzip
#https://www.bundeswahlleiter.de/dam/jcr/02e21ebc-b1b4-43c0-8469-1cd47a97083e/btw17_geometrie_wahlkreise_shp.zip 

# Setup
library(rgdal) #if install.packages("rgdal") is not enough, install over shell with brew install gdal (possibly you have to install Homebrew first: $(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install))
library(ggplot2)
library(mapproj)
library(dplyr)
library(scales)
library(ggmap)
library(gridExtra)
library(svglite)
library(extrafont)

# Import your fonts
# font_import()

# Set the directory of your shapefile
setwd("mypath/data/shapefiles")

# Read shapefile, possibly adapt directory
wk<-readOGR("./btw17_geometrie_wahlkreise_shp/Geometrie_Wahlkreise_19DBT.shp") #utm32, generalisiert
summary(wk)
#maybe you need to run gpclibPermit() (and possibly library(gpclib))
wk_fort<-fortify(wk, region="WKR_NR") #converts to dataframe so ggplot can deal with it

# Define cities to plot on the maps
cities<-data.frame("city"=c("Berlin", "München", "Hamburg", "Köln"), "lon"=c(792094, 692094, 565833, 356688), "lat"=c(5820073, 5334543, 5934036, 5644859))

# Define color scheme for each party
colSPDSozial<-c("#F4D7D3","#EAAEA8","#DF857B","#D3574A","#C31906")
colCDUUnion<-c("#C7C7C7","#939393","#626262","#353535","#0A0A0A")
colFDPFreieDem<-c("#F6F5D0","#EDECA0","#E4E16D","#DBD738","#D1CC00")
colGRÜNE<-c("#E0EDD3","#C2DBA7","#A4CA7B","#85B84F","#66A622")
colAlternativeAfD<-c("#CEE7F4","#9ED0E9","#6CB8DE","#389FD3","#0084C7")
colLINKE<-c("#E5D8EC","#CDB1D9","#B58CC7","#9C66B5","#8440A3")

colorFrame<-data.frame(colCDUUnion, colSPDSozial, colLINKE, colGRÜNE, colFDPFreieDem, colAlternativeAfD)

# Define diverging color scheme for deviations relative to previous election (same for all parties) 
colDiv<-c("#3e9396","#56a0a3","#6eaeb0","#86bbbd","#9ec9ca","#eab298","#e59f7e","#e08c65","#db794b","#d66632") #from win to loss

# Define color for NA-values
colNA<-"#C9C8BA"



################################################################################################################################################
### LOAD AND CLEAN DATA ###
################################################################################################################################################

## Read and clean the data

# function for cleaning our messy character strings
jam <- function(x) gsub("Ÿ", "ü", x) %>% 
  gsub("š", "ö", .) %>% 
  gsub("Š", "ä", .) %>% 
  gsub("Ð", "-", .) %>%
  gsub("§", "ss", .) %>%
  gsub("–", "-", .) %>%
  gsub("ß", "ss", .) %>%
  gsub("†", "Ü", .) %>%
  gsub("Ÿ", "ü", .) %>%
  gsub("€", "Ä", .) %>%
  gsub(" ", "",.)

# data source: https://www.bundeswahlleiter.de/bundestagswahlen/2017/strukturdaten.html
# File: "kerg_VVVVV.csv" ; VVVVV ascending Version 
butter <- read.csv("mypath/data/kerg.csv", sep=";", header=F, stringsAsFactors = F) # load data

# rename the variables
name.vec <- c() # create empty vector

# replicate the category of the columns-sets (party names) for every column in every set (4col=1set)
for (i in seq(from=4, to=length(butter)-1, by=4)) butter[3,c(i+1:3)] <- butter[3,i] # -1 because there is an empty column at the end, i.e. each row of the .csv ends with a ;
butter[4,seq(from=5, to=length(butter), by=4)] <- "Erststimmen" # define the sub-category (Erststimmen) for every column in every set
butter[4,seq(from=7, to=length(butter), by=4)] <- "Zweitstimmen" # define the sub-category (Zweitstimmen) for every column in every set

# # create a vector with unique columnnames: combination of category[party] * subcategory[Erst- | Zweitstimmen] * period[current=Endgültig | last=Vorperiode]
for (i in 1:length(butter)) name.vec[i] <- gsub(" ", "", paste(butter[3:5, i], collapse ="")) 
butter <- butter[-c(1:5),] # get rid of the messy header

colnames(butter) <- c("wk_nr", "name", "land", name.vec[4:length(name.vec)]) # set the columnnames we just created

# delete all rows and columns with no information
butter <- butter[- which(butter$wk_nr==""),]
butter <- butter[,-c(length(butter))]

# tidy up `land` and `name` (function was defined above) and colnames
butter$land <- jam(butter$land)
butter$name <- jam(butter$name)
colnames(butter) <- jam(colnames(butter))

# make all numerical variables numeric (for the map, Wkr-Nr. is NOT numeric)
str(butter) #verify that all variables are character variables (chr). if not, transform to character before transforming to numeric
butter[,c(1,3:length(butter))] <- sapply(butter[,c(1,3:length(butter))], as.numeric)

# we need to adjust the Länder-names:
# load("BTW_Indikatoren_2017.Rdata") 
butter <- butter %>% filter(!(land==99))# paste the names of the corresponding indicator data
butter <- butter[order(butter$wk_nr),] # order the data according to the `wk_nr`

# merge CDU and CSU
cdu.vec <- grep("ChristlichDemo", colnames(butter))
csu.vec <- grep("Christlich-Soz", colnames(butter))

#check which rows have CSU instead of CDU: 
which(is.na(butter[,cdu.vec[1]])) #Berlin-Ost and Berlin-West are still here, will be gotten rid of later
which(!is.na(butter[,csu.vec[1]]))

#add CSU and CDU to Union
for (i in 1:4) butter[212:257,cdu.vec[i]] <- butter[212:257,csu.vec[i]]#possibly verify, here, that in the new datafile these are the same... which(data13$land=="BY") should be equal to which(data13$CDUErststimmen==0) should be equal to which(data13$CSUErststimmen!=0)

colnames(butter) <- gsub("ChristlichDemokratischeUnionDeutschlands", "Union", colnames(butter))
butter <- select(butter, select=-grep("Christlich-Soz", colnames(butter)))

# DONE
butter
str(butter)




########################################################################################################
####################################### 3. SUBSETTING ##################################################
########################################################################################################

# get rid of "Berlin-West" and "Berlin-Ost" (no matching indicators)
butter.sub <- butter%>%filter(!name%in%c("Berlin-West", "Berlin-Ost"))

# for plot analysis it is easier to work with data frames; coerce:
butter <- as.data.frame(butter)

# we only concentrate on Wahlkreise, we don't need the numbers for Länder or Deutschland (wk_nr<900)
butter.sub <- filter(butter, !wk_nr>900)

## Calculate vote shares for each party
# we create vectors containing all columnnames for Zweitstimmen, and Erststimmen | Vorperiode = 2013, Vorläufig = 2017

### CAREFUL: VORLÄUFIG MAY HAVE TO BE REPLACED BY ZWISCHENERGEBNIS OR ENDGÜLTIG, DEPENDING ON DOCUMENT STATUS

zweitstimmen13.vec <- grep("Zweitstimmen",colnames(butter.sub), value=TRUE)[-c(1:8)] %>% grep("Vorperiode", ., value=TRUE)
erststimmen13.vec <- grep("Erststimmen",colnames(butter.sub), value=TRUE)[-c(1:8)] %>% grep("Vorperiode", ., value=TRUE)

zweitstimmen17.vec <- grep("Zweitstimmen",colnames(butter.sub), value=TRUE)[-c(1:8)] %>% grep("Vorläufig", ., value=TRUE)
erststimmen17.vec <- grep("Erststimmen",colnames(butter.sub), value=TRUE)[-c(1:8)] %>% grep("Vorläufig", ., value=TRUE)

butter13.sub <- butter.sub[,c(1:3, grep("Vorperiode",colnames(butter.sub)))]
butter17.sub <- butter.sub[,c(1:3, grep("Vorläufig",colnames(butter.sub)))]

# now we loop: every number of Zweitstimmen for every party in a Wahlkreis will be divided by the total number of VALID votes in a Wahlkreis (creates the percentages); same for Erststimmen
for (i in zweitstimmen13.vec) butter13.sub[,i] <- (butter13.sub[,i]/butter13.sub$GültigeZweitstimmenVorperiode)*100
for (i in erststimmen13.vec) butter13.sub[,i] <- (butter13.sub[,i]/butter13.sub$GültigeErststimmenVorperiode)*100

for (i in zweitstimmen17.vec) butter17.sub[,i] <- (butter17.sub[,i]/butter17.sub$GültigeZweitstimmenVorläufig)*100
for (i in erststimmen17.vec) butter17.sub[,i] <- (butter17.sub[,i]/butter17.sub$GültigeErststimmenVorläufig)*100

# check whether the rowsums are all 100 (==the total % of votes in a Wahlkreis is 100)
rowSums(butter13.sub[,grep("Zweitstimmen",colnames(butter13.sub))][-c(1:4)], na.rm=TRUE)
rowSums(butter13.sub[,grep("Erststimmen",colnames(butter13.sub))][-c(1:4)], na.rm=TRUE)

rowSums(butter17.sub[,grep("Zweitstimmen",colnames(butter17.sub))][-c(1:4)], na.rm=TRUE)
rowSums(butter17.sub[,grep("Erststimmen",colnames(butter17.sub))][-c(1:4)], na.rm=TRUE)

# create subsets with only Erststimmen- and Zweitstimmen-variables
zweitstimmen13 <- butter13.sub[,grep("Zweitstimmen", colnames(butter13.sub), value=TRUE)[-c(1:2)]] # selects only columns containing "Zweitstimmen" in their name
zweitstimmen17 <- butter17.sub[,grep("Zweitstimmen", colnames(butter17.sub), value=TRUE)[-c(1:2)]] # selects only columns containing "Zweitstimmen" in their name

# the we further select only those columns containing any of the big parties in their name
zweitstimmen13.gross <- zweitstimmen13[grep(paste(c("CDU", "CSU", "SPD", "FDP", "LINKE", "GRÜNE", "AfD",
                                                    "Union", "SozialdemokratischePartei", "FreieDemokratische",
                                                    "DIELINKE", "DIEGRÜNEN", 
                                                    "Alternative"), collapse="|"), colnames(zweitstimmen13), value=TRUE)] 
zweitstimmen17.gross <- zweitstimmen17[grep(paste(c("CDU", "CSU", "SPD", "FDP", "LINKE", "GRÜNE", "AfD",
                                                    "Union", "SozialdemokratischePartei", "FreieDemokratische",
                                                    "DIELINKE", "DIEGRÜNEN", 
                                                    "Alternative"), collapse="|"), colnames(zweitstimmen17), value=TRUE)] 

# repeat for erststimmen
erststimmen13 <- butter13.sub[,grep("Erststimmen", colnames(butter13.sub), value=TRUE)[-c(1:2)]]
erststimmen17 <- butter17.sub[,grep("Erststimmen", colnames(butter17.sub), value=TRUE)[-c(1:2)]]

erststimmen13.gross <- erststimmen13[grep(paste(c("CDU", "CSU", "SPD", "FDP", "LINKE", "GRÜNE", "AfD",
                                                  "Union", "SozialdemokratischePartei", "FreieDemokratische",
                                                  "DIELINKE", "DIEGRÜNEN",
                                                  "Alternative"), collapse="|"), colnames(erststimmen13), value=TRUE)] 
erststimmen17.gross <- erststimmen17[grep(paste(c("CDU", "CSU", "SPD", "FDP", "LINKE", "GRÜNE", "AfD",
                                                  "Union", "SozialdemokratischePartei", "FreieDemokratische",
                                                  "DIELINKE", "DIEGRÜNEN",
                                                  "Alternative"), collapse="|"), colnames(erststimmen17), value=TRUE)] 


#add wk-info to these dataframes
zweitstimmen13.gross<-cbind("wk_nr"=butter.sub$wk_nr, "name"=butter.sub$name, zweitstimmen13.gross)
erststimmen13.gross<-cbind("wk_nr"=butter.sub$wk_nr, "name"=butter.sub$name, erststimmen13.gross)

zweitstimmen17.gross<-cbind("wk_nr"=butter.sub$wk_nr, "name"=butter.sub$name, zweitstimmen17.gross)
erststimmen17.gross<-cbind("wk_nr"=butter.sub$wk_nr, "name"=butter.sub$name, erststimmen17.gross)

head(erststimmen13.gross) # check 
head(erststimmen17.gross)
head(zweitstimmen13.gross) 
head(zweitstimmen17.gross)

# check whether the rows (Wahlkreise) match between basemap and vote data
which((wk$WKR_NR == erststimmen17.gross$wk_nr) != TRUE)

# calculate vote turnout
voteTurnout17<-(butter17.sub$WählerZweitstimmenVorläufig/butter17.sub$WahlberechtigteZweitstimmenVorläufig)*100
voteTurnout13<-(butter13.sub$WählerZweitstimmenVorperiode/butter13.sub$WahlberechtigteZweitstimmenVorperiode)*100



