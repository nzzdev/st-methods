##################################################################################################################################
##-------------------------------------------------------------------------------------------------------------------------------
#Kartentyp 6: Gekippte Wahlkreise (Erststimmen)
##################################################################################################################################

# Define parties, years, color scheme
partynames<-c("Union (CDU/CSU)", "SPD", "Die Linke", "Grüne", "FDP", "AfD")

cols<-as.character(as.matrix(colorFrame[5,]))

voteDataAll.13<-erststimmen13.gross[,c(3:8)]
head(voteDataAll.13) #check if the sequence of columns still corresponds to the sequence of the partynames
colnames(voteDataAll.13)<-partynames

voteDataAll.17<-erststimmen17.gross[,c(3:8)]
head(voteDataAll.17) #check if the sequence of columns still corresponds to the sequence of the partynames
colnames(voteDataAll.17)<-partynames

setwd("mypath/graphics/maps")


#Process data: get row maximum along with its colname (party) and party color
datamax.13<-data.frame()
for (i in 1:nrow(voteDataAll.13)){
  #get maximum, set to na if all parties are na
  ifelse(length(voteDataAll.13[i,][which(!is.na(voteDataAll.13[i,]))])!=0, maxi<-max(voteDataAll.13[i,][which(!is.na(voteDataAll.13[i,]))]), maxi<-NA)
  #get party belonging to maximum, set to "noch nicht ausgezählt" if all parties are na
  ifelse(length(voteDataAll.13[i,][which(!is.na(voteDataAll.13[i,]))])!=0, maxPartyi<-colnames(voteDataAll.13[which(voteDataAll.13[i,]==maxi)]), maxPartyi<-"noch nicht ausgezählt")
  #get party color, set to colNA if all parties are na
  ifelse(length(voteDataAll.13[i,][which(!is.na(voteDataAll.13[i,]))])!=0, coli<-cols[match(maxPartyi, partynames)], coli<-colNA)
  rowi<-cbind.data.frame("maj"=as.numeric(as.character(maxi)), "party"=maxPartyi, "cols"=coli)
  datamax.13<-rbind.data.frame(datamax.13, rowi)
}

datamax.17<-data.frame()
for (i in 1:nrow(voteDataAll.17)){
  #get maximum, set to na if all parties are na
  ifelse(length(voteDataAll.17[i,][which(!is.na(voteDataAll.17[i,]))])!=0, maxi<-max(voteDataAll.17[i,][which(!is.na(voteDataAll.17[i,]))]), maxi<-NA) 
  #get party belonging to maximum, set to "noch nicht ausgezählt" if all parties are na
  ifelse(length(voteDataAll.17[i,][which(!is.na(voteDataAll.17[i,]))])!=0, maxPartyi<-colnames(voteDataAll.17[which(voteDataAll.17[i,]==maxi)]), maxPartyi<-"noch nicht ausgezählt")
  #get party color, set to colNA if all parties are na
  ifelse(length(voteDataAll.17[i,][which(!is.na(voteDataAll.17[i,]))])!=0, coli<-cols[match(maxPartyi, partynames)], coli<-colNA)
  rowi<-cbind.data.frame("maj"=as.numeric(as.character(maxi)), "party"=maxPartyi, "cols"=coli)
  datamax.17<-rbind.data.frame(datamax.17, rowi)
}


datamax.13_final<-as.data.frame(cbind("WKR_NR"=wk$WKR_NR, datamax.13))
datamax.17_final<-as.data.frame(cbind("WKR_NR"=wk$WKR_NR, datamax.17))

#check if wk-nr is correctly added
which(datamax_final$WKR_NR!=erststimmen17.gross$wk_nr)
which(datamax_final$WKR_NR!=erststimmen13.gross$wk_nr)

#define labels and colorscale for legend
ifelse(NA %in% datamax.13_final$maj, lbls<-c(partynames, "noch nicht ausgezählt"), lbls<-partynames)
ifelse(NA %in% datamax.13_final$maj, brks<-c(cols, colNA),brks<-cols)
ifelse(NA %in% datamax.13_final$maj, lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), paste0(brks[6]), paste0(brks[7])), lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), paste0(brks[6])))

ifelse(NA %in% datamax.17_final$maj, lbls<-c(partynames, "noch nicht ausgezählt"), lbls<-partynames)
ifelse(NA %in% datamax.17_final$maj, brks<-c(cols, colNA),brks<-cols)
ifelse(NA %in% datamax.17_final$maj, lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), paste0(brks[6]), paste0(brks[7])), lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), paste0(brks[6])))


#plot
filename<-paste0("2013_gewinner","8x8",".png")
ggplot() + 
  geom_map(data = datamax.13_final, aes(map_id = WKR_NR, fill = cols), map = wk_fort, colour="white", lwd=0.005) + 
  geom_point(data=cities, aes(lon, lat)) +
  expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
  coord_equal() +
  scale_fill_identity(breaks = paste0(brks), labels = lbls, guide="legend", limits = lmts) + #indicating all levels in "limits" forces ggplot to show the entire scale, including levels that are not in the map
  theme(line = element_blank(),
        title = element_blank(),
        panel.background = element_blank(),
        axis.title=element_blank(),
        axis.text=element_blank(),
        axis.ticks=element_blank(),
        legend.text=element_text(family="GT America", color="#6E6E7E", size=11))
ggsave(filename, width=8, height=8)

filename<-paste0("2017_gewinner","8x8",".png")
ggplot() + 
  geom_map(data = datamax.17_final, aes(map_id = WKR_NR, fill = cols), map = wk_fort, colour="white", lwd=0.005) + 
  geom_point(data=cities, aes(lon, lat)) +
  expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
  coord_equal() +
  scale_fill_identity(breaks = paste0(brks), labels = lbls, guide="legend", limits = lmts) + #indicating all levels in "limits" forces ggplot to show the entire scale, including levels that are not in the map
  theme(line = element_blank(),
        title = element_blank(),
        panel.background = element_blank(),
        axis.title=element_blank(),
        axis.text=element_blank(),
        axis.ticks=element_blank(),
        legend.text=element_text(family="GT America", color="#6E6E7E", size=11))
ggsave(filename, width=8, height=8)



#which wk were won by another party than in the previous election
datamax.13_final$party<-as.character(datamax.13_final$party)
datamax.17_final$party<-as.character(datamax.17_final$party)

nrow(datamax.17_final[which(datamax.17_final$party!=datamax.13_final$party),])
datamax.17_final[which(datamax.17_final$party!=datamax.13_final$party),]

gekippt.17<-c()
for (i in 1:nrow(datamax.17_final)){
  ifelse(datamax.17_final$party[i]==datamax.13_final$party[i], gekippt.17[i]<-datamax.17_final$WKR_NR[i], gekippt.17<-"same")
}
gekippt.13<-c()
for (i in 1:nrow(datamax.13_final)){
  ifelse(datamax.13_final$party[i]==datamax.13_final$party[i], gekippt.13[i]<-datamax.17_final$WKR_NR[i], gekippt.13<-"same")
}

