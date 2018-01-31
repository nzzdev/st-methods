# NZZ Storytelling, script for the following article: https://www.nzz.ch/international/freund-und-feind-betrachtet-durch-die-brille-des-weissen-hauses-ld.1349175#subtitle-die-methodik-im-detail
# questions and comments: marie-jose.kolly@nzz.ch

### MISE EN PLACE ###
library(dplyr)
library(tibble)
library(sotu)
library(tm)
library(ggplot2)
library(countrycode)
library(tidyr)
library(directlabels)

setwd("mypath/graphics")


#---------------------------------------------------------------------------------------------------------------------
### VIEW AND CONFIGURE DATA ###
nrow(sotu_meta)
length(sotu_text)
head(sotu_text)

# write all sotu-addresses to directory
sotu_dir("mypath/data/sotu_originals", filenames)


#------------------------------------------------------------------------------------------------------------------------------------------------
### CORPUS CREATION AND PROCESSING ###

# Read in as corpus
directoryIn<-"mypath/data/sotu_red_augm"
docs<-Corpus(DirSource(directoryIn, encoding = "UTF-8"), readerControl = list(language = "eng"))


## Create different corpora containing different types of information

# Corpus 1: keep punctuation but remove whitespace
corpus1<-tm_map(docs, stripWhitespace)
directoryOut<-"mypath/data/sotu_corpus1"
writeCorpus(corpus1, path=directoryOut, filenames=paste0(substr(dir(directoryIn), 1, nchar(dir(directoryIn))-4),".txt",sep=""))

# Corpus 2: remove punctuation and whitespace and convert to lowercase to count words, and for concept and frequent word analysis
corpus2<-tm_map(docs, removePunctuation, preserve_intra_word_dashes = TRUE)
corpus2<-tm_map(corpus2, stripWhitespace)
corpus2<-tm_map(corpus2, content_transformer(tolower))
directoryOut<-"mypath/data/sotu_corpus2"
writeCorpus(corpus2, path=directoryOut, filenames=paste0(substr(dir(directoryIn), 1, nchar(dir(directoryIn))-4),".txt",sep=""))

# Corpus 3: additionally stemmed and stopped
corpus3<-tm_map(corpus2, removeWords, stopwords("english"))
corpus3<-tm_map(corpus3, stemDocument, language = "english") 
directoryOut<-"mypath/data/sotu_corpus3"
writeCorpus(corpus3, path=directoryOut, filenames=paste0(substr(dir(directoryIn), 1, nchar(dir(directoryIn))-4),".txt",sep=""))


## Create metadata frame

# to count words and characters, read in these files again with scan, which creates a vector with one-word-one-element
txtCleanCorpus <- list.files(path="mypath/data/sotu_corpus2/", pattern="*.txt", full.names=F, recursive=FALSE)
directoryCorpus2<-"mypath/data/sotu_corpus2/"

# build metadata from filenames and sotu_meta
filename<-unlist(lapply(strsplit(as.character(txtCleanCorpus), "\\."),'[[', 1))
year<-substr(filename, nchar(filename)-3, nchar(filename))
president<-substr(filename, 1, nchar(filename)-5) %>% gsub("-", " ", .) %>% gsub("\\s$", "", .)

party<-c()
for (i in 1:length(president)) party[i]<-sotu_meta$party[grep(president[i], tolower(gsub("\\.", "", sotu_meta$president)))[1]]

metadata<-data.frame(president, year, party)

# add party information for trump as he's not in sotu_meta
metadata[grep("trump", metadata$president),3]<-"Republican"


#------------------------------------------------------------------------------------------------------------------------------------------------
### ANALYSIS NUMBER OF WORDS ###

# number of characters
nChars<-c()
for (i in 1:length(txtCleanCorpus)){ 
  nCharsi<-sum(nchar(scan(paste0(directoryCorpus2,"/",txtCleanCorpus[i],sep=""), quote=NULL, what="x")))
  nChars<-rbind(nChars, nCharsi)
}

# number of words
nWords<-c()
for (i in 1:length(txtCleanCorpus)){ 
  nWordsi<-length(scan(paste0(directoryCorpus2,"/",txtCleanCorpus[i],sep=""), quote=NULL, what="x"))
  nWords<-rbind(nWords, nWordsi)
}

metadata<-mutate(metadata, nWords=as.numeric(as.character(nWords)), nChars=as.numeric(as.character(nChars)))

#total number of words
sum(metadata$nWords)

# plot
ggplot(metadata, aes(as.numeric(as.character(year)),nWords)) + 
  geom_bar(stat="identity") +
  ggtitle("Anzahl Wörter in den Reden der US-Präsidenten")+
  ylab("Absolute Anzahl Wörter")+
  theme_minimal() +
  theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), # or play around with something like hjust=-0.12*(nchar(indicator)/10)
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 


#------------------------------------------------------------------------------------------------------------------------------------------------
### ANALYSIS COUNTRIES AND REGIONS ###


## AMERICA
americPerFile<-read.table("mypath/data/datafiles/americUSPerFile.txt", sep="\t")
colnames(americPerFile)<-c("file", "americ", "ourRepublic", "our_federalUnion", "US")
metadata_america<-metadata %>% 
  as.tibble(.) %>% 
  mutate(americ=100*(americPerFile$americ/nWords)) %>% 
  mutate(ourRepublic=100*(americPerFile$ourRepublic/nWords)) %>% 
  mutate(our_federalUnion=100*(americPerFile$our_federalUnion/nWords)) %>% 
  mutate(US=100*(americPerFile$US/nWords)) %>%
  gather(key=word, value=prop, americ, ourRepublic, our_federalUnion, US)

# plot
ggplot(metadata_america, aes(as.numeric(as.character(year)),prop, fill=word)) + 
  geom_bar(stat="identity") +
  ggtitle("America(n), United States, Union und Republic in den Reden der US-Präsidenten")+
  ylab("Proportional zur Anzahl Wörter in Rede, in Prozent")+
  theme_minimal() +
  theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), 
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 


## AMERICA VERSUS ALL OTHER COUNTRIES AND REGIONS

# first we need to build some regex with a vector of country names - use the countrycode_data-dataframe in the countrycode-package
summary(countrycode_data)
unique(countrycode_data$region)
countrycode_data$country.name.en

grepCountriesForBash<-paste0("&& grep -o", " '", countrycode_data$country.name.en.regex, "' ", "$file | wc -l | tr -d 'XXX' && printf \"YYY\" \\")

write.table(grepCountriesForBash, file="mypath/analysis/grepCountries.txt", row.names=F, quote=F, fileEncoding="UTF-8")
### CAREFUL: REPLACE XXX BY \n IN THE .TXT FILE and YYY BY \t. THEN TRANSFORM INTO BASH-SCRIPT stateOfUnion.sh
### CAREFUL 2: THERE WAS A LOT OF HAND-CLEANING AND -AUGMENTING IN THE BASH-SCRIPT BELONGING TO THIS

# see bash-script for text analysis

# read in countries-per-file, regions-per-file and define colnames
countriesPerFile<-read.table("mypath/data/datafiles/countriesPerFileC2.txt", sep="\t")
colnames(countriesPerFile)<-c("file", countrycode_data$country.name.en)

regionsPerFile<-read.table("mypath/data/datafiles/regionsPerFileC2.txt", sep="\t")
colnames(regionsPerFile)<-c("file", "asiaPacific", "europe", "africa", "polynesia", "caribbean", "southAmerica", "northAmerica", "middleNearEast", "southAsia")

#replace the US-column in countriesPerFile by the row sums of americPerFile, because this was counted in a methodologically cleaner way (corpus 1, including 'US' but not 'us')
americAll<-rowSums(americPerFile[,2:length(americPerFile)])
countriesPerFile$`United States of America`<-americAll

#remove US-column for row-sums without US
countriesPerFile$`United States of America`
countriesPerFile[,256]
countriesPerFile_noUS<-countriesPerFile[,-c(256)]

#verify
countriesPerFile_noUS[,grep("United States", colnames(countriesPerFile_noUS))]
head(rowSums(countriesPerFile[,2:length(countriesPerFile)]))
head(rowSums(countriesPerFile_noUS[,2:length(countriesPerFile_noUS)]))
head(americAll)

#all countries but US: kick out doubles (2nd and 3rd occurence of yemen, take korea as a whole and not north and south korea, 
#get rid of BRD, DDR and only keep germany as a whole, get rid of austria-hungary, and of 2nd occurence of virgin islands)
grep("Korea", colnames(countriesPerFile_noUS)) #north korea: 129, south korea: 194
grep("German", colnames(countriesPerFile_noUS)) #BRD: 79, DDR: 89
grep("Austria", colnames(countriesPerFile_noUS)) #austria-hungary: 17
grep("Hungar", colnames(countriesPerFile_noUS))
grep("Yemen", colnames(countriesPerFile_noUS)) #2nd and 3rd: 268, 269
grep("Virgin", colnames(countriesPerFile_noUS)) #2nd: 263

countriesPerFile_red<-countriesPerFile_noUS[,-c(17, 79, 89, 129,194,263, 268, 269)]

### plot us vs rest with regions, too
countriesRegionsPerFile<-data.frame(countriesPerFile_red, regionsPerFile[,-1])
allButUS_regions<-rowSums(countriesRegionsPerFile[,2:length(countriesRegionsPerFile)])

usVsRest_regions<-data.frame("file"=countriesPerFile$file, "USA"=countriesPerFile$`United States of America`, "rest"=allButUS_regions)

metadata_usVsRest_regions<-metadata %>% 
  bind_cols(usVsRest_regions) %>%
  group_by(year) %>%
  mutate(USA_prop=100*(USA/nWords)) %>% 
  mutate(rest_prop=100*(rest/nWords)) %>% 
  select(-USA, -rest) %>%
  gather(key=partOfWorld, value=prop, -president, -year, -party,-nWords, -nChars, -file)

# plot
ggplot(metadata_usVsRest_regions, aes(as.numeric(as.character(year)), prop, col=partOfWorld)) + 
  geom_point() +
  geom_smooth(span=0.1, se=F) +
  ylab("Anteil an allen Wörtern pro Rede")+
  theme_minimal() +
  scale_x_continuous(breaks=seq(1790,2018, 5))+
  theme(axis.text=element_text(family="GT America", color="#05032d", size=10, angle=90), 
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), 
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 
ggsave("usVsRest_pointSmoothe.svg", width = 18, height=9)


## 20 most named countries overall
countryTotals<-colSums(countriesPerFile[,2:length(countriesPerFile)])
countryTotals
sort(countryTotals, decreasing = T)

#the 20 most frequent countries 
frequentCountries<-data.frame(countriesPerFile$file,
                              countriesPerFile$`United States of America`, 
                              countriesPerFile$Mexico, 
                              countriesPerFile$`United Kingdom of Great Britain and Northern Ireland`, 
                              countriesPerFile$Spain, 
                              countriesPerFile$`Russian Federation`,
                              countriesPerFile$France,
                              countriesPerFile$China,
                              countriesPerFile$Cuba,
                              countriesPerFile$Japan,
                              countriesPerFile$Germany,
                              countriesPerFile$Panama,
                              countriesPerFile$Iraq,
                              countriesPerFile$Nicaragua,
                              countriesPerFile$`Iran (Islamic Republic of)`,
                              countriesPerFile$Korea,
                              countriesPerFile$`Viet Nam`,
                              countriesPerFile$Brazil,
                              countriesPerFile$Canada,
                              countriesPerFile$Afghanistan,
                              countriesPerFile$Colombia,
                              countriesPerFile$Philippines)

# plot overall frequency
frequentCountries_totals <- colSums(frequentCountries[,2:length(frequentCountries)])
nbs<-as.numeric(as.character(frequentCountries_totals))
nms<-c("USA", "Mexiko", "Grossbritannien", "Spanien", "Russland / Sowjetunion", "Frankreich", "China", "Kuba", "Japan", "Deutschland", "Panama", "Irak", "Nicaragua", "Iran", "Korea", "Vietnam", "Brasilien", "Kanada", "Afghanistan", "Kolumbien", "Philippinen")
frequentCountries_totals<-data.frame("country"=nms, "counts"=nbs)

#reorder levels according to frequency
orderVar<-frequentCountries_totals$counts 
frequentCountries_totals$country<-factor(frequentCountries_totals$country, levels=frequentCountries_totals$country[order(orderVar, decreasing=T)])
print(levels(frequentCountries_totals$country)) #check

frequentCountries_noUS<-frequentCountries_totals[grep("USA", frequentCountries_totals$country, invert = T),]

ggplot(frequentCountries_noUS, aes(country, counts))+
  geom_bar(stat="identity")+
  ylab("Anzahl Erwähnungen insgesamt")+
  theme_minimal() +
  theme(axis.text=element_text(family="GT America", color="#05032d", size=10, angle=90), 
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), 
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 
ggsave("frequentCountries_bar.svg", width = 18, height=9)

# plot over time: small mult
colnames(frequentCountries)<-c("file", "USA", "Mexiko", "Grossbritannien", "Spanien", "Russland / Sowjetunion", "Frankreich", "China", "Kuba", "Japan", "Deutschland", "Panama", "Irak", "Nicaragua", "Iran", "Korea", "Vietnam", "Brasilien", "Kanada", "Afghanistan", "Kolumbien", "Philippinen")

# calculate proportions relative to nWords per file
metadata_countries<-metadata %>% 
  bind_cols(frequentCountries) %>%
  group_by(year) %>%
  summarize_at(vars(USA:Philippinen, nWords),sum) %>%
  mutate_at(vars(USA:Philippinen),funs((. / nWords)*100)) %>%
  select(-Philippinen, -Kolumbien, -Iran, -Nicaragua, -Panama, -Brasilien)  %>%
  gather(key=country, value=prop, -year)

#reorder levels according to frequency of occurence
frequentCountries_totals_red<-frequentCountries_totals[grep("Philip|Kolum|Iran|Nicara|Panam|Brasi", frequentCountries_totals$country, invert=T),]#get rid of unused countries

metadata_countries_augm<-merge(metadata_countries, frequentCountries_totals_red, by.x="country", by.y="country", all=F)
metadata_countries_augm$country<-as.factor(metadata_countries_augm$country)
levels(metadata_countries_augm$country)
metadata_countries_augm$country <- factor(metadata_countries_augm$country, levels(metadata_countries_augm$country)[c(14,11,5,13,12,4,2,10,7,3,6,15,9,8,1)])

#plot small mult
ggplot(metadata_countries_augm, aes(as.numeric(as.character(year)),prop, col=country)) + 
  geom_line() +
  ylab("Anteil an allen Wörtern pro Rede")+
  facet_wrap(~country, ncol=5) +
  theme_minimal() +
  theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), 
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 
ggsave("smallMultiples_desktopTest.svg", plot = last_plot(), width=16, height=9)


#plot one-by-one for small-multiple-layout (y-axis with USA, same for all)
for(i in unique(metadata_countries_augm$country)){
  filename<-paste0(gsub("/", "", i), "Xtime_smallmultiples.svg")
  countryi<-filter(metadata_countries_augm, country==i)
  ggplot(countryi, aes(as.numeric(as.character(year)),prop)) +
    geom_line() +
    ggtitle(paste0(i))+
    ylab("Anteil an allen Wörtern pro Rede")+
    ylim(0,1.78)+ #possibly adapt
    scale_x_continuous(breaks=c(1790, seq(1800,2010, 50),2018))+
    theme_minimal() +
    theme(axis.text=element_text(family="GT America", color="#05032d", size=10, angle=90), 
          #axis.title.x=element_text(family="GT America", color="#05032d", size=13, hjust=1, vjust=-4), # or play around with something like vjust=-4/nchar(title.chars)
          axis.title.x=element_blank(),
          axis.title.y=element_text(family="GT America", color="#05032d", size=13),
          plot.title = element_text(family="GT America", color="#05032d", size=20), # or play around with something like hjust=-0.12*(nchar(indicator)/10)
          plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
          plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
          panel.grid = element_line(color="#ececf0", size=.3),
          plot.margin=unit(c(1,1,1.5,1.2),"cm"))
  ggsave(filename, width=9, height=9)
}


#plot one-by-one for grouped small-multiple-layout (y-axis without USA but same for all)
metadata_countries_augm_noUS<-metadata_countries_augm[grep("USA", metadata_countries_augm$country, invert=T),]
for(i in unique(metadata_countries_augm_noUS$country)){
  filename<-paste0(gsub("/", "", i), "Xtime_groups.svg")
  countryi<-filter(metadata_countries_augm, country==i)
  ggplot(countryi, aes(as.numeric(as.character(year)),prop)) +
    geom_line() +
    ggtitle(paste0(i))+
    ylab("Anteil an allen Wörtern pro Rede")+
    ylim(0,1.25)+ #possibly adapt
    scale_x_continuous(breaks=c(1790, seq(1800,2010, 50),2018))+
    theme_minimal() +
    theme(axis.text=element_text(family="GT America", color="#05032d", size=10, angle=90), 
          axis.title.x=element_blank(),
          axis.title.y=element_text(family="GT America", color="#05032d", size=13),
          plot.title = element_text(family="GT America", color="#05032d", size=20), # or play around with something like hjust=-0.12*(nchar(indicator)/10)
          plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
          plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
          panel.grid = element_line(color="#ececf0", size=.3),
          plot.margin=unit(c(1,1,1.5,1.2),"cm"))
  ggsave(filename, width=9, height=9)
}


### ANALYSIS OF THE MOST FREQUENT COUNTRIES PER PRESIDENT ###

metadata_countries<-metadata %>% 
  bind_cols(countriesPerFile) %>%
  gather(key=country, value=counts, -president, -year, -party,-nWords, -nChars, -file)

#get most important countries per president - and mean proportion per country (i.e., we value each year the same, regardless of whether there was more or less text)
presiCntry<-metadata_countries %>% 
  group_by(president, country) %>% 
  summarise(cntryMean=n(counts), startYear=min(as.numeric(as.character(year)))) %>% 
  arrange(desc(cntryMean))

maxCntriesPresi<-data.frame()
for(i in unique(metadata_countries$president)){
  presi<-presiCntry %>% filter(president==i)
  maxima<-presi[1:6,]
  maxCntriesPresi<-bind_rows(maxCntriesPresi, maxima)
}

#get most important countries per president - and sum per country
presiCntry_counts<-metadata_countries %>% 
  group_by(president, country) %>% 
  summarise(cntrySum=sum(counts), startYear=min(as.numeric(as.character(year)))) %>% 
  arrange(desc(cntrySum))

#get rid of doubles
presiCntry_counts_red<-presiCntry_counts[grep("Heard|Federal|Democratic", presiCntry_counts$country, invert=T),]
print(presiCntry_counts_red[presiCntry_counts_red$president=="donald j trump",], n=25)

#with sums, not means
maxCntriesPresi<-data.frame()
for(i in unique(metadata_countries$president)){
  presi<-presiCntry_counts_red %>% filter(president==i)
  maxima<-presi[1:8,]
  maxCntriesPresi<-bind_rows(maxCntriesPresi, maxima)
}

#reorder factor levels according to startYear of president
maxCntriesPresi$startYear<-as.numeric(as.character(maxCntriesPresi$startYear)) #  adapt to the reuired variable
maxCntriesPresi$president<-factor(maxCntriesPresi$president, levels(maxCntriesPresi$president)[order(unique(maxCntriesPresi$startYear), decreasing=F)])
print(levels(maxCntriesPresi$president)) #check

# plot
ggplot(maxCntriesPresi, aes(country,cntrySum)) + 
  geom_bar(stat="identity", fill="lightgray") +
  facet_wrap(~president, scales="free") +
  ggtitle("Andere Länder in den Reden der US-Präsidenten")+
  ylab("Proportional zur Anzahl Wörter in Rede, in Prozent")+
  geom_text(aes(label=country, x=country, y=(cntrySum-cntrySum)), hjust=-.3, angle=90, family="GT America", color="#05032d", size=2.5)+
  theme_minimal() +
  theme(axis.text.y=element_text(family="GT America", color="#05032d", size=11),
        axis.text.x=element_blank(),
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), 
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 


## Trump
trump<-filter(maxCntriesPresi, president =="donald j trump")

#rename
trump$country<-c("USA", "Nordkorea", "China", "Iran", "Mexiko", "Kanada", "Afghanistan", "Israel")

#reorder 
orderVar<-trump$cntrySum
trump$country<-factor(trump$country, levels=trump$country[order(orderVar, decreasing=T)])

#plot
ggplot(trump, aes(country,cntrySum)) + 
  geom_bar(stat="identity", fill="lightgray") +
  ggtitle("Donald J. Trump")+
  ylab("Anzahl Erwähnungen")+
  theme_minimal() +
  theme(axis.text.y=element_text(family="GT America", color="#05032d", size=11),
        axis.text.x=element_text(family="GT America", color="#05032d", size=11, angle=90),
        axis.title.x=element_blank(),
        axis.title.y=element_text(family="GT America", color="#05032d", size=13),
        plot.title = element_text(family="GT America", color="#05032d", size=20), 
        plot.subtitle = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1),
        plot.caption = element_text(family="GT America", color="#05032d", size=10, hjust=-0.1, vjust=-3),
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) 
ggsave("trump.svg")

