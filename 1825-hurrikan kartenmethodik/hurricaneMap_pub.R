### MISE EN PLACE ###

library(dplyr)
library(Hmisc)
library(ggplot2)
library(barcode)
library(lattice)
library(graphics)
library(svglite)

setwd("/Users/marie-jose/Documents/a_NZZ/storytellingTeam/methoden_tests/graphics")

#define and view colors
cols_seq8<-c("#191d63", "#463b75", "#6b5c88", "#8f819a", "#b3a5ad", "#d8ccbf", "#fdf4d1")
cols_div8<-c("#b23c39",  "#be5c5a", "#cb7c7b",  "#d89d9c",  "#aeb0c8",  "#9395b6",  "#787ba4",  "#5e6192")
colNA<-"#c9c8ba"
pie(rep(1/8,8),col=c(cols_seq8, colNA))
pie(rep(1/8,8),col=c(cols_div8))


#------------------------------------------------------------------------------------------------------------------------------
### DATA ACQUISITION  ###

# create sample data from different distributions
set.seed(85)
uniformSpl<-runif(100, 1, 20)
normalSpl<-rnorm(100, 10, 5)
skewedLSpl<-rbeta(100, 9, 2)
skewedRSpl<-rbeta(100, 2, 9)

# get overview (descriptive stats)
summary(uniformSpl)
summary(normalSpl)
summary(skewedLSpl)
summary(skewedRSpl)

# get overview (histogram)
hist(uniformSpl)
hist(normalSpl)
hist(skewedLSpl)
hist(skewedRSpl)

# or, read in real data
elo<-read.table("/Users/marie-jose/Documents/a_NZZ/projects/a_2018/WMfussball/eloRating_final_red.csv", sep=";", header=T)
myDistribution<-read.csv("/Users/marie-jose/Desktop/Mehrausgaben.csv", sep=";")
myDistribution<-myDistribution$wert

#------------------------------------------------------------------------------------------------------------------------------
### DATA PROCESSING AND VISUALIZATION ###

# create buckets using different methods

# attribute one of the random samples above or your own data to myDistribution 
myDistribution<-elo$Elo.Score


## method: "kmeans" - maximize between-group and minimize within-group variability ~ maximize differences in the data. 
clusters<-5
set.seed(1)
clust <- kmeans(myDistribution,clusters)$cluster
combined <- as.data.frame(cbind(myDistribution,clust))
brk <- sort(aggregate(combined[,1], list(combined[,2]), max)[,2]) # brk always belongs to the lower interval -> exclude from higher interval (if you program a for-loop - if you use cut, the function does it for you)
brk
start<-min(myDistribution)
start
intervals<-cut(myDistribution, breaks=c(start, brk), include.lowest=T) 
intervals

# visualize
pdf("eloXkmeans.pdf", width=12, height=6) #adapt filename
stripchart(myDistribution, pch="|", xaxt="n")
abline(v=c(start, brk), col="grey")
axis(1, at=c(start, brk), labels=round(c(start, brk),2)) 
dev.off()


## method: intervals of equal length 
steps<-(max(myDistribution)-min(myDistribution))/8
brk<-seq(min(myDistribution)+steps, max(myDistribution), steps)
start<-min(myDistribution)
intervals<-cut(myDistribution, breaks=c(start, brk), include.lowest=T) 
intervals

# visualize
pdf("eloXequallength.pdf", width=12, height=6) #adapt filename
stripchart(myDistribution, pch="|", xaxt="n")
abline(v=c(start, brk), col="grey")
axis(1, at=c(start, brk), labels=round(c(start, brk),2)) 
dev.off()


## method: intevals with equal numbers of datapoints
intervals<-cut_number(myDistribution, n = 8) #cut_number makes n groups with (approximately) equal numbers of observations
intervals
start<-min(myDistribution)
brk_all<-strsplit(as.character(unique(intervals)),",") %>%
  unlist() %>%
  as.character() %>%
  gsub("\\]|\\(|\\)|\\[","",.)%>%
  as.numeric(as.character(.)) %>%
  unique() %>%
  sort()
brk<-brk_all[2:length(brk_all)]

# visualize
pdf("eloXquantile.pdf", width=12, height=6) #adapt filename
stripchart(myDistribution, pch="|", xaxt="n")
abline(v=c(start, brk), col="grey")
axis(1, at=c(start, brk), labels=round(c(start, brk),2)) 
dev.off()


## visualize density of your current data (this may help spotting binomially distributed data or the like)
pdf("elo_density.pdf") #adapt filename
densityplot(myDistribution)
dev.off()

ggplot(combined, aes(x=myDistribution)) + 
  geom_histogram(aes(y = ..density..), color="black", fill=NA) +
  geom_density(color="blue")
ggsave("elo_hist.pdf") #adapt filename


## create and save a legend in the form of a stacked bar

#set your working directory
setwd("/Users/marie-jose/NZZ-Mediengruppe/NZZ\ Storytelling\ -\ Dokumente/Vorlagen/R-scripts/graphics")

# create dataframe with intervals, interval lengths, colors (very hacky and not yet abstracted - here, for 8 intervals)
cols<-c("#d64b47","#db5e55","#e06f63","#e47f72","#e78f81","#ea9f90","#ecaea0","#eebeb0") #add a sequential/diverging scale of the same length as your number of intervals
legend_ext<-data.frame(allIntervals=levels(intervals), cols, values=c(brk[1]-start, brk[2]-brk[1], brk[3]-brk[2], brk[4]-brk[3], brk[5]-brk[4], brk[6]-brk[5], brk[7]-brk[6], brk[8]-brk[7]))

# check if levels are in the right order (bucket that is supposed to appear at the top - usually the higherst number - should be first in list)
levels(legend_ext$allIntervals)
# if necessary, relevel
legend_ext$allIntervals <- factor(legend_ext$allIntervals,levels(legend_ext$allIntervals)[c(4,2,3,1,7,6,5,8)]) #change order (top-bucket first in list) of levels for accurate order of appearance in stacked bar

#plot
ggplot(legend_ext, aes(as.factor(1), values, fill=allIntervals)) + 
  geom_bar(stat="identity", position="stack") +
  scale_fill_manual(values=rev(as.character(legend_ext$cols))) +
  scale_y_continuous(breaks=c(0,legend_ext$values[1],
                              legend_ext$values[1]+legend_ext$values[2],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5]+legend_ext$values[6],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5]+legend_ext$values[6]+legend_ext$values[7],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5]+legend_ext$values[6]+legend_ext$values[7]+legend_ext$values[8]),
                     labels=c(start, brk)) +
  theme(
    panel.background = element_blank(),
    legend.title=element_blank(),
    axis.title=element_blank(),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank(),
    axis.text.y = element_text(family="GT America", color="#6E6E7E", size=11)
  )
#save
ggsave("mylegend.svg", width=4, height=14)



