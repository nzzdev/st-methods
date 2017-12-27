##################################################################################################################################
##-------------------------------------------------------------------------------------------------------------------------------
#Kartentyp 2: Veränderung zu 2013 pro Wahlkreis/Gemeinde
##################################################################################################################################

# Define parties, years, reverse color scheme
cols<-rev(colDiv) 

party<-c("Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE")
partyname<-c("SPD", "Union (CDU/CSU)", "FDP", "Grüne", "AfD", "Die Linke")
yearPast<-zweitstimmen13.gross
yearActual<-zweitstimmen17.gross

setwd("mypath/graphics/maps")

# Process data
diff<-yearActual #get structure of one of the dataframes (colnames and nrow of yearActual or yearPast) that can be filled with diff-data in the following
for (p in 1:length(party)){
  pastDatai<-yearPast[,grep(paste0(party[p]),colnames(yearPast))]
  actualDatai<-yearActual[,grep(paste0(party[p]),colnames(yearActual))]
  diffi<-actualDatai-pastDatai
  diff[,grep(paste0(party[p]),colnames(yearActual))]<-diffi
}

# Define breaks: 10 buckets between +/- the maximal deviation of an entry of diff from 0
maxDeviation<-max(abs(max(diff[,3:length(diff)])), abs(min(diff[,3:length(diff)])))
steps<-2*maxDeviation/10
brk<-seq(-maxDeviation+steps, maxDeviation, steps)
start<-brk[1]-steps

allIntervals<-c(paste0("[",round(-maxDeviation,digits=1),",",round(brk[1], digits=1),")"), 
                paste0("[",round(brk[1], digits=1),",",round(brk[2], digits=1),")"),
                paste0("[",round(brk[2], digits=1),",",round(brk[3], digits=1), ")"),
                paste0("[",round(brk[3], digits=1),",",round(brk[4], digits=1),")"),
                paste0("[",round(brk[4], digits=1), ",",round(brk[5], digits=1),")"),
                paste0("[",round(brk[5], digits=1), ",",round(brk[6], digits=1),")"),
                paste0("[",round(brk[6], digits=1), ",",round(brk[7], digits=1),")"),
                paste0("[",round(brk[7], digits=1), ",",round(brk[8], digits=1),")"),
                paste0("[",round(brk[8], digits=1), ",",round(brk[9], digits=1),")"),
                paste0("[",round(brk[9], digits=1), ",",round(brk[10], digits=1),")"))

legend<-data.frame(allIntervals, cols)



##-------------------------------------------------------------------------------------------------------------------------------
#case for small multiples, no legend
plot_list_diff<-list()
for(p in 1:length(party)){
  diffData<-diff[,grep(paste0(party[p]),colnames(diff))]
  #THIS IS AN NA-TEST, ENABLE TO TEST WHAT HAPPENS WITH NA-VALUES
  #diffData[c(2,12,22,32,42,87,93,134,165,198, 212, 213, 214, 215, 256,287,298)]<-NA #random NAs for testing
  #THIS IS THE END OF THE TEST
  #create intervals
  intervals<-c()
  for (i in 1:length(diffData)){
    for (j in 1:length(brk)){
      ifelse(diffData[i]<brk[1], intervals[i]<-paste0("[",round(start,digits=1),",",round(brk[1], digits=1),")"), 
             ifelse(diffData[i]>=brk[j] & diffData[i]<brk[j+1], intervals[i]<-paste0("[",round(brk[j], digits=1),",",round(brk[j+1], digits=1),")"),
                    ifelse(diffData[i]==brk[length(brk)], intervals[i]<-paste0("[",round(brk[length(brk)-1], digits=1),",",round(brk[length(brk)], digits=1),")"),
                           ifelse(is.na(diffData[i]),intervals[i]<-NA,
                                  j+1))))
    }
  }
  intervals_ord<-unique(intervals)[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals)))))]
  #attribute colors
  colInterval<-c()
  for (i in 1:length(intervals)){
    for (j in 1:length(brk)){
      ifelse(is.na(intervals[i]), colInterval[i]<-colNA, 
             ifelse(intervals[i]==allIntervals[j], colInterval[i]<-cols[j],
                    j+1))
    }
  }
  diffData_final<-as.data.frame(cbind(diffData, "WKR_NR"=wk$WKR_NR, intervals, colInterval))
  #plot
  plotp<-ggplot() + 
    geom_map(data = diffData_final, aes(map_id = WKR_NR, fill = colInterval), map = wk_fort, colour="white", lwd=0.005) + 
    geom_point(data=cities, aes(lon, lat)) +
    expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
    coord_equal() +
    ggtitle(partyname[p]) +
    scale_fill_identity() +
    theme(line = element_blank(),
          legend.title = element_blank(),
          plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5), #if we find possiblilty to print gt america with ggsave or to loop with quartz.save: family="GT America", 
          panel.background = element_blank(),
          axis.title=element_blank(),
          axis.text=element_blank(),
          axis.ticks=element_blank(),
          legend.text=element_text(family="GT America", color="#6E6E7E", size=11)) #if we find possiblilty to print gt america with ggsave or to loop with quartz.save: family="GT America", 
  plot_list_diff[[p]] <- plotp
}

#create and plot grid for small multiples, DESKTOP
filename<-paste0("diff","_", "smallmult","_","desktop14x12",".svg")
svglite(filename, width=14, height=12)
grid.arrange(plot_list_diff[[2]], plot_list_diff[[1]], plot_list_diff[[3]], plot_list_diff[[4]], plot_list_diff[[5]], plot_list_diff[[6]], ncol=3, nrow=2)
dev.off()


#create and plot grid for small multiples, MOBILE
filename<-paste0("diff","_", "smallmult","_","mobile8x20",".svg")
svglite(filename, width=8, height=20)
grid.arrange(plot_list_diff[[2]], plot_list_diff[[1]], plot_list_diff[[3]], plot_list_diff[[4]], plot_list_diff[[5]], plot_list_diff[[6]], ncol=2, nrow=3)
dev.off()






