##################################################################################################################################
##-------------------------------------------------------------------------------------------------------------------------------
#Kartentyp 4: Wahlbeteiligung - sequenzielle Farbskala
##################################################################################################################################

colWahlbeteiligung<-c("#191D63","#594C7F","#8F819A","#C6B8B6","#FDF4D1")
cols<-rev(colWahlbeteiligung)

turnoutData<-voteTurnout17

# Define buckets
clusters<-5
set.seed(1)
clust <- kmeans(turnoutData[which(!is.na(turnoutData))],clusters)$cluster
combined <- as.data.frame(cbind(turnoutData[which(!is.na(turnoutData))],clust))
brk <- sort(aggregate(combined[,1], list(combined[,2]), max)[,2])
start<-min(turnoutData[which(!is.na(turnoutData))])
#create intervals
intervals<-c()
for (i in 1:length(turnoutData)){
  for (j in 1:length(brk)){
    ifelse(turnoutData[i]<brk[1], intervals[i]<-paste0("[",round(start,digits=1),",",round(brk[1], digits=1),")"), 
           ifelse(turnoutData[i]>=brk[j] & turnoutData[i]<brk[j+1], intervals[i]<-paste0("[",round(brk[j], digits=1),",",round(brk[j+1], digits=1),")"),
                  ifelse(turnoutData[i]==brk[length(brk)], intervals[i]<-paste0("[",round(brk[length(brk)-1], digits=1),",",round(brk[length(brk)], digits=1),")"),
                         ifelse(is.na(turnoutData[i]),intervals[i]<-NA,
                                j+1))))
  }
}
intervals_ord<-unique(intervals)[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals)))))]
#attribute colors
colInterval<-c()
for (i in 1:length(intervals)){
  for (j in 1:length(brk)){
    ifelse(is.na(intervals[i]), colInterval[i]<-colNA, 
           ifelse(intervals[i]==intervals_ord[j], colInterval[i]<-cols[j],
                  j+1))
  }
}
turnoutData_final<-as.data.frame(cbind(turnoutData, "WKR_NR"=wk$WKR_NR, intervals, colInterval))
#create legend
lbls<-c() # is equal to intervals_ord if we do not have any NA, otherwise last bucket is NA-color and labelled "noch nicht ausgezählt"
for(i in 1:length(intervals_ord)){ifelse(is.na(intervals_ord[i]),lbls[i]<-"noch nicht ausgezählt", lbls[i]<-intervals_ord[i])}
maxBrk<-gsub("\\[|\\)","",strsplit(lbls[5],",")[[1]][1])
minBrk<-gsub("\\[|\\)","",strsplit(lbls[1],",")[[1]][2])
lbls<-rev(lbls)
lbls_red<-c()
ifelse(NA%in%intervals_ord, lbls_red<-c(paste0("> ",maxBrk,"%"), " "," "," ",paste0("< ",minBrk,"%"), "noch nicht ausgezählt"), 
       lbls_red<-c(paste0("> ",maxBrk,"%"), " "," "," ",paste0("< ",minBrk,"%")))
brks<-c()
ifelse(NA%in%intervals_ord, brks<-c(rev(cols), colNA), brks<-rev(cols))
#plot
filename<-paste0("2017_beteiligung","_","8x8",".svg")
ggplot() + 
  geom_map(data = turnoutData_final, aes(map_id = WKR_NR, fill = colInterval), map = wk_fort, colour="white", lwd=0.005) + 
  geom_point(data=cities, aes(lon, lat)) +
  expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
  coord_equal() +
  scale_fill_identity("Legend", labels = lbls_red, breaks=brks, guide = "legend") + #change lbls_red to lbls to check the buckets
  theme(line = element_blank(),
        legend.title = element_blank(),
        plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5), 
        panel.background = element_blank(),
        axis.title=element_blank(),
        axis.text=element_blank(),
        axis.ticks=element_blank(),
        legend.text=element_text(family="GT America", color="#6E6E7E", size=11)) 
ggsave(filename, device=svglite, width=8, height=8)


