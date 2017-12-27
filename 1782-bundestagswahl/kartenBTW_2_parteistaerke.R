##################################################################################################################################
##-------------------------------------------------------------------------------------------------------------------------------
#Kartentyp 1: Stimmenanteile pro Wahlkreis/Gemeinde
##################################################################################################################################

# Define parties, year
party<-c("Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE")
partyname<-c("SPD", "Union (CDU/CSU)", "FDP", "Grüne", "AfD", "Die Linke")
year<-zweitstimmen17.gross
yearname<-"2017"

setwd("mypath/graphics/maps")



##-------------------------------------------------------------------------------------------------------------------------------
### loop over parties: case for small multiples, legend below, do not show NA in legend (will be shown once for all 6 maps)
plot_list_parteistaerke = list()
for(p in 1:length(party)){
  voteData<-zweitstimmen17.gross[,grep(paste0(party[p]),colnames(zweitstimmen17.gross))]
  #THIS IS AN NA-TEST, ENABLE TO TEST WHAT HAPPENS WITH NA-VALUES
  #voteData[c(2,12,22,32,42,87,93,134,165,198, 212, 213, 214, 215, 256,287,298)]<-NA #random NAs for testing
  #THIS IS THE END OF THE TEST
  cols<-as.character(colorFrame[,grep(paste0(party[p]),colnames(colorFrame))])
  #create buckets
  clusters<-5
  set.seed(1)
  clust <- kmeans(voteData[which(!is.na(voteData))],clusters)$cluster
  combined <- as.data.frame(cbind(voteData[which(!is.na(voteData))],clust))
  brk <- sort(aggregate(combined[,1], list(combined[,2]), max)[,2])
  start<-min(voteData[which(!is.na(voteData))])
  #create intervals
  intervals<-c()
  for (i in 1:length(voteData)){
    for (j in 1:length(brk)){
      ifelse(voteData[i]<brk[1], intervals[i]<-paste0("[",round(start,digits=1),",",round(brk[1], digits=1),")"), 
             ifelse(voteData[i]>=brk[j] & voteData[i]<brk[j+1], intervals[i]<-paste0("[",round(brk[j], digits=1),",",round(brk[j+1], digits=1),")"),
                    ifelse(voteData[i]==brk[length(brk)], intervals[i]<-paste0("[",round(brk[length(brk)-1], digits=1),",",round(brk[length(brk)], digits=1),")"),
                           ifelse(is.na(voteData[i]),intervals[i]<-NA,
                                  j+1))))
    }
  }
  intervals_ord<-unique(intervals[which(!is.na(intervals))])[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals[which(!is.na(intervals))])))))] #gets rid of na, since we do not want them in the legend here
  #attribute colors
  colInterval<-c()
  for (i in 1:length(intervals)){
    for (j in 1:length(brk)){
      ifelse(is.na(intervals[i]), colInterval[i]<-colNA, 
             ifelse(intervals[i]==intervals_ord[j], colInterval[i]<-cols[j],
                    j+1))
    }
  }
  #create final dataframe
  voteData_final<-as.data.frame(cbind(voteData, "WKR_NR"=wk$WKR_NR, intervals, colInterval))
  #create legend
  lbls<-intervals_ord
  maxBrk<-gsub("\\[|\\)","",strsplit(lbls[5],",")[[1]][1])
  minBrk<-gsub("\\[|\\)","",strsplit(lbls[1],",")[[1]][2])
  lbls_red<-c(paste0("< ",minBrk,"%"), " "," "," ",paste0("> ",maxBrk,"%")) #change lbls_red to lbls to check the buckets
  brks<-colInterval[match(intervals_ord, voteData_final$intervals)]
  #plot
  plotp<-ggplot() + 
    geom_map(data = voteData_final, aes(map_id = WKR_NR, fill = paste0(colInterval)), map = wk_fort, colour="white", lwd=0.005) + 
    geom_point(data=cities, aes(lon, lat)) +
    expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
    coord_equal() +
    ggtitle(partyname[p]) +
    scale_fill_identity("Legend", labels = lbls_red, breaks=brks, guide = guide_legend(direction="horizontal", label.position = "bottom", keywidth=3, keyheight=.6)) +
    theme(line = element_blank(),
          legend.title = element_blank(),
          plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5),
          panel.background = element_blank(),
          axis.title=element_blank(),
          axis.text=element_blank(),
          axis.ticks=element_blank(),
          legend.position="bottom",
          legend.text=element_text(family="GT America", color="#6E6E7E", size=11)) 
  plot_list_parteistaerke[[p]] <- plotp
}

# create and plot grid for small multiples, DESKTOP
filename<-paste0(yearname,"_", "parteistaerke","_", "smallmult", "_","kmeans", "_", "desktop14x12",".svg")
svglite(filename, width=14, height=12)
grid.arrange(plot_list_parteistaerke[[2]], plot_list_parteistaerke[[1]], plot_list_parteistaerke[[3]], plot_list_parteistaerke[[4]], plot_list_parteistaerke[[5]], plot_list_parteistaerke[[6]], ncol=3, nrow=2)
dev.off()

# create and plot grid for small multiples, MOBILE
filename<-paste0(yearname,"_", "parteistaerke","_", "smallmult", "_","kmeans", "_", "mobile8x20",".svg")
svglite(filename, width=8, height=20)
grid.arrange(plot_list_parteistaerke[[2]], plot_list_parteistaerke[[1]], plot_list_parteistaerke[[3]], plot_list_parteistaerke[[4]], plot_list_parteistaerke[[5]], plot_list_parteistaerke[[6]], ncol=2, nrow=3)
dev.off()





