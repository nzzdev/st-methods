##################################################################################################################################
##-------------------------------------------------------------------------------------------------------------------------------
#Kartentyp 3: Gewinnerpartei pro Wahlkreis (Erststimmen)
##################################################################################################################################

# Define parties, years, color scheme
partynames<-c("Union (CDU/CSU)", "SPD", "Die Linke", "Grüne", "FDP", "AfD")

voteDataAll<-erststimmen17.gross[,c(3:8)]
head(voteDataAll) #check if the sequence of columns still corresponds to the sequence of the partynames
colnames(voteDataAll)<-partynames
cols<-as.character(as.matrix(colorFrame[5,]))

setwd("mypath/graphics/maps")


#Process data: get row maximum along with its colname (party) and party color
datamax<-data.frame()
for (i in 1:nrow(voteDataAll)){
  #get maximum, set to na if all parties are na
  ifelse(length(voteDataAll[i,][which(!is.na(voteDataAll[i,]))])!=0, maxi<-max(voteDataAll[i,][which(!is.na(voteDataAll[i,]))]), maxi<-NA)
  #get party belonging to maximum, set to "noch nicht ausgezählt" if all parties are na
  ifelse(length(voteDataAll[i,][which(!is.na(voteDataAll[i,]))])!=0, maxPartyi<-colnames(voteDataAll[which(voteDataAll[i,]==maxi)]), maxPartyi<-"noch nicht ausgezählt")
  #get party color, set to colNA if all parties are na
  ifelse(length(voteDataAll[i,][which(!is.na(voteDataAll[i,]))])!=0, coli<-cols[match(maxPartyi, partynames)], coli<-colNA)
  rowi<-cbind.data.frame("maj"=as.numeric(as.character(maxi)), "party"=maxPartyi, "cols"=coli)
  datamax<-rbind.data.frame(datamax, rowi)
}

datamax_final<-as.data.frame(cbind("WKR_NR"=wk$WKR_NR, datamax))

#check if wk-nr is correctly added
which(datamax_final$WKR_NR!=erststimmen17.gross$wk_nr)

#define labels and colorscale for legend
ifelse(NA %in% datamax_final$maj, lbls<-c(partynames, "noch nicht ausgezählt"), lbls<-partynames)
ifelse(NA %in% datamax_final$maj, brks<-c(cols, colNA),brks<-cols)
ifelse(NA %in% datamax_final$maj, lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), paste0(brks[6]), paste0(brks[7])), lmts<-c(paste0(brks[1]), paste0(brks[2]), paste0(brks[3]), paste0(brks[4]), paste0(brks[5]), paste0(brks[6])))

#plot
filename<-paste0("2017_gewinner_","8x8",".svg")
ggplot() + 
  geom_map(data = datamax_final, aes(map_id = WKR_NR, fill = cols), map = wk_fort, colour="white", lwd=0.005) + 
  geom_point(data=cities, aes(lon, lat)) +
  expand_limits(x = wk_fort$long, y = wk_fort$lat) + 
  coord_equal() +
  scale_fill_identity(breaks = paste0(brks), labels = lbls, guide="legend", limits = lmts) +
  theme(line = element_blank(),
        title = element_blank(),
        panel.background = element_blank(),
        axis.title=element_blank(),
        axis.text=element_blank(),
        axis.ticks=element_blank(),
        legend.text=element_text(family="GT America", color="#6E6E7E", size=11))
ggsave(filename, device=svglite, width=8, height=8)


