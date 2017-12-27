#NZZ Storytelling, July 2017: How we scraped the publication database of the Basel Committee on Banking Supervision and analyzed their supervisory texts in order to visualize quantity and quality of regulatory text over time
#Feedback welcome by e-mail marie-jose.kolly[at]nzz.ch or twitter [at]mjkolly

#Article presenting results: https://nzz.ch/ld.1304103

library(rvest)
library(pdftools)
library(tm)
library(ggplot2)
library(magrittr)
library(readr)

#------------------------------------------------------------------------------------------
## GET LINKS AND METADATA OF THE PDFS TO DOWNLOAD

# Publication Types
# -    standards
# -    guidelines
# -    sound practices
# Publication Status
# -    final 

# links to all sub-corpora
standards_final<-"https://www.bis.org/bcbs/publications.htm?a=1&set=8&set=1&mp=any&pi=title&page="
guidelines_final<-"https://www.bis.org/bcbs/publications.htm?a=1&set=8&set=2&mp=any&pi=title&page="
soundPract_final<-"https://www.bis.org/bcbs/publications.htm?a=1&set=8&mp=any&pi=title&set=7" ### ONLY ONE PAGE

#!! adapt this part depending on the sub-corpus to treat
link<-standards_final

names<-c()
dates<-c()
links<-c()
for (page in c(1,2)){
  # pseudo-loop over pages
  website<-read_html(paste0(link))
  # get document names
  names_page<-website %>%
    # change names-number according to page-number - quick fix
    html_nodes("h4 a") %>%
    html_text()
  # get document dates
  dates_page<-website %>%
    # change names-number according to page-number - quick fix
    html_nodes(".item .item_date") %>%
    html_text()
  # get link names
  links_page<-html_attr(html_nodes(website, "h4 a"), "href")
  names<-c(names, names_page)
  dates<-c(dates, dates_page)
  links<-c(links, links_page)
}

# clean names, as some additional characters were generated; remove "/" as R cannot handle file download when / in title; replace " by empty, as pdf2text cannot handle " in title
namesClean<-c()
for(i in 1:length(names)){namesClean[i]<-gsub(' \n|\n|\t|/|\"',"", names[i])}
datesClean<-c()
for(i in 1:length(dates)){datesClean[i]<-gsub(" \n|\n|\t","", dates[i])}

#quick fix: convert months to numbers as as.Date produces NA for oct, mar, may and dec for some reason
datesNr<-c()
for(i in 1:length(datesClean)){datesNr[i]<-gsub("Jan","01",datesClean[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Feb","02",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Mar","03",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Apr","04",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("May","05",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Jun","06",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Jul","07",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Aug","08",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Sep","09",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Oct","10",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Nov","11",datesNr[i])}
for(i in 1:length(datesNr)){datesNr[i]<-gsub("Dec","12",datesNr[i])}

#convert to R date format
datesFinal<-as.Date(datesNr, format="%d %m %Y")

linksPDF<-c()
for(i in 1:length(links)){linksPDF[i]<-gsub(".htm",".pdf", links[i])}
linksFinal<-c()
for(i in 1:length(linksPDF)){linksFinal[i]<-paste0("https://www.bis.org", linksPDF[i], sep="")}

### type of publication ###
## standards - final
type<-rep("standard",length(namesClean))
status<-rep("final",length(namesClean))
documentsBIS_standards_final<-data.frame(namesClean, datesFinal, linksFinal, type, status)

## guidelines - final
type<-rep("guideline",length(namesClean))
status<-rep("final",length(namesClean))
documentsBIS_guidelines_final<-data.frame(namesClean, datesFinal, linksFinal, type, status)

## sound Practices - final
type<-rep("soundPract",length(namesClean))
status<-rep("final",length(namesClean))
documentsBIS_soundPract_final<-data.frame(namesClean, datesFinal, linksFinal, type, status)


#------------------------------------------------------------------------------------------
# CREATE FILE WITH METADATA
documentsBISall<-rbind(documentsBIS_standards_final,
                       documentsBIS_standards_consClosed,
                       documentsBIS_standards_consOpen,
                       documentsBIS_guidelines_final,
                       documentsBIS_guidelines_consClosed,
                       documentsBIS_guidelines_consOpen,
                       documentsBIS_soundPract_final,
                       documentsBIS_soundPract_consClosed)


#------------------------------------------------------------------------------------------
## LOOP THROUGH *ALL* LINKS AND DOWNLOAD PDF DATA

setwd("mypath/data/rawPdfs")

#run loop below; some links do not lead to pdfs. replace them by NA. total 263 files (as of 7 July 2017), of which 4 are only available as .htm
documentsBISall[116,3]<-NA
documentsBISall[144,3]<-NA
documentsBISall[171,3]<-NA
documentsBISall[188,3]<-NA
documentsBISall[262,3]<-NA

documentsToDownload<-documentsBISall

filenames<-c()
for (i in 1:nrow(documentsToDownload)){
  filenames[i]<-paste0(documentsToDownload$datesFinal[i], "_", substr(documentsToDownload$type[i], 1, 5), "_", substr(documentsToDownload$status[i], 1, 5), "_", documentsToDownload$namesClean[i],".pdf",sep="")
}

for(i in 1:length(documentsToDownload$linksFinal)){
  if(!is.na(documentsToDownload$linksFinal)[i]){download.file(as.vector(documentsToDownload$linksFinal)[i], filenames[i], mode="wb")
  }
}

# 4 documents are not available as pdf -> text was hand-extracted from html to .txt

# 4 of the pdfs have to be ocr-ed

#order metadata frame by ascending date
documentsBIS_ordered<-documentsBISall[order(documentsBISall_final$datesFinal, decreasing=F),]


#------------------------------------------------------------------------------------------
## TRANSFORM .PDF TO .TXT

input<-"mypath/data/rawPdfs"

# get filenames
pdfNames <- list.files(path = input, pattern = "pdf",  full.names = TRUE)
pdfNames<-"mypath/data/rawPdfs"

# xpdf needs to be installed if .pdf files are to be transformed to .txt within the R environment
lapply(pdfNames, function(i) system(paste('"/Applications/xpdfbin-mac-3.04/bin64/pdftotext"', paste0('"', i, '"')), wait = FALSE) )

# copy file types into according folders
inputPdf<-"mypath/data/rawPdfs"
inputTxt<-"mypath/data/rawPdfs"

pdfNames <- list.files(path = inputPdf, pattern = "pdf",  full.names = TRUE)
txtNames <- list.files(path = inputTxt, pattern = "txt",  full.names = TRUE)

substr(pdfNames, 97, 101)
substr(txtNames, 97, 101)

outputPdfFinal<-"mypath/data/pdfs"
outputTxtFinal<-"mypath/data/txts"

for(i in 1:length(pdfNames)){
  if(substr(pdfNames[i], 97, 101)=="final"){file.copy(pdfNames[i], outputPdfFinal, recursive=FALSE, copy.mode = TRUE, copy.date = FALSE)
  }
}

for(i in 1:length(txtNames)){
  if(substr(txtNames[i], 97, 101)=="final"){file.copy(txtNames[i], outputTxtFinal, recursive=FALSE, copy.mode = TRUE, copy.date = FALSE)
  }
}


#------------------------------------------------------------------------------------------
## ADD TO DATAFRAME: NUMBER OF DOCUMENTS, PAGES, WORDS AND CHARACTERS PER MONTH/YEAR

# number of documents
nDocs<-rep_len(1, nrow(documentsBIS_ordered))

# number of pages
pdfCorpus <- list.files(path="mypath/data/pdfs", pattern="*.pdf", full.names=T, recursive=FALSE)

nPages<-c()
for (i in 1:length(pdfCorpus)){ 
  nPagesi<-length(pdf_text(pdfCorpus[i]))
  nPages<-rbind(nPages, nPagesi)
}

# include non-pdf documents
documentsBIS_ordered[30,] # 2 pages when copied to Word
documentsBIS_ordered[53,] # 6 pages when copied to Word
documentsBIS_ordered[85,] # 2 pages when copied to Word
documentsBIS_ordered[102,] # 3 pages when copied to Word

nPages_pdfhtml<-c() # htmls: 30, 53, 85, 102; pdfs: 1-29, 31-52, 54-84, 86-101, 103-163
nPages_pdfhtml[c(30,85)]<-2
nPages_pdfhtml[53]<-6
nPages_pdfhtml[102]<-3
nPages_pdfhtml[1:29]<-nPages[1:29]
nPages_pdfhtml[31:52]<-nPages[30:51]
nPages_pdfhtml[54:84]<-nPages[52:82]
nPages_pdfhtml[86:101]<-nPages[83:98]
nPages_pdfhtml[103:163]<-nPages[99:159]

# for the number of words and characters, create clean textcorpora first


#------------------------------------------------------------------------------------------------------------------------------------------------
### PARENTHESIS: CORPUS CREATION AND PROCESSING ###
directoryIn<-"mypath/data/txts"
docs<-Corpus(DirSource(directoryIn, encoding = "UTF-8"), readerControl = list(language = "eng"))

## Create different corpora containing different types of information

# Corpus 1: keep punctuation but remove whitespace, for language complexity analysis
corpus1<-tm_map(docs, stripWhitespace)
directoryOut<-"mypath/data/corpus1"
writeCorpus(corpus1, path=directoryOut, filenames=paste0(substr(dir(directoryIn), 1, nchar(dir(directoryIn))-4),".txt",sep=""))

# Corpus 2: remove punctuation and whitespace and convert to lowercase to count words and for concept and frequent word analysis
corpus2<-tm_map(docs, removePunctuation, preserve_intra_word_dashes = TRUE)
corpus2<-tm_map(corpus2, stripWhitespace)
corpus2<-tm_map(corpus2, content_transformer(tolower))
directoryOut<-"mypath/data/corpus2"
writeCorpus(corpus2, path=directoryOut, filenames=paste0(substr(dir(directoryIn), 1, nchar(dir(directoryIn))-4),".txt",sep=""))

# Corpus 3: additionally stemmed and stopped
corpus3<-tm_map(corpus2, removeWords, stopwords("english"))
corpus3<-tm_map(corpus3, stemDocument, language = "english") #risking becomes risk, operational becomes oper, credit stays credit
directoryOut<-"mypath/data/corpus3"
writeCorpus(corpus3, path=directoryOut, filenames=paste0(substr(dir(directoryIn), 1, nchar(dir(directoryIn))-4),".txt",sep=""))

### END OF PARENTHESIS
#-------------------------------------------------------------------------------------------------------------------------------------


# to count words and characters, read in these files again with scan, which creates a vector with one-word-one-element
txtCleanCorpus <- list.files(path="mypath/data/corpus2/", pattern="*.txt", full.names=F, recursive=FALSE)
directoryCorpus2<-"/Users/marie-jose/Documents/a_NZZ/projects/bankenregulierung/data/corpus2"

# number of words
nWords<-c()
for (i in 1:length(txtCleanCorpus)){ 
  nWordsi<-length(scan(paste0(directoryCorpus2,"/",txtCleanCorpus[i],sep=""), quote=NULL, what="x"))
  nWords<-rbind(nWords, nWordsi)
}

# number of characters
nChars<-c()
for (i in 1:length(txtCleanCorpus)){ 
  nCharsi<-sum(nchar(scan(paste0(directoryOut,"/",txtCleanCorpus[i],sep=""), quote=NULL, what="x")))
  nChars<-rbind(nChars, nCharsi)
}

# number of documents, pages, words, characters 
documentsBIS_size<-cbind(documentsBIS_ordered, nDocs, nPages_pdfhtml, nWords, nChars)


#-------------------------------------------------------------------------------------------------------------------------------------
### ANALYSIS ###


#-------------------------------------------------------------------------------------------------------------------------------------
## 1 AMOUNT OF TEXT PUBLISHED BY YEAR ##

# aggregate by year
dateByYear<-strftime(documentsBIS_size$datesFinal, "%Y")
documentsByYear<-setNames(aggregate(documentsBIS_size$nDocs ~ dateByYear, FUN = sum), c("date", "nDocs"))
pagesByYear<-setNames(aggregate(documentsBIS_size$nPages_pdfhtml ~ dateByYear, FUN = sum), c("date", "nPages"))
wordsByYear<-setNames(aggregate(documentsBIS_size$nWords ~ dateByYear, FUN = sum), c("date", "nWords"))
charsByYear<-setNames(aggregate(documentsBIS_size$nChars ~ dateByYear, FUN=sum), c("date", "nChars"))

documentsBIS_sizeYear<-cbind(documentsByYear, pagesByYear[,2], wordsByYear[,2], charsByYear[,2])
colnames(documentsBIS_sizeYear)<-c("year", "nDocs", "nPages", "nWords", "nChars")

# plot nPages by year
ggplot(pagesByYear, aes(date, nPages)) + 
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
ggsave("nPagesXyear.pdf", plot = last_plot())


#-------------------------------------------------------------------------------------------------------------------------------------
## 2 FREQUENT TERMS AND PARTICULAR CONCEPTS ##

#create term-document-matrix, find frequent terms - with corpus 2, unstopped, unstemmed
dtmatrixC2 <- TermDocumentMatrix(corpus2)
as.matrix(dtmatrixC2[5000:5003, 1:3])

# order by frequency
freq<-rowSums(as.matrix(dtmatrixC2))
freq_ord<-freq[order(freq)]

# create TDM with corpus3 to find all occurences of risk*
dtmatrixC3 <- TermDocumentMatrix(corpus3)

freqC3<-rowSums(as.matrix(dtmatrixC3))
freqC3_ord<-freqC3[order(freqC3)]

wf<-data.frame(term=names(freqC3_ord),occurrences=freqC3_ord)
ggplot(subset(wf, freqC3_ord>3000), aes(term, occurrences)) +
  geom_bar(stat="identity") +
  theme(axis.text.x=element_text(angle=45, hjust=1))

wordcloud(names(freqC3),freqC3, min.freq=1900)

# this is how often "risk*" appears in every document
nRisk<-c()
for (i in 1:163){
  nRisk[i]<-as.matrix(dtmatrixC3[Terms(dtmatrixC3)=="risk",])[i]
}

dateByYear<-strftime(documentsBIS_augm$datesFinal, "%Y")
nRiskByYear<-setNames(aggregate(documentsBIS_augm$nRisk ~ dateByYear, FUN = sum), c("date", "nRisk"))

###### !! Spot-checks and additional analyses show that the tm package and its TDM miss some occurences of words (e.g. risk) for no apparent reason.
###### !! We used bash for our text analysis R for data processing and visualisation. 

# get bash results for the number of "risk" occurences per file, corpus  3
riskPerFile_unix <- read_delim("mypath/data/unixResults/riskPerFile_unix.txt", "\t", escape_double = FALSE, trim_ws = TRUE)

# get bash results for the number of words per file, corpus2
wordsPerFile_unix <- read_delim("~/Documents/a_NZZ/projects/bankenregulierung/data/unixResults/nWordsPerFile_unix.txt", "\t", escape_double = FALSE, trim_ws = TRUE)

# processing: nRisk per nWords, per year
riskPerFile_unix$nRiskProp<-100*(riskPerFile_unix$risk/wordsPerFile_unix$nWords)
year<-substr(riskPerFile_unix$text, 1, 4)
riskPerYear<-as.data.frame(cbind(year, "risk"=riskPerFile_unix$nRiskProp))
riskPerYear$risk<-as.numeric(as.character(riskPerYear$risk))
riskPerYear_agg<-setNames(aggregate(riskPerYear$risk ~ riskPerYear$year, FUN=mean, na.rm=T), c("year", "risk"))

# aggregated; plot nRisk by year
ggplot(riskPerYear_agg, aes(year,risk)) + 
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

# use bash to find frequence of terms, collocations, n-grams


#-------------------------------------------------------------------------------------------------------------------------------------
## 3 RISK TYPES OVER TIME
# use bash to count the occurence of the most frequent risk types per file
riskTypesPerFile_unix <- read_delim("~/Documents/a_NZZ/projects/bankenregulierung/data/unixResults/riskTypesPerFileWithUnix_unix.txt", "\t", escape_double = FALSE, trim_ws = TRUE)

#risk type occurences as a proportion of nWords 
riskTypesPerFile_unix$creditRiskProp<-100*(riskTypesPerFile_unix$creditRisk/wordsPerFile_unix$nWords)
riskTypesPerFile_unix$marketRiskProp<-100*(riskTypesPerFile_unix$marketRisk/wordsPerFile_unix$nWords)
riskTypesPerFile_unix$operationalRiskProp<-100*(riskTypesPerFile_unix$operationalRisk/wordsPerFile_unix$nWords)
riskTypesPerFile_unix$liquidityRiskProp<-100*(riskTypesPerFile_unix$liquidityRisk/wordsPerFile_unix$nWords)
riskTypesPerFile_unix$interestRateRiskProp<-100*(riskTypesPerFile_unix$interestRateRisk/wordsPerFile_unix$nWords)
riskTypesPerFile_unix$systemicRiskProp<-100*(riskTypesPerFile_unix$systemicRisk/wordsPerFile_unix$nWords)

riskTypesPerFile_red<-riskTypesPerFile_unix[,-c(2:7, 13)]

year<-substr(riskTypesPerFile_red$text, 1, 4)
riskTypesPerYear<-as.data.frame(cbind(year, riskTypesPerFile_red))
riskTypesPerYear_agg<-setNames(aggregate(riskTypesPerYear[,-c(1:2)], by=list(year= riskTypesPerYear$year), FUN=mean), c("year", "Kreditrisiko", "Marktrisiko", "operationelles Risiko", "Liquiditätsrisiko","Zinsrisiko"))
riskTypesPerYear_agg$year<-as.numeric(as.character(riskTypesPerYear_agg$year))
riskTypesPerYear_agg_augm<-rbind(riskTypesPerYear_agg[1,],
                                 c(1976, 0,0,0,0,0),
                                 c(1977, 0,0,0,0,0),
                                 riskTypesPerYear_agg[2:3,],
                                 c(1980, 0,0,0,0,0),
                                 c(1981, 0,0,0,0,0),
                                 riskTypesPerYear_agg[4:5,],
                                 c(1984, 0,0,0,0,0),
                                 c(1985, 0,0,0,0,0),
                                 riskTypesPerYear_agg[6,],
                                 c(1987, 0,0,0,0,0),
                                 riskTypesPerYear_agg[7,],
                                 c(1989, 0,0,0,0,0),
                                 riskTypesPerYear_agg[8:10,],
                                 c(1993, 0,0,0,0,0),
                                 riskTypesPerYear_agg[11:34,])

riskTypesPerYear_long<-reshape(riskTypesPerYear_agg_augm, varying=colnames(riskTypesPerYear_agg_augm)[2:length(colnames(riskTypesPerYear_agg_augm))], v.names="prop", timevar="Risikotyp", times=colnames(riskTypesPerYear_agg_augm)[2:length(colnames(riskTypesPerYear_agg_augm))], direction="long")

#change order of levels for barplot: credit risk > market risk > operational risk > rate risk > liquidity risk > systemic risk
riskTypesPerYear_long$Risikotyp<-as.factor(riskTypesPerYear_long$Risikotyp)
levels(riskTypesPerYear_long$Risikotyp)
riskTypesPerYear_long$Risikotyp <- factor(riskTypesPerYear_long$Risikotyp,levels(riskTypesPerYear_long$Risikotyp)[c(4,2,3,5,1)])
riskTypesPerYear_long$year<-as.factor(riskTypesPerYear_long$year)

##############FINAL GRAPH
ggplot(riskTypesPerYear_long, aes(year,prop, group=Risikotyp, fill=Risikotyp)) + 
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  theme(axis.title.x = element_blank())+
  ylab("Mittlerer Anteil an allen Wörtern pro Dokument, in Prozent")
ggsave("riskTypeXyear.pdf", plot = last_plot(), width=16, height=9)
ggsave("riskTypeXyear_mobile.pdf", plot = last_plot(), width=9, height=9)
##############FINAL GRAPH


#-------------------------------------------------------------------------------------------------------------------------------------
## 4 MODAL VERBS OVER TIME:
# use bash to count the occurence of modal verbs / constructions of interest, per file
modVerbsPerFile_unix <- read_delim("~/Documents/a_NZZ/projects/bankenregulierung/data/unixResults/modVerbsPerFileWithUnix_unix.txt", "\t", escape_double = FALSE, trim_ws = TRUE)
modVerbsRelPerFile_3cat<-modVerbsPerFile_unix

# create categories according to degree of obigation expressed by construction and morphological variants
modVerbsRelPerFile_3cat$strong<-modVerbsPerFile_unix$must+modVerbsPerFile_unix$hasTo+modVerbsPerFile_unix$haveTo
modVerbsRelPerFile_3cat$middle<-modVerbsPerFile_unix$needTo+modVerbsPerFile_unix$needsTo+modVerbsPerFile_unix$needN+
  modVerbsPerFile_unix$isRequiredTo+modVerbsPerFile_unix$areRequiredTo+modVerbsPerFile_unix$isRequiredToN+modVerbsPerFile_unix$areRequiredToN+
  modVerbsPerFile_unix$shall
modVerbsRelPerFile_3cat$soft<-modVerbsPerFile_unix$should

# reduce to the verbs that we want to have in the plot
modVerbsRelPerFile_3cat_red<-modVerbsRelPerFile_3cat[,c(1,45:47)]

# calculate sum of all these verbs
allTheseModVerbs_3cat<-rowSums(modVerbsRelPerFile_3cat_red[, 2:4])

# calculate proportion of nWords
modVerbsRelPerFile_3cat_red$strongVsAll<-100*(modVerbsRelPerFile_3cat_red$strong/allTheseModVerbs_3cat)
modVerbsRelPerFile_3cat_red$middleVsAll<-100*(modVerbsRelPerFile_3cat_red$middle/allTheseModVerbs_3cat)
modVerbsRelPerFile_3cat_red$softVsAll<-100*(modVerbsRelPerFile_3cat_red$soft/allTheseModVerbs_3cat)

modVerbsRelPerFile_3cat_redmore<-modVerbsRelPerFile_3cat_red[,-c(2:4)]

year<-substr(modVerbsRelPerFile_3cat_redmore$text, 1, 4)
modVerbsRelPerYear_3cat<-as.data.frame(cbind(year, modVerbsRelPerFile_3cat_redmore))
modVerbsRelPerYear_3cat_agg<-setNames(aggregate(modVerbsRelPerYear_3cat[,-c(1:2)], by=list(year= modVerbsRelPerYear_3cat$year), FUN=mean, na.rm=T), c("year", "must, have/has to", "shall, need/needs to, is/are required to", "should"))
modVerbsRelPerYear_3cat_agg$year<-as.numeric(as.character(modVerbsRelPerYear_3cat_agg$year))
modVerbsRelPerYear_3cat_agg_augm<-rbind(modVerbsRelPerYear_3cat_agg[1,],
                                        c(1976, 0,0,0,0,0),
                                        c(1977, 0,0,0,0,0),
                                        modVerbsRelPerYear_3cat_agg[2:3,],
                                        c(1980, 0,0,0,0,0),
                                        c(1981, 0,0,0,0,0),
                                        modVerbsRelPerYear_3cat_agg[4:5,],
                                        c(1984, 0,0,0,0,0),
                                        c(1985, 0,0,0,0,0),
                                        modVerbsRelPerYear_3cat_agg[6,],
                                        c(1987, 0,0,0,0,0),
                                        modVerbsRelPerYear_3cat_agg[7,],
                                        c(1989, 0,0,0,0,0),
                                        modVerbsRelPerYear_3cat_agg[8:10,],
                                        c(1993, 0,0,0,0,0),
                                        modVerbsRelPerYear_3cat_agg[11:34,])

modVerbsRelPerYear_3cat_long<-reshape(modVerbsRelPerYear_3cat_agg_augm, varying=colnames(modVerbsRelPerYear_3cat_agg_augm)[2:length(colnames(modVerbsRelPerYear_3cat_agg_augm))], v.names="prop", timevar="verb", times=colnames(modVerbsRelPerYear_3cat_agg_augm)[2:length(colnames(modVerbsRelPerYear_3cat_agg_augm))], direction="long")

#reorder order of appearance of levels of the factor verb
modVerbsRelPerYear_3cat_long$verb<-as.factor(modVerbsRelPerYear_3cat_long$verb)
print(levels(modVerbsRelPerYear_3cat_long$verb))
modVerbsRelPerYear_3cat_long$verb <- factor(modVerbsRelPerYear_3cat_long$verb, levels(modVerbsRelPerYear_3cat_long$verb)[c(1,2,3)])
modVerbsRelPerYear_3cat_long$year<-as.factor(modVerbsRelPerYear_3cat_long$year)

##############FINAL GRAPH
ggplot(modVerbsRelPerYear_3cat_long, aes(year,prop, group=verb, fill=verb)) +
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  theme(axis.title.x = element_blank())+
  ylab("Mittlerer Anteil pro Dokument, in Prozent")
ggsave("modalVerbsRelativeXyear_3cat.pdf", plot = last_plot(), width=16, height=9)
ggsave("modalVerbsRelativeXyear_3cat_mobile.pdf", plot = last_plot(), width=9, height=9)
##############FINAL GRAPH


#-------------------------------------------------------------------------------------------------------------------------------------
## 5 REGULATORY INSTRUMENTS OVER TIME:
# use bash to count the occurence of the instruments of interest, per file
instrumentsPerFile_unix <- read_delim("~/Documents/a_NZZ/projects/bankenregulierung/data/unixResults/instrumentsWithUnix_unix.txt", "\t", escape_double = FALSE, trim_ws = TRUE)

#categorize instrument types
instrumentsPerFile_unix$capitalRequirements<-instrumentsPerFile_unix$capReq
instrumentsPerFile_unix$otherCapital<-instrumentsPerFile_unix$leveraRat+instrumentsPerFile_unix$lr+
  instrumentsPerFile_unix$totalLossAbsCapi+instrumentsPerFile_unix$totalLossAbsCapy+instrumentsPerFile_unix$tlac+
  instrumentsPerFile_unix$countercBuff+instrumentsPerFile_unix$countercCapBuff+instrumentsPerFile_unix$consBuff
instrumentsPerFile_unix$supervision<-instrumentsPerFile_unix$supervRev#+instrumentsPerFile_unix$stressTest
instrumentsPerFile_unix$marketDiscipline<-instrumentsPerFile_unix$markDisc#+instrumentsPerFile_unix$disclReq+instrumentsPerFile_unix$disclStand
instrumentsPerFile_unix$liquidity<-instrumentsPerFile_unix$liquiCovRat+instrumentsPerFile_unix$lcr+
  instrumentsPerFile_unix$netStabFundRat+instrumentsPerFile_unix$nsfr

#calculate proportion vs nWords per file
instrumentsPerFile_unix$capitalRequirementsProp<-100*(instrumentsPerFile_unix$capitalRequirements/wordsPerFile_unix$nWords)
instrumentsPerFile_unix$otherCapitalProp<-100*(instrumentsPerFile_unix$otherCapital/wordsPerFile_unix$nWords)
instrumentsPerFile_unix$supervisionProp<-100*(instrumentsPerFile_unix$supervision/wordsPerFile_unix$nWords)
instrumentsPerFile_unix$marketDisciplineProp<-100*(instrumentsPerFile_unix$marketDiscipline/wordsPerFile_unix$nWords)
instrumentsPerFile_unix$liquidityProp<-100*(instrumentsPerFile_unix$liquidity/wordsPerFile_unix$nWords)

instrumentsPerFile_red<-instrumentsPerFile_unix[,-c(2:33,35)] #risk-weighted assets raus, in absprache mit jürg

year<-substr(instrumentsPerFile_red$text, 1, 4)
instrumentsPerYear<-as.data.frame(cbind(year, instrumentsPerFile_red))
instrumentsPerYear_agg<-setNames(aggregate(instrumentsPerYear[,-c(1:2)], by=list(year= instrumentsPerYear$year), FUN=mean), c("year", "Kapitalvorschriften", "Kapitalvorschrfiten, neue Formen", "Aufsichtliche Überprüfungsverfahren","Marktdisziplin", "Liquiditätsvorschriften"))

#add missing years
instrumentsPerYear_agg$year<-as.numeric(as.character(instrumentsPerYear_agg$year))
instrumentsPerYear_agg_augm<-rbind(instrumentsPerYear_agg[1,],
                                   c(1976, 0,0,0,0,0),
                                   c(1977, 0,0,0,0,0),
                                   instrumentsPerYear_agg[2:3,],
                                   c(1980, 0,0,0,0,0),
                                   c(1981, 0,0,0,0,0),
                                   instrumentsPerYear_agg[4:5,],
                                   c(1984, 0,0,0,0,0),
                                   c(1985, 0,0,0,0,0),
                                   instrumentsPerYear_agg[6,],
                                   c(1987, 0,0,0,0,0),
                                   instrumentsPerYear_agg[7,],
                                   c(1989, 0,0,0,0,0),
                                   instrumentsPerYear_agg[8:10,],
                                   c(1993, 0,0,0,0,0),
                                   instrumentsPerYear_agg[11:34,])

instrumentsPerYear_long<-reshape(instrumentsPerYear_agg_augm, varying=colnames(instrumentsPerYear_agg_augm)[2:length(colnames(instrumentsPerYear_agg_augm))], v.names="prop", timevar="instrumentType", times=colnames(instrumentsPerYear_agg_augm)[2:length(colnames(instrumentsPerYear_agg_augm))], direction="long")

#change order of levels for barplot: credit risk > market risk > operational risk > rate risk > liquidity risk > systemic risk
instrumentsPerYear_long$instrumentType<-as.factor(instrumentsPerYear_long$instrumentType)
levels(instrumentsPerYear_long$instrumentType)
instrumentsPerYear_long$instrumentType <- factor(instrumentsPerYear_long$instrumentType,levels(instrumentsPerYear_long$instrumentType)[c(2,3,1,5,4)])

#plot nInstrument by year
ggplot(instrumentsPerYear_long, aes(year,prop, group=instrumentType, fill=instrumentType)) + 
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  theme(axis.title.x = element_blank())+
  ylab("Mittlerer Anteil an allen Wörtern pro Dokument, in Prozent")
ggsave("instrumentTypeXyear.pdf", plot = last_plot(), width=16, height=9)
ggsave("instrumentTypeXyear_mobile.pdf", plot = last_plot(), width=9, height=9)


#-------------------------------------------------------------------------------------------------------------------------------------
## 6 LANGUAGE COMPLEXITY ANALYSIS ##

# removed from article as the results on syntactic and lexical complexity / richness were not particularly interesting