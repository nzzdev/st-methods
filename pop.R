## Popmusik, NZZ, 5. 12. 2019 ##
## This is a replication script for the data presented in:
# Und plötzlich dominieren wenige Superhits die Schweizer Charts 
# https://www.nzz.ch/feuilleton/schweizer-charts-und-ploetzlich-dominieren-wenige-superhits-ld.1488251


##Preparation
rm(list=ls(all=TRUE))
dev.off()
setwd("~/Library/Mobile Documents/com~apple~CloudDocs/NZZ/Pop2")
options(stringsAsFactors=F) # Das automatische Bilden von Faktoren in dataframes verhindern

#Packages
library(tidyverse)
library(readxl)
library(directlabels)
library(rvest)

# Scraping and formatting take a long time, clean data as used in the article are provided. 
# Uncomment the following section to scrape and format the data yourself.

# #### SCRAPE SINGLES ####
# # download the data: weekly charts pages are numbered consecutively, download all with a loop
# 
# dir.create(paste0(getwd(),"/html"))
# dir.create(paste0(getwd(),"/html/singles"))
# 
# for (i in 1:2653){ # last page is 2653 as of 1. December 2019
#   download.file(paste0("https://hitparade.ch/showcharttext.asp?week=",i), paste0("html/singles/week",i,".html"), quiet = F)
# }
# read in and structure the data with a loop
# filenames <- dir(path= "html/singles/", pattern = "*.html") #list all HTML files in /html
# hitparade <- data.frame()
# 
# for (j in 1:length(filenames)){
# 
#   webpage <- read_html(paste0("~/Library/Mobile Documents/com~apple~CloudDocs/NZZ/Pop2/html/singles/",filenames[j]))
#   rank_data_html <- html_nodes(webpage,'.mcontent')
#   rank_data <- html_text(rank_data_html) #Converting the html to text
# 
# 
#   split1 <- str_split(rank_data, "\r\n\r\n", simplify = TRUE) #split...
#   date <- str_sub(split1[4], 1, 10)
# 
#   pos <- split1[c(TRUE, FALSE)]
#   pos <- pos[-c(1:2)] %>% str_sub( 1, -2)
# 
#   rest <- split1[c(FALSE, TRUE)]
#   rest <- rest[-c(1:2)]
# 
#   vorwoche <- as.vector(str_extract(rest, "\\([^()]+\\)")) %>% str_sub( 2, -2) #...and extract the strings with regex
#   serie <- as.vector(str_extract_all(rest, "\\([:digit:]+\\.\\ [^()]+\\)", simplify =  TRUE)) %>% str_sub( 2, -9)
#   # label <- as.vector(str_extract_all(rest, "\\([^()]+[^() ]\\/[^() ][^()]+\\)", simplify =  TRUE)) %>% str_sub( 2, -2) #commented out wegen komplikationen " / "
#   artist <- str_extract_all(rest, "\\)[^\n]+\\ \\-\\ ", simplify = T) %>% str_sub( 3, -4)
#   title <- str_extract_all(rest, "\\ \\-\\ [^\n]+\\([:digit:]", simplify = T) %>% str_sub( 4, -4)
# 
#   tab <- as.data.frame(cbind(date, pos, title, artist, vorwoche, serie)) #combine to dataframe
#   tab
#   hitparade <- rbind(hitparade, tab)
# 
# }
# 
# # formatting
# hitparade$date <- as.Date(hitparade$date, format = "%d.%m.%Y")
# 
# hitparade$pos <- as.numeric(hitparade$pos)
# hitparade$serie <- as.numeric(hitparade$serie)
# hitparade$vorwoche <- as.numeric(hitparade$vorwoche)
# 
# rownames(hitparade) <- c()
# 
# # check for excess length table: >100 = reread html
# check <- as.data.frame(table(hitparade$date)) #check for lengths
# table(as.factor(check$Freq))
# check[check$Freq > 100,]
# 
# # save
# write_csv(hitparade, "hitparade.csv")

hitparade <- read_csv("hitparade.csv")

#### SCRAPE ALBUMS ####

sundays <- as.Date(sort(unique(hitparade$date))) #get all the dates when charts were published (uncommented, used later)
wsundays <- format(sundays, format = "%d-%m-%Y")

# dir.create(paste0(getwd(),"/html/albums"))
# 
# for (k in 2639:2653) { # 2621 as of 21. April
# download.file(paste0("https://hitparade.ch/charts/alben/", wsundays[k]), paste0("html/albums/albumweek",k,".html"), quiet = F)
# }
# 
# afilenames <- dir(path= "html/albums/", pattern = "*.html") #list all HTML files in /html
# head(afilenames)
# 
# ahitparade <- data.frame()
# afolder <- paste0(getwd(),"/html/albums/")
# 
# for (l in 1:length(afilenames)){
# 
#   aartist <- read_html(paste0(afolder,afilenames[l])) %>%
#     html_nodes('.navb b') %>%
#     html_text()
# 
#   atitle <- read_html(paste0(afolder ,afilenames[l])) %>%
#     html_nodes('.navb') %>%
#     html_text() %>%
#     str_replace(coll(aartist), "")
# 
#   apos <- read_html(paste0(afolder ,afilenames[l])) %>%
#     html_nodes('.text:nth-child(1)') %>%
#     html_text()
# 
#   aprev <- read_html(paste0(afolder ,afilenames[l])) %>%
#     html_nodes('.charts td:nth-child(2)') %>%
#     html_text()
# 
#   astreak <- read_html(paste0(afolder ,afilenames[l])) %>%
#     html_nodes('.notmobile+ .text') %>%
#     html_text()
# 
#   adate <-read_html(paste0(afolder ,afilenames[l])) %>%
#     html_nodes('h2') %>%
#     html_text() %>%
#     str_replace_all(fixed("\r\n"), "") %>%
#     rep(length(atitle))
# 
#   tab <- as.data.frame(cbind(adate, apos, atitle, aartist, aprev, astreak)) #combine to dataframe
#   tab
#   ahitparade <- rbind(ahitparade, tab)
# }
# 
# ahitparade$adate <- as.Date(ahitparade$adate, format = "%d.%m.%Y")
# ahitparade$apos <- as.numeric(ahitparade$apos)
# ahitparade$aprev <- as.numeric(ahitparade$aprev)
# ahitparade$astreak <- as.numeric(ahitparade$astreak)
# 
# write_csv(ahitparade, "album-hitparade.csv")

ahitparade <- read_csv("album-hitparade.csv")


#Lifespan Singles

hitparade$unique <- paste0(hitparade$artist, " - ", hitparade$title) #create unique idetifier
no1hits <- unique(hitparade$unique[hitparade$pos == 1]) # get every no 1 hit

tabsin <- data.frame()

#for every hit, get how many weeks they spent in the top 10. for top 1, change 11 to 2 on line 155
for (n in 1:length(no1hits)){
  
  akt <- c(no1hits[n], 
               as.character(min(hitparade$date[hitparade$unique == no1hits[n]])), 
               length(hitparade$unique[hitparade$unique == no1hits[n] & hitparade$pos < 11]))
  tabsin <- rbind(tabsin, akt)
}

colnames(tabsin) <- c("name", "firstdate", "weeks")
tabsin$weeks <- as.numeric(tabsin$weeks)
tabsin$decade <- tabsin$firstdate %>% substr(1,4) %>% as.numeric() #get the year from the date (decade is the wrong name here, but too lazy to change it everywhere now)
tabsindec <- tabsin %>% group_by(decade) %>% summarise(weeks = median(weeks)) # get the median length per year

plot(tabsindec$decade, tabsindec$weeks,  bty='n') #SIMPLE base plot

#Lifespan Albums (same logic as above)

ahitparade$unique <- paste0(ahitparade$aartist, " - ", ahitparade$atitle)
ano1hits <- unique(ahitparade$unique[ahitparade$apos == 1])

atabsin <- data.frame()

for (n in 1:length(ano1hits)){
  
  aakt <- c(ano1hits[n], 
            as.character(min(ahitparade$adate[ahitparade$unique == ano1hits[n]])), 
            length(ahitparade$unique[ahitparade$unique == ano1hits[n] & ahitparade$apos < 11]))
  atabsin <- rbind(atabsin, aakt)
}

colnames(atabsin) <- c("name", "firstdate", "weeks")

atabsin$weeks <- as.numeric(atabsin$weeks)
atabsin$decade <- atabsin$firstdate %>% substr(1,4) %>% as.numeric()
atabsindec <- atabsin %>% group_by(decade) %>% summarise(weeks = median(weeks))

plot(atabsindec$decade, atabsindec$weeks, bty='n')

# The average hit trajectory

latrajectoire <- data.frame()

#for every hit, get their first appearance, their peak and the time inbetween both

for (q in 1:length(no1hits)){
  
  lehit <- no1hits[q]
  lepremier <- min(hitparade$date[hitparade$unique == lehit])
  lesommet <- min(hitparade$date[hitparade$unique == lehit & hitparade$pos == 1])
  ladifference <- lesommet-lepremier
  
  leloop <- cbind(lehit, as.character(lepremier), as.character(lesommet), ladifference)
  latrajectoire<- rbind(latrajectoire, leloop)
}

colnames(latrajectoire) <- c("lehit", "first", "peak", "gap")

latrajectoire$gap <- as.numeric(latrajectoire$gap)

table(latrajectoire$gap) #see how big the gap is to reach no1, in days

relhit <- left_join(hitparade, latrajectoire, by = c("unique" = "lehit")) #merge with main data file
relhit$reldate <- relhit$date-as.Date(relhit$first) #for every occurence in the charts, calculate how long the hit has been there

relhit$relweek <- round(as.numeric(relhit$reldate)/7, digits = 0) #get weeks instead of days
relchart <- relhit %>% subset(!is.na(relweek) & relweek < 100) # just get no1 hits and only the first 100 weeks

length(unique(relchart$unique)) #number of songs on no1

#get the median position per relative week
relmean <- relchart %>%
  group_by(relweek) %>%
  summarise(score = median(pos))

#plot it nicely
ggplot() + 
  geom_point(data = relchart[relchart$relweek < 53 & relchart$pos < 51,], aes(x = relweek, y = pos, group = unique),alpha = 0.03, color = "orange2") +
  geom_line(data = relmean[relmean$relweek < 32,], aes(x = relweek, y = score)) +
  scale_y_reverse(breaks=c(1,10,20,30,40,50)) +
  scale_x_continuous(breaks=c(0,13,26,39,52)) + 
  theme_minimal() + theme(legend.position="none")

table(relchart$relweek) #fpr the median line, check how many hits are still in the charts after any number of weeks. for the article, 150 was chosen as the limit

# Hits with long careers
# get some examples...

relx <- relchart %>% subset(unique == "Lo & Leduc - 079") %>%
  group_by(relweek) %>%
  summarise(score = median(pos))

rely <- relchart %>% subset(unique == "Ed Sheeran - Shape Of You") %>%
  group_by(relweek) %>%
  summarise(score = median(pos))

relz <- relchart %>% subset(unique == "Scorpions - Wind Of Change") %>%
  group_by(relweek) %>%
  summarise(score = median(pos))

relzz <- relchart %>% subset(unique == "Luis Fonsi feat. Daddy Yankee - Despacito") %>%
  group_by(relweek) %>%
  summarise(score = median(pos))

#...and plot them
ggplot() + 
  geom_line(data = relx, aes(x = relweek, y = score), color = "blue3") +
  geom_line(data = rely, aes(x = relweek, y = score), color = "darkgreen") +
  geom_line(data = relz, aes(x = relweek, y = score)) +
  geom_line(data = relzz, aes(x = relweek, y = score), color = "darkred") +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  scale_x_continuous(breaks=c(26,52,78,104)) + 
  theme_minimal() + theme(legend.position="none")


# Special cases - object chrna reused to avoid creating a million objects

# Adele - Someone Like You

adele <- subset(hitparade, unique == "Adele - Someone Like You")

#merge chart occurences to all chart dates to get NA to be able to plot the gaps
chrna <- left_join(as.data.frame(hitparade$date), adele, by = c("hitparade$date" = "date")) %>%
  distinct() %>% 
  subset(`hitparade$date` > "2011-06-01" & `hitparade$date` < "2013-05-15") #select date range

chrna$weeknr <- c(0:99) #select relative date range

#plot it (with gaps!)
ggplot(chrna, aes(x = weeknr , y = pos)) +
  geom_line() + 
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  scale_x_continuous(breaks=c(0,26,52, 78)) + 
  theme_minimal() + theme(legend.position="none") + ggtitle("Someone like you") #Warnings are due to NA values and can be ignored


# the following examples follow the same logic, but with absolute rather than relative dates plotted

# Mariah Carey - All I Want For Christmas Is You

alliwant <- subset(hitparade, unique == "Mariah Carey - All I Want For Christmas Is You")

chrna <- left_join(as.data.frame(hitparade$date), alliwant, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > "1994-01-01" & `hitparade$date` < max(alliwant$date))

ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
  geom_line() + 
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  scale_x_date(date_labels = "%Y", date_minor_breaks = "1 year", breaks = c(as.Date("2010-01-01"), #custom ticks
                                                                            as.Date("1994-01-01"),
                                                                            as.Date("2000-01-01"),
                                                                            as.Date("2010-01-01"),
                                                                            as.Date("2018-01-01"))) +
  theme_minimal() + theme(legend.position="none") + ggtitle("All I Want For Christmas Is You")

# Wham! - Last Christmas

lastchristmas <- subset(hitparade, unique == "Wham! - Last Christmas")

chrna <- left_join(as.data.frame(hitparade$date), lastchristmas, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > min(lastchristmas$date) & `hitparade$date` < max(lastchristmas$date))

ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
  geom_line() +
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  theme_minimal() + theme(legend.position="none") + ggtitle("Last Christmas")

# Baschi - Bring en hei

hei <- subset(hitparade, unique == "Baschi - Bring en hei")

chrna <- left_join(as.data.frame(hitparade$date), hei, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > min(hei$date) & `hitparade$date` < "2013-01-01")

ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
  geom_line() +
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  theme_minimal() + theme(legend.position="none") + ggtitle("Baschi - Bring en hei")

# Queen - Bohemian Rhapsody

queen <- subset(hitparade, unique == "Queen - Bohemian Rhapsody")

chrna <- left_join(as.data.frame(hitparade$date), queen, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > min(queen$date) & `hitparade$date` < max(queen$date))

ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
  geom_line() +
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  theme_minimal() + theme(legend.position="none") + ggtitle("Queen - Bohemian Rhapsody")

