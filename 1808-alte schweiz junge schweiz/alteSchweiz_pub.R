# NZZ Storytelling, script for the following main article: 
# https://www.nzz.ch/schweiz/schweiz-alterung-gemeinden-ld.1351100
# questions and comments: alexandra.kohler@nzz.ch or marie-jose.kolly@nzz.ch



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### MISE EN PLACE ###

# Load libraries
library(dplyr)
library(tibble)
library(ggplot2)
library(tidyr)
library(rgdal)
library(gridExtra)
library(svglite)

# Define colors
vizCols<-c("#191d63", "#d6b222", "#656565", "#e08b63", "#2e6e71", "#dd5b6c", "#1eafc7", "#9a8700", "#1f9877")
vizColsTransparent<-paste0(vizCols, "77") 
mapCols<-c("#191D63", "#463C75", "#72648C", "#9A8BA0", "#C2B5B4", "#EAE0C8", "#FDF4D1")
mapCols6<-c("#8440a3", "#9a63b2", "#ae84c1", "#c2a6cf", "#d5c9de", "#e6d9c7")

# Set writing directory
setwd("mypath/graphics")



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### READ, CLEAN AND PROCESS DATA ###

## Read age and municipality-category data
AlterCH<-read.csv("mypath/data/Gemeinden_Kantone_Alter.csv", header=T, sep=";")
AlterCH[AlterCH$Medianalter=="…",]
AlterCH<-as.data.frame(lapply(AlterCH, function(y) gsub("…", "NA", y)))

cat_gem<-read.csv("mypath/data/gemeinden_31122016_cat1to6.csv", header=T, sep=";")


## Read and process data on immigration
canton<-c("AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH")
canton_full=c("Aargau", "Appenzell A. Rh.", "Appenzell I. Rh.", "Basel-Land", "Basel-Stadt", "Bern", "Freiburg", "Genf", 
              "Glarus", "Graubünden", "Jura", "Luzern", "Neuenburg", "Nidwalden", "Obwalden", "Schaffhausen", "Schwyz", "Solothurn", 
              "St. Gallen", "Tessin", "Thurgau", "Uri", "Waadt", "Wallis", "Zug", "Zürich")

# Immigration saldo
saldoCanton<-data.frame()
for (j in 2008:2016){
  for (i in canton){
    table<- read_excel(paste0("mypath/data/zuwanderung/saldo/3-10-Bew-In-Out-Tot-Kat-d-12Mt-",paste0(j),"-12.xlsx"), 
                       sheet = i)
    zunahme<-as.numeric(as.character(table[which(table$`3-10`=="Total Zunahme"),2]))
    abnahme<-as.numeric(as.character(table[which(table$`3-10`=="Total Abnahme"),2]))
    saldo<-zunahme-abnahme
    saldoi<-cbind("kanton"=paste0(i), "year"=paste0(j), "saldo"=saldo)
    saldoCanton<-rbind(saldoCanton, saldoi)
  }
}

# Immigration by age and origin
ageOriginCanton<-data.frame()
for (j in 2008:2016){
  for (i in canton){
    table<- read_excel(paste0("mypath/data/zuwanderung/staendigeWohnbev/nachAlter_Herkunft_Kt/2-21-Best-Stae-Alter-d-",paste0(j),"-12.xlsx"), 
                       sheet = i)
    age05<-as.numeric(as.character(table[which(table$`2-21`=="Gesamttotal"),3]))
    age615<-as.numeric(as.character(table[which(table$`2-21`=="Gesamttotal"),6]))
    age1617<-as.numeric(as.character(table[which(table$`2-21`=="Gesamttotal"),9]))
    age1864<-as.numeric(as.character(table[which(table$`2-21`=="Gesamttotal"),12]))
    age65plus<-as.numeric(as.character(table[which(table$`2-21`=="Gesamttotal"),15]))
    yearCantoni<-cbind("kanton"=paste0(i), "year"=paste0(j), age05, age615, age1617, age1864, age65plus)
    ageOriginCanton<-rbind(ageOriginCanton, yearCantoni)
  }
}



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### PROCESS DATA ###

## Age and population growth
alterCH<-merge(AlterCH, cat_gem, by.x = "bfs_nr", by.y="bfs_nr")

# Calculate age development and population growth (in %) between 2016 and 1970
agePopDevelopment<- alterCH%>% 
  group_by(bfs_nr, name.x, kanton, kanton_kurz, groessenklasse, stadt_land, staedtischer_charakter, gemeinde1, gemeinde2, sprachgebiet) %>%
  summarize(ageDevelopment=Medianalter[Jahr==2016]-Medianalter[Jahr==1970],
            populationGrowth=100*(bewohner[Jahr==2016]-bewohner[Jahr==1970])/bewohner[Jahr==1970],
            bewohner2016=bewohner[Jahr==2016])


## Immigration

# Canton ranking regarding immigration saldo between 2008 and 2016
saldoCanton$saldo<-as.numeric(as.character(saldoCanton$saldo))

saldoCanton_mean<-saldoCanton %>% 
  group_by(kanton) %>%
  summarise(meanSaldo=mean(saldo)) %>%
  left_join(inhabitants, by=c("kanton" = "kuerzel")) %>%
  mutate(propMeanSaldo=(meanSaldo/bev2016)*100) %>%
  arrange(desc(propMeanSaldo))

# Canton ranking regarding immigration by age group
ageOriginCanton[,c(3:7)]<-sapply(ageOriginCanton[,c(3:7)], as.character)
ageOriginCanton[,c(3:7)]<-sapply(ageOriginCanton[,c(3:7)], as.numeric)

ageOriginCanton_augm<-ageOriginCanton %>%
  left_join(inhabitants_augm, by=c("kanton"="kuerzel")) %>%
  group_by(kanton, bev2016) %>%
  summarise(meanAge05=mean(age05), meanAge615=mean(age615), meanAge1617=mean(age1617), meanAge1864=mean(age1864), meanAge65plus=mean(age65plus)) %>%
  mutate(propAge05=100*meanAge05/bev2016, propAge615=100*meanAge615/bev2016, propAge1617=100*meanAge1617/bev2016, propAge1864=100*meanAge1864/bev2016, propAge65plus=100*meanAge65plus/bev2016) %>%
  arrange(desc(propAge1864))

ageOriginCanton_augm %>% print(., n=26)



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### VISUALIZE DATA ###

## Scatterplots: age development vs. population growth in different types of municipalities

# Age development vs population growth, colored by linguistic region
ggplot(agePopDevelopment, aes(ageDevelopment, populationGrowth, label=name.x, col=as.factor(sprachgebiet))) + 
  geom_point() +
  scale_color_manual(values=vizColsTransparent[1:4])

# Facetted by groessenklasse
ggplot(agePopDevelopment, aes(ageDevelopment, populationGrowth, label=name.x, col=as.factor(sprachgebiet))) + 
  geom_point() +
  facet_wrap(~groessenklasse) +
  scale_color_manual(values=vizColsTransparent[1:4])

# Facetted by gemeinde1
ggplot(agePopDevelopment, aes(ageDevelopment, populationGrowth, label=name.x, col=as.factor(sprachgebiet))) + 
  geom_point() +
  facet_wrap(~gemeinde1) +
  scale_color_manual(values=vizColsTransparent[1:4])


## Create maps
year<-c(1970, 1980, 1990, 2000, 2010, 2016)

# Read shapefiles
shapeCH<-readOGR("/Users/marie-jose/Documents/a_NZZ/R/shapeCH/ggg_2016vz/shp/g2g16vz.shp") #VZ = volkszählung = stand ende dezember 2016, ohne VZ = stand anfang januar 2016 
shapeCH<-shapeCH[order(as.numeric(as.character(shapeCH$GMDNR)), decreasing=F),]
shapeCH_fort<-fortify(shapeCH)

AlterCH$Medianalter<-as.numeric(as.character(AlterCH$Medianalter))

# One map per year

# Classify data
cols<-as.character(rev(mapCols))
clusters<-7
set.seed(1)
AlterCH$Medianalter<-as.numeric(as.character(AlterCH$Medianalter))
clust <- kmeans(AlterCH$Medianalter[which(!is.na(AlterCH$Medianalter))],clusters)$cluster #kmeans(AlterCH$Medianalter,clusters)$cluster 
combined <- as.data.frame(cbind(AlterCH$Medianalter[which(!is.na(AlterCH$Medianalter))],clust)) #as.data.frame(cbind(AlterCH$Medianalter,clust))
brk <- sort(aggregate(combined[,1], list(combined[,2]), max)[,2])
start<-min(AlterCH$Medianalter[which(!is.na(AlterCH$Medianalter))])

# Legend for 7 buckets
allIntervals<-c(paste0("[",round(start,digits=1),",",round(brk[1], digits=1),")"), 
                paste0("[",round(brk[1], digits=1),",",round(brk[2], digits=1),")"),
                paste0("[",round(brk[2], digits=1),",",round(brk[3], digits=1), ")"),
                paste0("[",round(brk[3], digits=1),",",round(brk[4], digits=1),")"),
                paste0("[",round(brk[4], digits=1), ",",round(brk[5], digits=1),")"),
                paste0("[",round(brk[5], digits=1), ",",round(brk[6], digits=1),")"),
                paste0("[",round(brk[6], digits=1), ",",round(brk[7], digits=1),")"))

legend<-data.frame(allIntervals, cols)
lmts<-c(paste0(legend$cols[1]), paste0(legend$cols[2]), paste0(legend$cols[3]), paste0(legend$cols[4]), paste0(legend$cols[5]), 
        paste0(legend$cols[6]), paste0(legend$cols[7])) #see in plot - this forces R to show all levels in the legend, even if not all appear in the map

# loop over years to create one age-map per year
plot_list_medianalter = list()
for(y in 1:length(year)){
  ageData<-filter(AlterCH, Jahr==year[y])
  ageData[,c(2,7)] <- sapply(ageData[,c(2,7)], as.character)
  ageData[,c(2,7)] <- sapply(ageData[,c(2,7)], as.numeric)
  #ageData<-ageData[-which(!(as.numeric(as.character(ageData$bfs_nr)) %in% shapeCH_red$GMDNR)),]
  ageData<-ageData[order(as.numeric(as.character(ageData$bfs_nr)), decreasing=F),]
  #create id-variable that will match the id-variable in shapeCH_fort, as the exact MDNR is, there, replaced by 1:length(GMDNR)
  idvar<-c(0:(nrow(ageData)-1))
  ageData_age<-ageData$Medianalter
  #create intervals
  intervals<-c()
  for (i in 1:length(ageData_age)){
    for (j in 1:length(brk)){
      ifelse(ageData_age[i]<brk[1], intervals[i]<-paste0("[",round(start,digits=1),",",round(brk[1], digits=1),")"), 
             ifelse(ageData_age[i]>=brk[j] & ageData_age[i]<brk[j+1], intervals[i]<-paste0("[",round(brk[j], digits=1),",",round(brk[j+1], digits=1),")"),
                    ifelse(ageData_age[i]==brk[length(brk)], intervals[i]<-paste0("[",round(brk[length(brk)-1], digits=1),",",round(brk[length(brk)], digits=1),")"),
                           ifelse(is.na(ageData_age[i]),intervals[i]<-NA,
                                  j+1))))
    }
  }
  intervals_ord<-unique(intervals)[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals)))))]
  #attribute colors
  colInterval<-c()
  for (i in 1:length(intervals)){
    for (j in 1:length(brk)){
      ifelse(is.na(intervals[i]), colInterval[i]<-colNA, 
             ifelse(intervals[i]==allIntervals[j], colInterval[i]<-cols[j], #if we relate to intervals_ord, here, we get problems in cases where not the entire scale is used 
                    j+1))
    }
  }
  #create final dataframe
  ageData_final<-as.data.frame(cbind(ageData_age, idvar, intervals, colInterval)) 
  #plot
  ploty<-ggplot() + 
    geom_map(data = ageData_final, aes(map_id = idvar, fill = paste0(
      as.character(colInterval))), map = shapeCH_fort, colour="white", lwd=0.005) + 
    expand_limits(x = shapeCH_fort$long, y = shapeCH_fort$lat) + 
    coord_equal() +
    ggtitle(year[y]) +
    #scale_fill_identity("Legend", labels = legend$allIntervals, breaks=legend$cols, guide = "none") + #enable this and disable the next line if you do not want the legend
    scale_fill_identity("Legend", labels = legend$allIntervals, breaks=legend$cols, limits=lmts, guide = guide_legend(direction="horizontal", label.position = "bottom", keywidth=3, keyheight=.6, nrow=1)) +
    theme(line = element_blank(),
          legend.title = element_blank(),
          plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5),
          panel.background = element_blank(),
          axis.title=element_blank(),
          axis.text=element_blank(),
          axis.ticks=element_blank(),
          legend.position="bottom",
          legend.text=element_text(family="GT America", color="#6E6E7E", size=11)) 
  plot_list_medianalter[[y]] <- ploty
}


#legend
legend_ext<-data.frame(legend, values=c(brk[1]-start, brk[2]-brk[1], brk[3]-brk[2], brk[4]-brk[3], brk[5]-brk[4], brk[6]-brk[5], brk[7]-brk[6]))

# enable to relevel
legend_ext$allIntervals <- factor(legend_ext$allIntervals,levels(legend_ext$allIntervals)[c(7,6,5,4,3,2,1)]) #change order of levels for accurate order of appearance in stacked bar

ggplot(legend_ext, aes(as.factor(1), values, fill=allIntervals)) + #changed l
  geom_bar(stat="identity", position="stack") +
  scale_fill_manual(values=rev(as.character(legend_ext$cols)), guide=F) +
  scale_y_continuous(breaks=c(0,legend_ext$values[1],
                              legend_ext$values[1]+legend_ext$values[2],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5]+legend_ext$values[6],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5]+legend_ext$values[6]+legend_ext$values[7]),
                     labels=c(start,brk)) +
  theme(
    panel.background = element_blank(),
    legend.title=element_blank(),
    axis.title=element_blank(),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank(),
    axis.text.y = element_text(family="GT America", color="#6E6E7E", size=11)
  )


# Map the age development between 2016 and 1970
diff<-year2016$Medianalter-year1970$Medianalter

# Classify data
cols<-as.character(rev(mapCols6))
clusters<-6
set.seed(1)
clust <- kmeans(diff[which(!is.na(diff))],clusters)$cluster 
combined <- as.data.frame(cbind(diff[which(!is.na(diff))],clust)) 
brk <- sort(aggregate(combined[,1], list(combined[,2]), max)[,2]) 
brk[1]<-0
start<-min(diff[which(!is.na(diff))])

intervals<-cut(diff, breaks=c(start, brk), include.lowest=T) 

# legend for 6 buckets
allIntervals<-c(paste0("[",round(start,digits=1),",",round(brk[1], digits=1),"]"), 
                paste0("(",round(brk[1], digits=1),",",round(brk[2], digits=1),"]"),
                paste0("(",round(brk[2], digits=1),",",round(brk[3], digits=1), "]"),
                paste0("(",round(brk[3], digits=1),",",round(brk[4], digits=1),"]"),
                paste0("(",round(brk[4], digits=1), ",",round(brk[5], digits=1),"]"),
                paste0("(",round(brk[5], digits=1), ",",round(brk[6], digits=1),"]"))

legend<-data.frame(allIntervals, cols)
lmts<-c(paste0(legend$cols[1]), paste0(legend$cols[2]), paste0(legend$cols[3]), paste0(legend$cols[4]), paste0(legend$cols[5]), 
        paste0(legend$cols[6]), paste0(legend$cols[7])) #see in plot - this forces R to show all levels in the legend, even if not all appear in the map

ageData<-data.frame("bfs_nr"=year2016$bfs_nr, diff)
ageData[,c(1,2)] <- sapply(ageData[,c(1,2)], as.character)
ageData[,c(1,2)] <- sapply(ageData[,c(1,2)], as.numeric)
ageData<-ageData[order(as.numeric(as.character(ageData$bfs_nr)), decreasing=F),]

#create id-variable that will match the id-variable in shapeCH_fort, as the exact GMDNR is, there, replaced by 1:length(GMDNR)
idvar<-c(0:(nrow(ageData)-1))
ageData_age<-ageData$diff
intervals_ord<-unique(intervals)[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals)))))]
#attribute colors
colInterval<-c()
for (i in 1:length(intervals)){
  for (j in 1:length(brk)){
    ifelse(is.na(intervals[i]), colInterval[i]<-colNA, 
           ifelse(intervals[i]==allIntervals[j], colInterval[i]<-cols[j], #if we relate to intervals_ord, here, we get problems in cases where not the entire scale is used 
                  j+1))
  }
}
#create final dataframe
ageData_final<-as.data.frame(cbind(ageData_age, idvar, intervals, colInterval)) 
#plot
ggplot() + 
  geom_map(data = ageData_final, aes(map_id = idvar, fill = paste0(
    as.character(colInterval))), map = shapeCH_fort, colour="white", lwd=0.005) + 
  expand_limits(x = shapeCH_fort$long, y = shapeCH_fort$lat) + 
  coord_equal() +
  ggtitle("Die Deutschschweiz ist stärker gealtert als die Romandie") +
  scale_fill_identity("Legend", labels = legend$allIntervals, breaks=legend$cols, limits=lmts, guide = guide_legend(direction="horizontal", label.position = "bottom", keywidth=3, keyheight=.6, nrow=1)) +
  theme(line = element_blank(),
        legend.title = element_blank(),
        plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5),
        panel.background = element_blank(),
        axis.title=element_blank(),
        axis.text=element_blank(),
        axis.ticks=element_blank(),
        legend.position="bottom",
        legend.text=element_text(family="GT America", color="#6E6E7E", size=11)) 
ggsave("medianalterDiff_2016vs1970_kmeans_desktop14x12.svg", width=14, height=12)

#legend
legend_ext<-data.frame(legend, values=c(brk[1]-start, brk[2]-brk[1], brk[3]-brk[2], brk[4]-brk[3], brk[5]-brk[4], brk[6]-brk[5]))

# enable to relevel
legend_ext$allIntervals <- factor(legend_ext$allIntervals,levels(legend_ext$allIntervals)[c(4,3,2,5,1,6)]) #change order (top-bucket first in list) of levels for accurate order of appearance in stacked bar

ggplot(legend_ext, aes(as.factor(1), values, fill=allIntervals)) + 
  geom_bar(stat="identity", position="stack") +
  scale_fill_manual(values=rev(as.character(legend_ext$cols)), guide=F) +
  scale_y_continuous(breaks=c(0,legend_ext$values[1],
                              legend_ext$values[1]+legend_ext$values[2],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5],
                              legend_ext$values[1]+legend_ext$values[2]+legend_ext$values[3]+legend_ext$values[4]+legend_ext$values[5]+legend_ext$values[6]),
                     labels=c(start,brk)) +
  theme(
    panel.background = element_blank(),
    legend.title=element_blank(),
    axis.title=element_blank(),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank(),
    axis.text.y = element_text(family="GT America", color="#6E6E7E", size=11)
  )



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### INFERENTIAL STATISTICS ###

## Do the French-speaking and the German-speaking municipalities really differ?
summary(aov(agePopDevelopment$ageDevelopment ~ agePopDevelopment$sprachgebiet)) 
lm(agePopDevelopment$ageDevelopment ~ agePopDevelopment$sprachgebiet) %>% summary()
TukeyHSD(aov(agePopDevelopment$ageDevelopment ~ as.factor(agePopDevelopment$sprachgebiet))) #Post-Hoc
