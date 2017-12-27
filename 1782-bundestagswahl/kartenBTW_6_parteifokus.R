
##################################################################################################################################
##-------------------------------------------------------------------------------------------------------------------------------
#Kartentyp 5: Parteifokus - Parteistaerke und Diff, side-by-side
##################################################################################################################################

# Loop for parteistaerke-case
party<-c("Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE")
partyname<-c("SPD", "Union (CDU/CSU)", "FDP", "Grüne", "AfD", "Die Linke")
year<-zweitstimmen17.gross
yearname<-"2017"

##-------------------------------------------------------------------------------------------------------------------------------
### loop over parties: stand-alone maps for parteistaerke, legend by the side
pltlst_fokus_staerke<-list()
for(p in 1:length(party)){
  voteData<-year[,grep(paste0(party[p]),colnames(year))]
  #THIS IS AN NA-TEST, ENABLE TO TEST WHAT HAPPENS WITH NA-VALUES
  #voteData[c(2,12,22,32,42,87,93,134,165,198, 212, 213, 214, 215, 256,287,298)]<-NA #random NAs for testing
  #THIS IS THE END OF THE TEST
  cols<-as.character(colorFrame[,grep(paste0(party[p]),colnames(colorFrame))])
  #create buckets
  clusters<-5
  set.seed(1)
  clust <- kmeans(voteData[which(!is.na(voteData))],clusters)$cluster #kmeans(voteData,clusters)$cluster 
  combined <- as.data.frame(cbind(voteData[which(!is.na(voteData))],clust)) #as.data.frame(cbind(voteData,clust))
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
  intervals_ord<-unique(intervals[which(!is.na(intervals))])[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals[which(!is.na(intervals))])))))] # throws out na, since we do not want them in the legend here; formerly intervals_ord<-unique(intervals)[order(as.numeric(sub(",.*", "", sub("\\[", "",unique(intervals)))))]
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
  lbls<-rev(intervals_ord)
  maxBrk<-gsub("\\[|\\)","",strsplit(intervals_ord[5],",")[[1]][1])
  minBrk<-gsub("\\[|\\)","",strsplit(intervals_ord[1],",")[[1]][2])
  lbls_red<-rev(c(paste0("< ",minBrk,"%"), " "," "," ",paste0("> ",maxBrk,"%"))) #change lbls_red to lbls to check the buckets
  brks<-rev(colInterval[match(intervals_ord, voteData_final$intervals)])
  #plot
  plotp<-ggplot() + 
    geom_map(data = voteData_final, aes(map_id = WKR_NR, fill = colInterval), map = wk_fort, colour="white", lwd=0.005) + 
    geom_point(data=cities, aes(lon, lat)) +
    expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
    coord_equal() +
    scale_fill_identity("Legend", labels = lbls_red, breaks=brks, guide = guide_legend(label.position = "left", label.hjust = 1)) +
    theme(line = element_blank(),
          legend.title = element_blank(),
          plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5), 
          panel.background = element_blank(),
          axis.title=element_blank(),
          axis.text=element_blank(),
          axis.ticks=element_blank(),
          legend.position="left",
          legend.text=element_text(family="GT America", size=11, color="#6E6E7E")) 
  pltlst_fokus_staerke[[p]]<-plotp
}



##-------------------------------------------------------------------------------------------------------------------------------
### loop over parties: stand-alone maps for diff, legend by the side

colDiv<-c("#3e9396","#56a0a3","#6eaeb0","#86bbbd","#9ec9ca","#eab298","#e59f7e","#e08c65","#db794b","#d66632") #von gewinn zu verlust
cols<-rev(colDiv) #rev, denn: wollen von kleinen zu grossen zahlen, i.e. von verlust zu gewinn

yearPast<-zweitstimmen13.gross
yearActual<-zweitstimmen17.gross

diff<-yearActual #get structure of one of the dataframes (colnames and nrwo of yearActual or yearPast) that can be filled with diff-data in the following
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

### case for stand-alone maps, legend by the side
pltlst_fokus_diff<-list()
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
  #create legend
  maxBrk<-gsub("\\[|\\)","",strsplit(as.character(legend$allIntervals[10]),",")[[1]][1])
  minBrk<-gsub("\\[|\\)","",strsplit(as.character(legend$allIntervals[1]),",")[[1]][2])
  lbls<-rev(paste0(legend$allIntervals))
  lbls_red<-c(paste0("> ",maxBrk,"%p"), " "," "," "," "," "," "," "," ",paste0("< ",minBrk,"%p"))
  brks<-rev(paste0(legend$cols))
  lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), 
          paste0(brks[6]), paste0(brks[7]), paste0(brks[8]), paste0(brks[9]), paste0(brks[10]))
  #plot
  plotp<-ggplot() + 
    geom_map(data = diffData_final, aes(map_id = WKR_NR, fill = colInterval), map = wk_fort, colour="white", lwd=0.005) + 
    geom_point(data=cities, aes(lon, lat)) +
    expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
    coord_equal() +
    scale_fill_identity("Legend", labels = lbls_red, breaks=brks, limits=lmts, guide = "legend") + #change lbls_red to lbls to check the buckets
    theme(line = element_blank(),
          legend.title = element_blank(),
          plot.title = element_text(family="GT America", color="#05032D", size=16, hjust=0.5), 
          panel.background = element_blank(),
          axis.title=element_blank(),
          axis.text=element_blank(),
          axis.ticks=element_blank(),
          legend.text=element_text(family="GT America", size=11, color="#6E6E7E")) 
  pltlst_fokus_diff[[p]] <- plotp
}


# Plot side-by-side, parteistaerke and diff, DESKTOP
for (p in 1:length(party)){
  filename<-paste0("parteifokus","_",gsub("/","",partyname[p]),"_","desktop12x7",".svg")
  svglite(filename, width=12, height=7)
  grid.arrange(pltlst_fokus_staerke[[p]], pltlst_fokus_diff[[p]], ncol=2, nrow=1)
  dev.off()
}


# Plot side-by-side, parteistaerke and diff, MOBILE
for (p in 1:length(party)){
  filename<-paste0("parteifokus","_",gsub("/","",partyname[p]),"_","mobile7x14",".svg")
  svglite(filename, width=7, height=14)
  grid.arrange(pltlst_fokus_staerke[[p]], pltlst_fokus_diff[[p]], ncol=1, nrow=2)
  dev.off()
}






