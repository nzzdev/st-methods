## Popmusik, NZZ, 5. 12. 2019##

## Prep
rm(list=ls(all=TRUE))
dev.off()
setwd("~/Library/Mobile Documents/com~apple~CloudDocs/NZZ/Pop2")
options(stringsAsFactors=F) # Das automatische Bilden von Faktoren in dataframes verhindern

#Packages
library(tidyverse)
library(readxl)
library(directlabels)
library(rvest)

#uncomment for scraping and formatting

#### SCRAPE SINGLES ####

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

sundays <- as.Date(sort(unique(hitparade$date))) #uncommented for later use
wsundays <- format(sundays, format = "%d-%m-%Y")
# 
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

# #### explore ####
# 
# # single
# bsp <- hitparade[grep("All I Want For Christmas Is You", hitparade$title), ]
# levels(as.factor(bsp$title))
# 
# # bsp <- subset(bsp, pos < 11)
# 
# ggplot(bsp, aes(x = date, y = pos, color = title)) +
#   geom_line() +
#   geom_dl(aes(label=title), method = "top.bumpup") +
#   scale_y_reverse(breaks=c(1,10,50,100)) + 
#   theme_classic() + theme(legend.position="none")
# 
# #album
# 
# absp <- ahitparade[grep("Beatrice Egli", ahitparade$aartist), ]
# levels(as.factor(absp$atitle))
# 
# # absp <- subset(bsp, pos < 11)
# 
# ggplot(absp, aes(x = adate, y = apos, color = atitle)) +
#   geom_line() +
#   geom_dl(aes(label=atitle), method = "top.bumpup") +
#   scale_y_reverse(breaks=c(1,10,50,100)) + 
#   theme_classic() + theme(legend.position="none")
# 
# 
# #### Career ####
# # choose artists for overview
# 
# atop <- subset(hitparade$artist, hitparade$pos == 1)
# stop <- subset(ahitparade$aartist, ahitparade$apos == 1)
# 
# 
# top <- rbind(atop, stop) %>% as.vector() %>% unique()
# top

# create career index

# hitparade$type <- "single"
# ahitparade$type <- "album"
# 
# colnames(ahitparade) <- colnames(hitparade)
# thitparade <- rbind(hitparade, ahitparade)
# thitparade$npos <- 101-thitparade$pos
# 
# framesun <- as.data.frame(sundays)
# colnames(framesun) <- "date"
# 
# ctable <- vector()
# 
# for (m in 1:length(top)){
# 
# score <- thitparade %>%
#   subset(artist == top[m]) %>%
#   select(date, npos) %>%
#   group_by(date) %>%
#   summarise(score = sum(npos))
#   
# what <- left_join(framesun, score, by = "date")
# 
# cloop <- cbind(what, top[m])
# 
# ctable <- rbind(ctable, cloop)
# 
# } ## WHAT ABOUT ONE HIT WONDER DEFINITION / SONG NAMES?
# 
# csum <- data.frame()
# 
# for (n in 1:length(top)){
#   bsptbl <- subset(ctable, `top[m]` == top[n])
#   
#   cmin <- bsptbl$date[min(which(bsptbl$score > 89))]
#   cmax <- bsptbl$date[max(which(bsptbl$score > 89))]
#   cmedian <- bsptbl$date[median(which(!is.na(bsptbl$score)))]
#   cweeks <- difftime(cmax, cmin, units = "weeks") %>% 
#     as.numeric() %>% round(digits = 0)
#   aname <- unique(bsptbl$`top[m]`)
#   
#   csuml <- as.data.frame(cbind(aname , as.character(cmin),  as.character(cmax), as.character(cmedian), as.numeric(cweeks)))
#   
#   csum <- rbind.data.frame(csum, csuml)
# }
# 
# csum$cmedian <- as.Date(csum$V4, format = "%Y-%m-%d")
# csum$cmin <- as.Date(csum$V2, format = "%Y-%m-%d")
# csum$cmax <- as.Date(csum$V3, format = "%Y-%m-%d")
# csum$cweeks <- as.numeric(csum$V5)

#Langlebigkeit Songs

hitparade$unique <- paste0(hitparade$artist, " - ", hitparade$title)
no1hits <- unique(hitparade$unique[hitparade$pos == 1])

tabsin <- data.frame()

for (n in 1:length(no1hits)){
  
  akt <- c(no1hits[n], 
               as.character(min(hitparade$date[hitparade$unique == no1hits[n]])), 
               length(hitparade$unique[hitparade$unique == no1hits[n] & hitparade$pos < 11]))
  tabsin <- rbind(tabsin, akt)
}

colnames(tabsin) <- c("name", "firstdate", "weeks")

tabsin$weeks <- as.numeric(tabsin$weeks)
tabsin$decade <- tabsin$firstdate %>% substr(1,4) %>% as.numeric()
tabsindec <- tabsin %>% group_by(decade) %>% summarise(weeks = median(weeks))

plot(tabsindec$decade, tabsindec$weeks,  bty='n')

#Langlebigkeit Alben

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

# Durschschnittshit

latrajectoire <- data.frame()

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

table(latrajectoire$gap)

relhit <- left_join(hitparade, latrajectoire, by = c("unique" = "lehit")) 
relhit$reldate <- relhit$date-as.Date(relhit$first)

relhit$relweek <- round(as.numeric(relhit$reldate)/7, digits = 0)
relchart <- relhit %>% subset(!is.na(relweek) & relweek < 100)

length(unique(relchart$unique))

relmean <- relchart %>%
  group_by(relweek) %>%
  summarise(score = median(pos))

ggplot() + 
  geom_point(data = relchart[relchart$relweek < 53 & relchart$pos < 51,], aes(x = relweek, y = pos, group = unique),alpha = 0.03, color = "orange2") +
  geom_line(data = relmean[relmean$relweek < 32,], aes(x = relweek, y = score)) +
  scale_y_reverse(breaks=c(1,10,20,30,40,50)) +
  scale_x_continuous(breaks=c(0,13,26,39,52)) + 
  theme_minimal() + theme(legend.position="none")

table(relchart$relweek)

# Langlebige Hits 

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

ggplot() + 
  geom_line(data = relx, aes(x = relweek, y = score), color = "blue3") +
  geom_line(data = rely, aes(x = relweek, y = score), color = "darkgreen") +
  geom_line(data = relz, aes(x = relweek, y = score)) +
  geom_line(data = relzz, aes(x = relweek, y = score), color = "darkred") +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  scale_x_continuous(breaks=c(26,52,78,104)) + 
  theme_minimal() + theme(legend.position="none")


# Adele - Someone Like You

adele <- subset(hitparade, unique == "Adele - Someone Like You")

chrna <- left_join(as.data.frame(hitparade$date), adele, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > "2011-06-01" & `hitparade$date` < "2013-05-15")

chrna$weeknr <- c(0:99)

ggplot(chrna, aes(x = weeknr , y = pos)) +
  geom_line() + 
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  scale_x_continuous(breaks=c(0,26,52, 78)) + 
  theme_minimal() + theme(legend.position="none") + ggtitle("Someone like you")

# christmas <- subset(hitparade, unique == "Adele - Someone Like You")
# 
# chrna <- left_join(as.data.frame(hitparade$date), christmas, by = c("hitparade$date" = "date")) %>% 
#   distinct() %>% 
#   subset(`hitparade$date` > min(christmas$date) & `hitparade$date` < max(christmas$date))
# 
# ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
#   geom_line() +
#   geom_point(alpha = 0.25)+
#   scale_y_reverse(breaks=c(1,10,50,100)) + 
#   theme_minimal() + theme(legend.position="none")


# Mariah Carey - All I Want For Christmas Is You

alliwant <- subset(hitparade, unique == "Mariah Carey - All I Want For Christmas Is You")

chrna <- left_join(as.data.frame(hitparade$date), alliwant, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > "1994-01-01" & `hitparade$date` < max(alliwant$date))

ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
  geom_line() + 
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  scale_x_date(date_labels = "%Y", date_minor_breaks = "1 year", breaks = c(as.Date("2010-01-01"), 
                                                                            as.Date("1994-01-01"),
                                                                            as.Date("2000-01-01"),
                                                                            as.Date("2010-01-01"),
                                                                            as.Date("2018-01-01"))) +
  theme_minimal() + theme(legend.position="none") + ggtitle("All I Want...")

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

# Wham! - Last Christmas

hei <- subset(hitparade, unique == "Baschi - Bring en hei")

chrna <- left_join(as.data.frame(hitparade$date), hei, by = c("hitparade$date" = "date")) %>% 
  distinct() %>% 
  subset(`hitparade$date` > min(hei$date) & `hitparade$date` < "2013-01-01")

ggplot(chrna, aes(x = `hitparade$date` , y = pos)) +
  geom_line() +
  geom_point(alpha = 0.25) +
  scale_y_reverse(breaks=c(1,10,50,100)) + 
  theme_minimal() + theme(legend.position="none") + ggtitle("Last Christmas")

