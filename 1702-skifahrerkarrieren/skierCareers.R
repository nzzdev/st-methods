#NZZ Storytelling, January 2017: How we scraped the FIS database in order to visualize and categorize skiers' careers
#Feedback welcome by e-mail marie-jose.kolly[at]nzz.ch or twitter [at]mjkolly

#Main article presenting results: http://nzz.ch/ld.139656
#Article that describes our methods: http://nzz.ch/ld.142634


library(rvest)
library(directlabels)
library(ggplot2)

### FIRST DEFINE THE SAMPLE. WE WANT ALL SKIERS WHO GOT INTO THE TOP 10 OF THE FINAL WORLD CUP RANKING IN AT LEAST ONE YEAR SINCE 1967 (50 YEARS) ###

##loop over season, keep Cup=World Cup (WC), sort by ALL (Overall), leave Nation empty

#males
male_wc1967_2016<-data.frame()
for(year in 1967:2016){
  raceTypes<-list()
  skiers<-data.frame()
  page<-read_html(paste0("http://data.fis-ski.com/alpine-skiing/cup-standings.html?suchen=true&export_standing=&suchcompetitorid=&suchseason=",year,"&suchgender=M&suchnation=&sector=AL&suchcup=WC&discipline=ALL&search=Search", sep=""))
  #count race types to determine number of cols
  racesi<-page %>% 
    html_nodes("th") %>%
    html_text()
  ncols<-length(racesi)+(length(racesi)-2)+1
  #get race types for every year
  #raceTypes[[i]]<-racesi
  #get world cup skiers' ranking for every year
  skiers<-page %>% 
    html_nodes("td") %>%
    html_text()
  for(i in 1:length(skiers)){skiers[i]<-gsub("\\s*","",skiers[i])} #replace space by empty
  mat<-matrix(unlist(skiers), ncol=ncols, byrow=TRUE)
  colnames(mat)<-mat[1,]
  ifelse(length(colnames(mat))==11, colnames(mat)<-c("ditch", "name", "nation", 
                                                     paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                     paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                     paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                     paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep="")), 
         ifelse(length(colnames(mat))==13, colnames(mat)<-c("ditch", "name", "nation", 
                                                            paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                            paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                            paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                            paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep=""),
                                                            paste0("rank",racesi[7],sep=""), paste0("pts",racesi[7],sep="")),
                ifelse(length(colnames(mat))==15, colnames(mat)<-c("ditch", "name", "nation", 
                                                                   paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                                   paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                                   paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                                   paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep=""),
                                                                   paste0("rank",racesi[7],sep=""), paste0("pts",racesi[7],sep=""),
                                                                   paste0("rank",racesi[8],sep=""), paste0("pts",racesi[8],sep="")),
                       ifelse(length(colnames(mat))==17, colnames(mat)<-c("ditch", "name", "nation", 
                                                                          paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                                          paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                                          paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                                          paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep=""),
                                                                          paste0("rank",racesi[7],sep=""), paste0("pts",racesi[7],sep=""),
                                                                          paste0("rank",racesi[8],sep=""), paste0("pts",racesi[8],sep=""),
                                                                          paste0("rank",racesi[9],sep=""), paste0("pts",racesi[9],sep="")), colnames(mat)<-mat[1,]))))
  mat_red<-mat[-1,-1]
  dat<-as.data.frame(mat_red, stringsAsFactors=FALSE, col.names=mat[1,])
  dat_red <- dat[-nrow(dat),]
  wcyear<-rep(year, nrow(dat_red))
  dat_year<-cbind(year, dat_red)
  mypath <- file.path("path",paste0("male_worldCup",year,".txt", sep = ""))
  write.table(dat_year, mypath, row.names=FALSE, quote=FALSE, sep="\t")
  male_wc1967_2016<-rbind(male_wc1967_2016, dat_year[,1:5])
}

#females
female_wc1967_2016<-data.frame()
for(year in 1967:2016){
  raceTypes<-list()
  skiers<-data.frame()
  page<-read_html(paste0("http://data.fis-ski.com/alpine-skiing/cup-standings.html?suchen=true&export_standing=&suchcompetitorid=&suchseason=",year,"&suchgender=L&suchnation=&sector=AL&suchcup=WC&discipline=ALL&search=Search", sep=""))
  #count race types to determine number of cols
  racesi<-page %>% 
    html_nodes("th") %>%
    html_text()
  ncols<-length(racesi)+(length(racesi)-2)+1
  #get race types for every year
  #raceTypes[[i]]<-racesi
  #get world cup skiers' ranking for every year
  skiers<-page %>% 
    html_nodes("td") %>%
    html_text()
  for(i in 1:length(skiers)){skiers[i]<-gsub("\\s*","",skiers[i])} #replace space by empty
  mat<-matrix(unlist(skiers), ncol=ncols, byrow=TRUE)
  colnames(mat)<-mat[1,]
  ifelse(length(colnames(mat))==11, colnames(mat)<-c("ditch", "name", "nation", 
                                                     paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                     paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                     paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                     paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep="")), 
         ifelse(length(colnames(mat))==13, colnames(mat)<-c("ditch", "name", "nation", 
                                                            paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                            paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                            paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                            paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep=""),
                                                            paste0("rank",racesi[7],sep=""), paste0("pts",racesi[7],sep="")),
                ifelse(length(colnames(mat))==15, colnames(mat)<-c("ditch", "name", "nation", 
                                                                   paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                                   paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                                   paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                                   paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep=""),
                                                                   paste0("rank",racesi[7],sep=""), paste0("pts",racesi[7],sep=""),
                                                                   paste0("rank",racesi[8],sep=""), paste0("pts",racesi[8],sep="")),
                       ifelse(length(colnames(mat))==17, colnames(mat)<-c("ditch", "name", "nation", 
                                                                          paste0("rank",racesi[3],sep=""), paste0("pts",racesi[3],sep=""), 
                                                                          paste0("rank",racesi[4],sep=""), paste0("pts",racesi[4],sep=""),
                                                                          paste0("rank",racesi[5],sep=""), paste0("pts",racesi[5],sep=""),
                                                                          paste0("rank",racesi[6],sep=""), paste0("pts",racesi[6],sep=""),
                                                                          paste0("rank",racesi[7],sep=""), paste0("pts",racesi[7],sep=""),
                                                                          paste0("rank",racesi[8],sep=""), paste0("pts",racesi[8],sep=""),
                                                                          paste0("rank",racesi[9],sep=""), paste0("pts",racesi[9],sep="")), colnames(mat)<-mat[1,]))))
  mat_red<-mat[-1,-1]
  dat<-as.data.frame(mat_red, stringsAsFactors=FALSE, col.names=mat[1,])
  dat_red <- dat[-nrow(dat),]
  wcyear<-rep(year, nrow(dat_red))
  dat_year<-cbind(year, dat_red)
  mypath <- file.path("path",paste0("female_worldCup",year,".txt", sep = ""))
  write.table(dat_year, mypath, row.names=FALSE, quote=FALSE, sep="\t")
  female_wc1967_2016<-rbind(female_wc1967_2016, dat_year[,1:5])
}

#transform variables to factors / numeric
male_wc1967_2016$name<-as.factor(male_wc1967_2016$name)
male_wc1967_2016$nation<-as.factor(male_wc1967_2016$nation)
male_wc1967_2016$rankALL<-as.numeric(male_wc1967_2016$rankALL)
male_wc1967_2016$ptsALL<-as.numeric(male_wc1967_2016$ptsALL)

female_wc1967_2016$name<-as.factor(female_wc1967_2016$name)
female_wc1967_2016$nation<-as.factor(female_wc1967_2016$nation)
female_wc1967_2016$rankALL<-as.numeric(female_wc1967_2016$rankALL)
female_wc1967_2016$ptsALL<-as.numeric(female_wc1967_2016$ptsALL)

#subset data to top 10 of every season
female_top10<-subset(female_wc1967_2016, female_wc1967_2016$rankALL<11)
female_top10_unique<-paste(unique(female_top10$name))
fem<-rep("f", length(female_top10_unique))
female_top10_nation<-female_top10$nation[match(female_top10_unique, female_top10$name)]

male_top10<-subset(male_wc1967_2016, male_wc1967_2016$rankALL<11)
male_top10_unique<-paste(unique(male_top10$name))
masc<-rep("m", length(male_top10_unique))
male_top10_nation<-male_top10$nation[match(male_top10_unique, male_top10$name)]

top10<-rbind(cbind(male_top10_unique, as.character(male_top10_nation), masc), cbind(female_top10_unique, as.character(female_top10_nation), fem))
colnames(top10)<-c("skier", "nation", "gender")


### NOW SCRAPE ENTIRE CAREER FOR EVERY ONE OF THE ATHLETES IN OUR SAMPLE ###

## Get the FIS codes of all athletes
#loop gets the number of html pages to loop through. on the last page, there'll be no "next" link to the next 100 results
skiersCodesAll<-data.frame()
start<-0
repeat{
  website_codes<-read_html(paste0("https://data.fis-ski.com/global-links/search-a-athlete.html?sector=AL&rec_start=", start,  "&limit=100", sep=""))
  skiersCodes<-website_codes %>% html_nodes("td") %>% html_text()
  skiersCodesSelect<-skiersCodes[1:900]
  for(i in 1:length(skiersCodesSelect)){skiersCodesSelect[i]<-gsub("\\s*","",skiersCodesSelect[i])} #replace space by empty
  mat<-matrix(unlist(skiersCodesSelect), ncol=9, byrow=TRUE)
  mat_select<-mat[,2:9]
  dat<-as.data.frame(mat_select, stringsAsFactors=FALSE)
  colnames(dat)<-c("status", "FIScode", "competitor", "gender", "birthdate", "sector", "nation", "skiClub")
  skiersCodesAll<-rbind(skiersCodesAll, dat)
  start<-start+100
  #stop as soon as the "next" link to the next page does not appear on the page anymore - this is our last page
  if("TRUE" %in% grepl("Next", website_codes %>% html_nodes(".calendar_next_prev_wrapper a") %>% html_text())==F){
    break
  }
}

skiersCodesAll$status<-as.factor(skiersCodesAll$status)
skiersCodesAll$FIScode<-as.factor(skiersCodesAll$FIScode)
skiersCodesAll$competitor<-as.factor(skiersCodesAll$competitor)
skiersCodesAll$gender<-as.factor(skiersCodesAll$gender)
skiersCodesAll$birthdate<-as.factor(skiersCodesAll$birthdate)
skiersCodesAll$sector<-as.factor(skiersCodesAll$sector)
skiersCodesAll$nation<-as.factor(skiersCodesAll$nation)
skiersCodesAll$skiClub<-as.factor(skiersCodesAll$skiClub)

#now match the top10 with the FIS codes
top10dat<-as.data.frame(top10)

top10codes<-data.frame(top10dat$skier, top10dat$gender, top10dat$nation, skiersCodesAll$FIScode[match(top10dat$skier, skiersCodesAll$competitor)], skiersCodesAll$status[match(top10dat$skier, skiersCodesAll$competitor)], skiersCodesAll$birthdate[match(top10dat$skier, skiersCodesAll$competitor)])
colnames(top10codes)<-c("skier", "gender", "origin", "FIScode", "status", "birthdate")
top10codes$status<-as.character(top10codes$status)
top10codes$status<-ifelse(nchar(top10codes$status)==0, "nonActive", top10codes$status)

#Tamara Mc Kinney is in the database twice (535150) is empty --> (-10879) produces results. replace.
match("MCKINNEYTamara", top10codes$skier)
top10codes[213,4]<-"-10879"


####----------------------------------------------------------------------------------------------------------------------------------
####START HERE TO UPDATE THE DATA WITH NEW RACES####

##Now top10codes[,4] as to get all skiers' career data
#loop through all fis codes - takes some time
skiersCareer<-data.frame()
for (code in top10codes[,4]){ #the FIS-codes
  start<-0
  careerX<-data.frame()
  repeat{
    website<-read_html(paste0("http://data.fis-ski.com/dynamic/athlete-biography.html?sector=AL&fiscode=", code, "&rec_start=", start, "&limit=100", sep=""))
    careerPage<-website %>% html_nodes("td") %>% html_text()
    cutoff<-grep("[0-9]{2}[-][0-9]{2}[-][0-9]", careerPage)[1] #captures the first "real" table entry which is a date in the format dd-mm-yyyy
    if(is.na(cutoff)){
      break
    }
    careerPage_clean<-careerPage[cutoff:length(careerPage)] #oder mit grep/regex ein pattern suchen, das dem ersten eintrag=datum+leerzeichen entspricht, von diesem vektoreintrag her auswählen
    for(i in 1:length(careerPage_clean)){careerPage_clean[i]<-gsub("\\s*","",careerPage_clean[i])} #replace space by empty
    for(i in 1:length(careerPage_clean)){careerPage_clean[i]<-gsub("^$",NA,careerPage_clean[i])} # replace empty by NA
    mat<-matrix(unlist(careerPage_clean), ncol=8, byrow=T)
    mat_red<-mat[,-8]
    dat<-data.frame(matrix(mat_red, ncol=7))
    dat_augm<-cbind(dat, rep(code, nrow(dat)), rep(top10codes$skier[match(code, top10codes$FIScode)],nrow(dat)), rep(top10codes$gender[match(code, top10codes$FIScode)],nrow(dat)), rep(top10codes$status[match(code, top10codes$FIScode)],nrow(dat)), rep(top10codes$origin[match(code, top10codes$FIScode)],nrow(dat)), rep(top10codes$birthdate[match(code, top10codes$FIScode)],nrow(dat))) #add skiers' code, name, gender and origin to the dataframe with his/her results
    careerX<-rbind(careerX, dat_augm)
    start<-start+100
    #stop as soon as the "next" link to the next page does not appear on the page anymore - this is our last page
    if("TRUE" %in% grepl("Next", website %>% html_nodes(".calendar_next_prev_wrapper a") %>% html_text())==F){
      break
    }
  }
  skiersCareer<-rbind(skiersCareer, careerX)
}
colnames(skiersCareer)<-c("raceDate", "place", "nation", "category", "discipline", "position", "FISpoints", "FIScode", "skier", "gender", "status", "origin", "birthdate")

#transform variables and drop unused levels
skiersCareer$raceDate<-droplevels(skiersCareer$raceDate)
skiersCareer$raceDate<-as.Date(skiersCareer$raceDate, format="%d-%m-%Y")#convert to proper R date format
skiersCareer$place<-droplevels(skiersCareer$place)
skiersCareer$nation<-droplevels(skiersCareer$nation)
skiersCareer$category<-droplevels(skiersCareer$category)
skiersCareer$discipline<-droplevels(skiersCareer$discipline)
skiersCareer$position<-droplevels(skiersCareer$position)
skiersCareer$FISpoints<-droplevels(skiersCareer$FISpoints)
skiersCareer$FISpoints<-as.numeric(skiersCareer$FISpoints)
skiersCareer$FIScode<-droplevels(skiersCareer$FIScode)
skiersCareer$skier<-droplevels(skiersCareer$skier)
skiersCareer$birthdate<-as.Date(skiersCareer$birthdate, format="%d-%m-%Y")#convert to proper R date format

###transform and augment some more:

#throw out races that are not either in FISWorldCup, FISWorldSkiChampionships or OlympicWinterGames
skiersCareer_WCWMOS<-subset(skiersCareer, skiersCareer$category=="FISWorldCup" | skiersCareer$category=="FISWorldSkiChampionships" | skiersCareer$category=="OlympicWinterGames")

#find NAs such that we can check they're really not podium or DSQ-something positions
isna<-subset(skiersCareer_WCWMOS, is.na(skiersCareer_WCWMOS$position)==T)

#in one case (out of 14), isna actually produced an athlete that had position==NA but that had a podium: Gertrude Gabl, 03.01.1969, Oberstaufen (for Olga Pall there is the entry "2")
skiersCareer_WCWMOS[22208,6]<-2

#throw out races where athlete did not start (but keep those where disqualified or did not end, NAs etc.
skiersCareer_skiedRaces<-subset(skiersCareer_WCWMOS, skiersCareer_WCWMOS$position!="DNS"&skiersCareer_WCWMOS$position!="DNS1") #get rid of DNS, DNS1

#drop unused levels
skiersCareer_skiedRaces$position<-droplevels(skiersCareer_skiedRaces$position)
skiersCareer_skiedRaces$category<-droplevels(skiersCareer_skiedRaces$category)
skiersCareer_skiedRaces$place<-droplevels(skiersCareer_skiedRaces$place)
skiersCareer_skiedRaces$nation<-droplevels(skiersCareer_skiedRaces$nation)
skiersCareer_skiedRaces$discipline<-droplevels(skiersCareer_skiedRaces$discipline)
skiersCareer_skiedRaces$FIScode<-droplevels(skiersCareer_skiedRaces$FIScode)
skiersCareer_skiedRaces$skier<-droplevels(skiersCareer_skiedRaces$skier)

#order by increasing date
skiersCareer_skiedRaces_ord<-skiersCareer_skiedRaces[order(skiersCareer_skiedRaces$raceDate, decreasing=F),]

#since position needs to stay a factor (DNF etc.), take =="1" and ="1" or "2" or "3" for the victory/podium columns (define victory as 1=1, rest=0) (define podium as 1:3=1, rest=0)
skiersCareer_augm<-cbind(skiersCareer_skiedRaces_ord, "victory"=skiersCareer_skiedRaces_ord$position, "podium"=skiersCareer_skiedRaces_ord$position)
skiersCareer_augm$victory<-as.character(skiersCareer_augm$victory) 
skiersCareer_augm$victory[skiersCareer_augm$victory=="1"]<-"1"
skiersCareer_augm$victory[skiersCareer_augm$victory!="1"]<-"0"
skiersCareer_augm$victory<-as.factor(skiersCareer_augm$victory)

skiersCareer_augm$podium<-as.character(skiersCareer_augm$podium)
skiersCareer_augm$podium[skiersCareer_augm$podium=="1"]<-"1"
skiersCareer_augm$podium[skiersCareer_augm$podium=="2"]<-"1"
skiersCareer_augm$podium[skiersCareer_augm$podium=="3"]<-"1"
skiersCareer_augm$podium[skiersCareer_augm$podium!="1"&skiersCareer_augm$podium!="2"&skiersCareer_augm$podium!="3"]<-"0"
skiersCareer_augm$podium<-as.factor(skiersCareer_augm$podium)

#cumulative victories / podiums from career start on
skiersCareer_augm$podium<-as.numeric(as.character(skiersCareer_augm$podium))
skiersCareer_augm$victory<-as.numeric(as.character(skiersCareer_augm$victory))

skiersCareer_cumSums<-data.frame()
for (athlete in unique(skiersCareer_augm$FIScode)){
  skierX<-subset(skiersCareer_augm, skiersCareer_augm$FIScode==athlete)
  skierX_ord<-skierX[order(skierX$raceDate, decreasing=F),]
  skierX_races<-cbind(skierX_ord, "raceN"=c(1:nrow(skierX_ord)))
  skierX_cum_v<-within(skierX_races, victoryCum<-cumsum(victory))
  skierX_cum_vp<-within(skierX_cum_v, podiumCum<-cumsum(podium))
  skierX_cum_vperc<-within(skierX_cum_vp, victoryCumPerc<-100*(victoryCum/raceN))
  skierX_cum_vpperc<-within(skierX_cum_vperc, podiumCumPerc<-100*(podiumCum/raceN))
  skiersCareer_cumSums<-rbind(skiersCareer_cumSums, skierX_cum_vpperc)
}


###transform skier name to printable form
# split before last uppercase letter (followed by lowercase)
skiersCareer_clean<-skiersCareer_cumSums
skiersCareer_clean$skier<-gsub("([A-Z])([A-Z][a-z])", "\\1SPLITHERE\\2", skiersCareer_clean$skier)
skiersCareer_clean$skier<-sub("SPLITHERE", " ", skiersCareer_clean$skier)
#transform last name to lower case and change order to firstname > lastname
for (i in 1:length(skiersCareer_clean$skier)){
  if(grepl(" ", skiersCareer_clean$skier[i]) == T){
    skiersCareer_clean$skier[i]<-paste0(strsplit(as.character(skiersCareer_clean$skier)[[i]], " ")[1][[1]][[2]], " ", toupper(substr(strsplit(as.character(skiersCareer_clean$skier)[[i]], " ")[1][[1]][[1]],1,1)), tolower(substr(strsplit(as.character(skiersCareer_clean$skier)[[i]], " ")[1][[1]][[1]],2,30)), sep="")
  }
}
#now also split the cases where there are two first names and where a second last name follows a hyphen
skiersCareer_clean$skier<-sub("([a-z])([A-Z])", "\\1SPLITHERE\\2", skiersCareer_clean$skier)
skiersCareer_clean$skier<-sub("SPLITHERE", " ", skiersCareer_clean$skier)
skiersCareer_clean$skier<-sub("(-)([a-z])", "\\1\\U\\2", skiersCareer_clean$skie, perl=T)
#and, finally, fix the case where an acronym stands for the first name(s)
skiersCareer_clean$skier<-sub("KITTAJ", "AJ Kitt", skiersCareer_clean$skier)
skiersCareer_clean$skier<-sub("Tamara Mckinney", "Tamara McKinney", skiersCareer_clean$skier)
#and, very finally, fix the umlauts, accents etc.
twoGraphs<-c("Gustavo", "Defago", "Proell", "Goetschl", "Paerson", "Huetter", "Goergl", "Guenther", "Thoeni", "Baehler", "Noel", "Joel", "Hoelzl", 
             "Kroell", "Moelgg", "Buechel", "Hoefl", "Pietilae", "Kueng", "Mueller", "Schoenfelder", "Haeusl", "Haechergavet", 
             "Kaelin", "Kjoerstad", "Loeseth", "Perillat", "Leo Lacroix", "Andre ", "Skaardal", "Fernandez", "Farbinger", 
             "Danielle", "Haaker", "Francoise", "Huega", "Marie-Therese", "Vongruenigen", "Dechiesa", "Peter I Wirnsberger", "Fogdoe")
umlaut<-c("Gustav", "Défago", "Pröll", "Götschl", "Pärson", "Hütter", "Görgl", "Günther", "Thöni", "Bähler", "Noël", "Joël", "Hölzl", 
          "Kröll", "Mölgg", "Büchel", "Höfl", "Pietilä", "Küng", "Müller", "Schönfelder", "Häusl", "Hächer-Gavet", 
          "Kälin", "Kjörstad", "Loeseth", "Périllat", "Léo Lacroix", "André ", "Skardal", "Fernández", "Färbinger", 
          "Danièle", "Haker", "Françoise", "Heuga", "Marie-Theres", "von Grünigen", "De Chiesa", "Peter Wirnsberger", "Fogdö")
for(i in 1:length(twoGraphs)) {skiersCareer_clean$skier <- sub(twoGraphs[i], umlaut[i], skiersCareer_clean$skier)}

#Set Aamodt, Défago, Raich, Kathrin Zettel, Nicole Hosp, Tina Maze, Ivica Kostelic to non-active
skierToInactive<-c("Kjetil André Aamodt", "Didier Défago", "Benjamin Raich", "Kathrin Zettel", "Nicole Hosp", "Tina Maze", "Ivica Kostelic")
for(i in 1:nrow(skiersCareer_clean)){
  ifelse(skiersCareer_clean$skier[i] %in% skierToInactive, skiersCareer_clean$status[i]<-"nonActive", skiersCareer_clean$status[i])
}

#re-transform to factor
skiersCareer_clean$skier<-as.factor(skiersCareer_clean$skier)


#----------------------------------------------------------------------------------------------------------------------------------
###ANALYSIS
setwd("mypath")

##principal graph: podium per date (as non-podium races are not always in the FIS database)

#podium X date
ggplot(skiersCareer_clean, aes(raceDate, podiumCum, color=skier)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("2005-01-01"), as.Date("2030-12-31"))) +
  #scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-12-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("dateXpodiumCum_abs.pdf", plot = last_plot())

##active vs non-active athletes

#podium X date
ggplot(skiersCareer_clean, aes(x=raceDate, y=podiumCum, group=factor(skier), color=status)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-12-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("status_dateXpodiumCum_abs.pdf", plot = last_plot())


#look at athletes from specific country/-ies
countries<-c("SUI")

countriesSet<-data.frame()
for (i in countries){
  countryi<-subset(skiersCareer_clean, skiersCareer_clean$origin==i)
  countriesSet<-rbind(countriesSet, countryi)
}

ggplot(countriesSet, aes(x=raceDate, y=podiumCum, color=skier)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-01-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("swiss_dateXpodiumCum_abs.pdf", plot = last_plot())




## find career shapes: fast or slow starters? early or late stoppers?
#therefore check if the second third of a skiers' career is steeper than the first and if the third is flatter than the second

#length in days and shape in steepness of careers
careerLengthShape<-data.frame()
for (i in unique(skiersCareer_clean$skier)){
  skieri<-subset(skiersCareer_clean, skiersCareer_clean$skier==i)
  careerLengthi_races<-max(skieri$raceN)
  oneThird<-floor(max(skieri$raceN/3))
  careerThird1<-subset(skieri, skieri$raceN<=oneThird)
  careerThird1_length<-as.numeric(nrow(careerThird1))
  careerThird2<-subset(skieri, skieri$raceN>max(careerThird1$raceN) & skieri$raceN<=(max(careerThird1$raceN) + oneThird))
  careerThird2_length<-as.numeric(nrow(careerThird2))
  careerThird3<-subset(skieri, skieri$raceN>max(careerThird2$raceN))
  careerThird3_length<-as.numeric(nrow(careerThird3))
  careerSteepness1<-careerThird1$podiumCum[nrow(careerThird1)]/nrow(careerThird1)
  careerSteepness2<-careerThird2$podiumCum[nrow(careerThird2)]/nrow(careerThird2)
  careerSteepness3<-careerThird3$podiumCum[nrow(careerThird3)]/nrow(careerThird3)
  quotientSteepness3_2<-careerSteepness3/careerSteepness2
  quotientSteepness2_1<-careerSteepness2/careerSteepness1
  careerLengthShapei<-cbind(paste0(skieri$skier[1]), paste0(skieri$status[1]), careerLengthi_races, careerThird1_length, careerThird2_length, careerThird3_length, careerSteepness1, careerSteepness2, careerSteepness3, quotientSteepness2_1, quotientSteepness3_2)
  careerLengthShape<-rbind(careerLengthShape, careerLengthShapei)
}
colnames(careerLengthShape)<-c("skier", "status", "nRaces", "nRacesThird1", "nRacesThird2", "nRacesThird3", "careerSteepness1", "careerSteepness2", "careerSteepness3", "quotientSteepness2_1", "quotientSteepness3_2")


#-------------------------------------------------------------------------------------------------------------------------
#PLOT CAREER SHAPES: EARLY AND SLOW STARTERS AND RETIERERS

#fast starters
faststarters<-subset(careerLengthShape_ord, careerLengthShape_ord$quotientSteepness2_1<2.1)

athletes_faststart<-data.frame()
for (i in faststarters$skier){
  skieri<-subset(skiersCareer_clean, skiersCareer_clean$skier==i)
  if(max(skieri$podiumCum)>25 & max(skieri$raceN)>50){
    athletes_faststart<-rbind(athletes_faststart, skieri)
  }
}

#proceed to some hand-cleaning as the approximation of a curve through linear functions as well as the assumption
#of careers being more or less constant within three parts is not bullet-proof 

athletes_faststart_red<-athletes_faststart[athletes_faststart$skier!="Deborah Compagnoni" & athletes_faststart$skier!="Annie Famose" 
                                           & athletes_faststart$skier!="Monika Kaserer" & athletes_faststart$skier!="Carlo Janka" 
                                           & athletes_faststart$skier!="Peter Luscher" & athletes_faststart$skier!="Bojan Krizaj" 
                                           & athletes_faststart$skier!="Benjamin Raich" & athletes_faststart$skier!="Günther Mader" 
                                           & athletes_faststart$skier!="Atle Skardal" & athletes_faststart$skier!="Ole Christian Furuseth"
                                           & athletes_faststart$skier!="Tamara McKinney" & athletes_faststart$skier!="Hannes Trinkl"
                                           & athletes_faststart$skier!="Andreas Wenzel" & athletes_faststart$skier!="Peter Müller", ]

add<-subset(skiersCareer_clean, skiersCareer_clean$skier=="Mikaela Shiffrin")

faststarters_final<-rbind(athletes_faststart_red, add)

ggplot(faststarters_final, aes(x=raceDate, y=podiumCum, color=skier)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-12-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("faststarters_dateXpodiumCum.pdf", plot = last_plot())


#slow starters
slowstarters<-subset(careerLengthShape_ord, careerLengthShape_ord$quotientSteepness2_1>3)

athletes_slowstart<-data.frame()
for (i in slowstarters$skier){
  skieri<-subset(skiersCareer_clean, skiersCareer_clean$skier==i)
  if(max(skieri$podiumCum)>25 & max(skieri$raceN)>50){
    athletes_slowstart<-rbind(athletes_slowstart, skieri)
  }
}

athletes_slowstart_red<-athletes_slowstart[athletes_slowstart$skier!="Henrik Kristoffersen" & athletes_slowstart$skier!="Merle Carole" 
                                           & athletes_slowstart$skier!="Maria Walliser" & athletes_slowstart$skier!="Hilde Gerg" 
                                           & athletes_slowstart$skier!="Janica Kostelic" & athletes_slowstart$skier!="Mikaela Shiffrin" 
                                           & athletes_slowstart$skier!="Viktoria Rebensburg" & athletes_slowstart$skier!="Maria Höfl-Riesch", ]

add<-subset(skiersCareer_clean, skiersCareer_clean$skier=="Tina Maze" | skiersCareer_clean$skier=="Didier Cuche")

slowstarters_final<-rbind(athletes_slowstart_red, add)

ggplot(slowstarters_final, aes(x=raceDate, y=podiumCum, color=skier)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-12-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("slowstarters_dateXpodiumCum.pdf", plot = last_plot())


#early stoppers
earlystoppers<-subset(careerLengthShape_ord, careerLengthShape_ord$quotientSteepness3_2>1.3) # only non-actives

athletes_earlystop<-data.frame()
for (i in earlystoppers$skier){
  skieri<-subset(skiersCareer_clean, skiersCareer_clean$skier==i)
  if(max(skieri$podiumCum)>25 & max(skieri$raceN)>50 & skieri$status[1]=="nonActive"){
    athletes_earlystop<-rbind(athletes_earlystop, skieri)
  }
}

athletes_earlystop_red<-athletes_earlystop[athletes_earlystop$skier!="Tanja Poutiainen" & athletes_earlystop$skier!="Brigitte Ortli" 
                                           & athletes_earlystop$skier!="Lise-Marie Morerod" & athletes_earlystop$skier!="Monika Kaserer" 
                                           & athletes_earlystop$skier!="Wiltrud Drexel" & athletes_earlystop$skier!="Irene Epple" 
                                           & athletes_earlystop$skier!="Isolde Kostner" & athletes_earlystop$skier!="Peter Müller"
                                           & athletes_earlystop$skier!="Leonhard Stock" & athletes_earlystop$skier!="Andreas Wenzel"
                                           & athletes_earlystop$skier!="Paul Frommelt" & athletes_earlystop$skier!="Christian Mayer" 
                                           & athletes_earlystop$skier!="Ole Christian Furuseth" & athletes_earlystop$skier!="Carole Merle"
                                           & athletes_earlystop$skier!="Franz Heinzer" & athletes_earlystop$skier!="Cindy Nelson" 
                                           & athletes_earlystop$skier!="Karl Schranz"  & athletes_earlystop$skier!="Kjetil André Aamodt" 
                                           & athletes_earlystop$skier!="Ted Ligety" & athletes_earlystop$skier!="Fabienne Serrat"
                                           & athletes_earlystop$skier!="Hannes Trinkl", ]

earlystoppers_final<-athletes_earlystop_red

ggplot(earlystoppers_final, aes(x=raceDate, y=podiumCum, color=skier)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-12-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("earlystoppers_dateXpodiumCum.pdf", plot = last_plot())



#late stoppers
latestoppers<-subset(careerLengthShape_ord, careerLengthShape_ord$quotientSteepness3_2<1.3) # only non-actives

athletes_latestop<-data.frame()
for (i in latestoppers$skier){
  skieri<-subset(skiersCareer_clean, skiersCareer_clean$skier==i)
  if(max(skieri$podiumCum)>25 & max(skieri$raceN)>50 & skieri$status[1]=="nonActive"){
    athletes_latestop<-rbind(athletes_latestop, skieri)
  }
}

athletes_latestop<-data.frame()
for (i in latestopNames){
  skieri<-subset(skiersCareer_clean, skiersCareer_clean$skier==i)
  if(max(skieri$podiumCum)>25 & max(skieri$raceN)>50 & skieri$status[1]=="nonActive"){
    athletes_latestop<-rbind(athletes_latestop, skieri)
  }
}

athletes_latestop_red<-athletes_latestop[athletes_latestop$skier!="Lasse Kjus" & athletes_latestop$skier!="Günther Mader" 
                                         & athletes_latestop$skier!="Florence Steurer" & athletes_latestop$skier!="Isabelle Mir" 
                                         & athletes_latestop$skier!="Tamara McKinney" & athletes_latestop$skier!="Bernhard Russi" 
                                         & athletes_latestop$skier!="Bojan Krizaj" & athletes_latestop$skier!="Atle Skardal"
                                         & athletes_latestop$skier!="Peter Luscher", ]

add<-subset(skiersCareer_clean, skiersCareer_clean$skier=="Ivica Kostelic" | skiersCareer_clean$skier=="Bode Miller")

latestoppers_final<-rbind(athletes_latestop_red, add)

ggplot(latestoppers_final, aes(x=raceDate, y=podiumCum, color=skier)) + 
  geom_line(stat="identity", na.rm=T) +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  theme(legend.position="none") +
  scale_x_date(limits = c(as.Date("1960-01-01"), as.Date("2030-12-31"))) +
  geom_dl(aes(label = skier), method = list(dl.combine("last.points"), cex = 0.8))
ggsave("latestoppers_dateXpodiumCum.pdf", plot = last_plot())

#faststarters and slowstarters: look at temporal distribution
faststartersBefore1990<-data.frame()
faststartersAfter1990<-data.frame()
for (i in unique(faststarters_final_ord$skier)){
  skieri<-subset(faststarters_final_ord, faststarters_final_ord$skier==i)
  ifelse(min(skieri$raceDate)<as.Date("1990-01-01"), faststartersBefore1990<-rbind(faststartersBefore1990, skieri[1,]), faststartersAfter1990<-rbind(faststartersAfter1990, skieri[1,]))
}

slowstartersBefore1990<-data.frame()
slowstartersAfter1990<-data.frame()
for (i in unique(slowstarters_final_ord$skier)){
  skieri<-subset(slowstarters_final_ord, slowstarters_final_ord$skier==i)
  ifelse(min(skieri$raceDate)<as.Date("1990-01-01"), slowstartersBefore1990<-rbind(slowstartersBefore1990, skieri[1,]), slowstartersAfter1990<-rbind(slowstartersAfter1990, skieri[1,]))
}

#latestoppers and earlystoppers: look at gender distribution
latestoppersM<-subset(latestoppers_final_ord, latestoppers_final_ord$gender=="m")
length(unique(latestoppersM$skier))
latestoppersF<-subset(latestoppers_final_ord, latestoppers_final_ord$gender=="f")
length(unique(latestoppersF$skier))

earlystoppersM<-subset(earlystoppers_final_ord, earlystoppers_final_ord$gender=="m")
length(unique(earlystoppersM$skier))
earlystoppersF<-subset(earlystoppers_final_ord, earlystoppers_final_ord$gender=="f")
length(unique(earlystoppersF$skier))

#sign.test
tabLateEarlystoppersMF <- matrix(c(17,6,14,21),2,2)
dimnames(tabLateEarlystoppersMF) <-  list(c("male", "female"), c("latestop", "earlystop"))
chisq.test(tabLateEarlystoppersMF)
