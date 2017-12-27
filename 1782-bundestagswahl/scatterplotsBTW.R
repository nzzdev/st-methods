
########################################################################################################
################################### TABLE OF CONTENTS ##################################################
########################################################################################################

## 0. Packages and env prep
## 1. Data Prep: socio-economic indicators for BTW 2017
## 2. Data Prep: BTW-results 2013
## 3. Subsetting the data for the automated regression analyses with chained serial plotting
## 4. Loop for the automated regression analyses with chained serial plotting

## Comment: if you don't like the names of the dataframes: Edit > Find and replace

########################################################################################################
################################ 0. PACKAGES AND ENV PREP ##############################################
########################################################################################################

rm(list=ls()) # clean env

# packages
library(dplyr)
library(scales)
library(svglite)

setwd("mypath/data/") # set working directory

# function for cleaning our messy character strings
jam <- function(x) gsub("Ÿ", "ü", x) %>% 
  gsub("š", "ö", .) %>% 
  gsub("Š", "ä", .) %>% 
  gsub("Ð", "-", .) %>%
  gsub("§", "ss", .) %>%
  gsub("–", "-", .) %>%
  gsub("ß", "ss", .) %>%
  gsub("†", "Ü", .) %>%
  gsub("Ÿ", "ü", .) %>%
  gsub("€", "Ä", .) %>%
  gsub(" ", "",.)


########################################################################################################
################################ 1. DATA PREP: INDICATORS BTW 2017 #####################################
########################################################################################################

# data source: https://www.bundeswahlleiter.de/bundestagswahlen/2017/strukturdaten.html
tea <- read.csv("btw17_strukturdaten_kreise2.csv", sep=";", header=F, stringsAsFactors = F) # load data

tea <- tea[-c(1:9),] # remove the header

# create tibble matrix [manually...]; rename variables 
tea <- tibble(land=tea$V1, # Land
              wk_nr=tea$V2, # Wahklreisnummer
              name=tea$V3, # Name des Wahklreis
              anz_gem=tea$V4, # Anzahl Gemeinden
              flaeche=tea$V5, # Wahklreisfläche
              bev_gsmt=tea$V6, # Gesamtbev. [in 1000]
              bev_dt=tea$V7, # Anzahl Deutsche Gesamtbev. [in 1000]
              bev_ausl=tea$V8, # Anteil Ausländer Gesamtbev [%]
              bev_dichte=tea$V9, # Bev.Dichte [Einwohner/km2]
              geburten=tea$V10, # Geburtensaldo [je 1000 Einwohner]
              wander=tea$V11, # Wanderungssaldo [je 1000 Einwohner]
              alt_u18=tea$V12, # Anteil U18 [%]
              alt_1824=tea$V13, # Anteil 18-24 [%]
              alt_2534=tea$V14, # Anteil 25-34 [%]
              alt_3559=tea$V15, # Anteil 35-59 [%]
              alt_6074=tea$V16, # Anteil 60-74 [%]
              alt_75=tea$V17, # Anteil Ü75 [%]
              z_omh=tea$V18, # Zensus 2011: Anteil Bev. ohne Migrationshintergrund [%]
              z_mmh=tea$V19, # Zensus 2011: Anteil Bev. mit Migrationshintergrund [%]
              z_kath=tea$V20, # Zensus 2011: Anteil kath. Bev. [%]
              z_evang=tea$V21, # Zensus 2011: Anteil reform. Bev. [%]
              z_ok=tea$V22, # Zensus 2011: Anteil Bev. ohne Kirche [%]
              eink=tea$V26, # Verfügbares Einkommen d. privaten Haushalte (je Einwohner)
              bippc=tea$V27, # BIP per capita
              abs_beruf=tea$V29, # Absolventen beruflicher Schulen
              abs_tot=tea$V30, # Absolventen allgemeinbildender Schulen 2015 - insgesamt ohne Externe [je 1000 Einwohner]
              abs_ohnehaupt=tea$V31, # Absolventen allgemeinbildender Schulen 2015 - ohne Hauptschulabschluss [%]
              abs_haupt=tea$V32, # Absolventen allgemeinbildender Schulen 2015 - mit Hauptschulabschluss [%]
              abs_mitt=tea$V33, # Absolventen allgemeinbildender Schulen 2015 - mit mittlerem Schulabschluss [%]
              abs_hoch=tea$V34, # Absolventen allgemeinbildender Schulen 2015 - mit allgemeiner und Fachhochschulreife [%]
              kita=tea$V35, # Kita-Betreuung: Betreute Kinder je 1000 Einwohner
              arbtslq_tot=tea$V47, # Arbeitslosenquote insgesamt
              arbtslq_m=tea$V48, # Arbeitslosenquote Männer
              arbtslq_f=tea$V49, # Arbeitslosenquote Frauen
              arbtslq_1520=tea$V50, # Arbeitslosenquote 15-20
              arbtslq_5565=tea$V51) # Arbeitslosenquote 55-65

# clean `land` and `name` (function was defined in 0.)
tea$land <- jam(tea$land)
tea$name <- jam(tea$name)

# make all numerical variables numeric
tea[,c(2,4:length(tea))] <- lapply(tea[,c(2,4:length(tea))], as.numeric)
# there are 3 missing values in abs_beruf:
tea %>% filter(is.na(abs_beruf))

# compute x*1000 for all variables coded with "in 1000"
sauce <- function (x) x*1000
tea[,6:7] <- lapply(tea[,6:7], sauce) 

# replace all the 'Landingesamt' with the Länder-names
tea$name[tea$wk_nr>900] <- tea$land[tea$wk_nr>900]

# order the data according to the `wk_nr`
tea <- tea[order(tea$wk_nr),]

# coerce to data frame (better for plotting)
tea <- as.data.frame(tea)

# add the full variables names and the units as comments to the variables
# full variable names
comment.vec <- c("Land", "Wahlkreisnummer", "Name Wahlkreis", "Anzahl Gemeinden", "Fläche", 
                 "Bevölkerung Gesamt", "Gesamtbevölkerung: Deutsche", "Ausländeranteil",
                 "Bevölkerungsdichte", "Geburtenrate", "Wanderungssaldo", "Anteil U18-jährige",
                 "Anteil 18-24-jährige", "Anteil 25-34-jährige", " Anteil 35-59-jährige", 
                 "Anteil 60-74-jährige", "Anteil Ü75-jährige", "Anteil Bev. ohne Migrationshintergrund",
                 "Anteil Bev. mit Migrationshintergrund", "Anteil kath. Bev.", "Anteil reform. Bev.", 
                 "Anteil Bev. ohne Kirche", "Verfügbares Einkommen d. privaten Haushalte", "BIP per capita", 
                 "Absolventen beruflicher Schulen", "Absolventen - insgesamt ohne Externe", 
                 "Absolventen - ohne Hauptschulabschluss", "Absolventen - mit Hauptschulabschluss", 
                 "Absolventen - mit mittlerem Schulabschluss", "Absolventen - mit allgemeiner und Fachhochschulreife",
                 "Kita-Betreuung", "Arbeitslosenquote insgesamt", "Arbeitslosenquote Männer", "Arbeitslosenquote Frauen", 
                 "Arbeitslosenquote 15-20-jährige", "Arbeitslosenquote 55-65-jährige")
# units
unit.vec <- c("Char.", "Nummer", "Char.", "abs. Zahlen","km2", "abs. Zahlen", "abs. Zahlen", "Prozent", "Einwohner/km2", 
              "Geburtensaldo je 1000 Einwohner", "Wanderungssaldo je 1000 Einwohner", rep("Prozent", 11), "Verf. Einkommen/Einw.", 
              "BIP pc", "?", "je 1000 Einwohner", rep("Prozent", 4), "Betreute Kinder/1000 Einw.", rep("Prozent", 5))

# loop for adding the comments [shows progress]
for (i in 1:length(tea)) {
  comment(tea[,i]) <- c(comment.vec[i], unit.vec[i])
  print(paste(comment(tea[,i]), i, sep = "|||||||"))
}

attributes(tea) # check

# DONE
head(tea)
str(tea)

tea$bev_dt<-tea$bev_dt/tea$bev_gsmt



# save(tea, file="BTW_Indikatoren_2017.Rdata")
# load("BTW_indikatoren.Rdata")


########################################################################################################
################################ 2.DATA PREP: RESULTS BTW 2013 #########################################
########################################################################################################

# data source: https://www.bundeswahlleiter.de/bundestagswahlen/2017/strukturdaten.html
butter <- read.csv("kerg.csv", sep=";", header=F, stringsAsFactors = F) # load data

# rename the variables
name.vec <- c() # create emtpy verctor
# replicate the category of the columns-sets (party names) for every column in every set (4col=1set)
for (i in seq(from=4, to=length(butter)-1, by=4)) butter[3,c(i+1:3)] <- butter[3,i] 
butter[4,seq(from=5, to=length(butter), by=4)] <- "Erststimmen" # define the sub-category (Erststimmen) for every column in every set
butter[4,seq(from=7, to=length(butter), by=4)] <- "Zweitstimmen" # define the sub-category (Zweitstimmen) for every column in every set
# create a vector with unique columnnames: combination of category[party] * subcategory[Erst- | Zweitstimmen] * period[current=Endgültig | last=Vorperiode]
for (i in 1:length(butter)) name.vec[i] <- gsub(" ", "", paste(butter[3:5, i], collapse ="")) 
butter <- butter[-c(1:5),] # get rid of the messy header

colnames(butter) <- c("wk_nr", "name", "land", name.vec[4:length(name.vec)]) # set the columnnames we just created

# delete all rows and columns with no information
butter <- butter[- which(butter$wk_nr==""),]
butter <- butter[,-c(length(butter))]

# tidy up `land` and `name` (function was defined in 0.)
butter$land <- jam(butter$land)
butter$name <- jam(butter$name)

# make all numerical variables numeric
butter[,c(1,3:length(butter))] <- sapply(butter[,c(1,3:length(butter))], as.numeric)

# we need to adjust the Länder-names:
# load("BTW_Indikatoren_2017.Rdata") 
butter <- butter%>% filter(!(land==99))# paste the names of the corresponding indicator data
butter <- butter[order(butter$wk_nr),] # order the data according to the `wk_nr`

# merge CDU and CSU
cdu.vec <- grep("ChristlichDemo", colnames(butter))
csu.vec <- grep("Christlich-Soz", colnames(butter))

for (i in 1:4) butter[212:257,cdu.vec[i]] <- butter[212:257,csu.vec[i]]
colnames(butter) <- gsub("ChristlichDemokratischeUnionDeutschlands", "Union", colnames(butter))
butter <- select(butter, select=-grep("Christlich-Soz", colnames(butter)))


# DONE
butter
str(butter)


# save(butter, file="BTW_ergebnisse_13_umgerechnet.Rdata")

########################################################################################################
####################################### 3. SUBSETTING ##################################################
########################################################################################################


# load("BTW_ergebnisse_13_umgerechnet.Rdata") # butter
# load("BTW_Indikatoren_2017.Rdata") # tea

# we only concentrate on Wahlkreise, we don't need the numbers for Länder or Deutschland (wk_nr<900)
tea.sub <- filter(tea, !wk_nr>900)
# check whether the rows (Wahlkreise) match
tea.sub$name == butter$name 
tea.sub$wk_nr == butter$wk_nr

# get rid of "Berlin-West" and "Berlin-Ost" (no matching indicators)
butter.sub <- butter%>%filter(!name%in%c("Berlin-West", "Berlin-Ost"))
# check whether the rows (Wahlkreise) match
tea.sub$name == butter.sub$name 
tea.sub$wk_nr == butter.sub$wk_nr

# we create vectors containing all columnnames for Zweitstimmen, and Erststimmen
zweitstimmen.vec <- grep("Zweitstimmen",colnames(butter.sub), value=TRUE)[-c(1:8)] %>% grep("Vorläufig", ., value=TRUE)
erststimmen.vec <- grep("Erststimmen",colnames(butter.sub), value=TRUE)[-c(1:8)] %>% grep("Vorläufig", ., value=TRUE)

butter.sub <- butter.sub[,c(1:3, grep("Vorläufig",colnames(butter.sub)))]

# now we loop: every number of Zweitstimmen for every party in a Wahlkreis will be divided by the total number of VALID votes in a Wahlkreis (creates the percentages); same for Erststimmen
for (i in zweitstimmen.vec) butter.sub[,i] <- (butter.sub[,i]/butter.sub$GültigeZweitstimmenVorläufig)*100
for (i in erststimmen.vec) butter.sub[,i] <- (butter.sub[,i]/butter.sub$GültigeErststimmenVorläufig)*100

# check whether the rowsums are all 100 (==the total % of votes in a Wahlkreis is 100)
rowSums(butter.sub[,grep("Zweitstimmen",colnames(butter.sub))][-c(1:4)], na.rm=TRUE)
rowSums(butter.sub[,grep("Erststimmen",colnames(butter.sub))][-c(1:4)], na.rm=TRUE)


# create subsets with only Erststimmen- and Zweitstimmen-variables
zweitstimmen <- butter.sub[,grep("Zweitstimmen", colnames(butter.sub), value=TRUE)[-c(1:2)]] # selects only columns containing "Zweitstimmen" in their name
# the we furtehr select only those columns containing any of the big parties in their name
zweitstimmen.gross <- zweitstimmen[grep(paste(c("CDU", "CSU", "SPD", "FDP", "LINKE", "GRÜNE", "AfD",
                                                "Union", "SozialdemokratischePartei", "FreieDemokratische",
                                                "DIELINKE", "DIEGRÜNEN", 
                                                "Alternative"), collapse="|"), colnames(zweitstimmen), value=TRUE)] 
head(zweitstimmen.gross) # check
# repeat for erststimmen
erststimmen <- butter.sub[,grep("Erststimmen", colnames(butter.sub), value=TRUE)[-c(1:2)]]
erststimmen.gross <- erststimmen[grep(paste(c("CDU", "CSU", "SPD", "FDP", "LINKE", "GRÜNE", "AfD",
                                              "Union", "SozialdemokratischePartei", "FreieDemokratische",
                                              "DIELINKE", "DIEGRÜNEN",
                                              "Alternative"), collapse="|"), colnames(erststimmen), value=TRUE)] 
head(erststimmen.gross)

#add wk nr, wk name and land name to final dataframe
zweitstimmen.gross<-cbind.data.frame("wk_nr"=butter.sub$wk_nr, "name"=butter.sub$name, "land"=tea.sub$land, zweitstimmen.gross)
erststimmen.gross<-cbind.data.frame("wk_nr"=butter.sub$wk_nr, "name"=butter.sub$name, "land"=tea.sub$land, erststimmen.gross)


########################################################################################################
################ 4. AUTOMATED REG ANALYSES WITH CHAINED SERIAL PLOTTING ################################
########################################################################################################

# replace all 0 by NA's [VERY DEBATEABLE!!!!!!!!]
zweitstimmen.gross[zweitstimmen.gross==0] <- NA 

# color vector (party colors)
farben <- c("black", "firebrick1", "violet", "limegreen", "gold", "dodgerblue")

# the automated regression loop with chained serial plotting
for (m in 4:length(zweitstimmen.gross)){ # looping over the number of parties
  # first we create a matrix with r-squared values of the linear regressions for every indicator on the Zweitstimmen-shares of every party
  james <- matrix(,length(tea), 2) # empty 36x2 matrix
  
  for (i in 7:length(tea)){ # looping over the number of indicators
    james[i,1] <- summary(lm(zweitstimmen.gross[,m] ~ tea.sub[,i]))$r.squared # regression analysis; extracting r-squared
    james[i,2] <- i # attach the column number of every indicator
  }
  
  james <- na.omit(james[order(james[,1], decreasing = TRUE),]) # order the matrix by r-squared values, omitting NA's
  
  # open 5x2 plot panel
  par(mfrow=c(5,2), oma = c(0,2,2,0) + 0.1,
      mar = c(3,2,1,1) + 0.4) 
  # chained loop for serial plotting
  for (k in james[,2]){ # loop over the columnnumbers of the indicators ordered by r-squared values
    plot(tea.sub[,k], zweitstimmen.gross[,m], pch=19, # scatterplot: Zweitstimmen-share party a ~ indicator x
         bty="n", # no border
         ylab="", # no y labels
         xlab="", # no x labels
         main="", # no title
         col=c(alpha(farben[m-3], 0.4)), # colors according to the color vector
         cex.axis=0.6) # smaller axis ticks
    title(comment(tea[,k])[1], cex.main=0.7) # take the extended variable names (attached as comment to every indicator) as title for each plot
    abline(lm(zweitstimmen.gross[,m] ~ tea.sub[,k]), col=alpha("black", 0.6)) # add regression line
    mtext(comment(tea[,k])[2], line = -8, cex=0.4) # add the unit of each variable as x label (attached as comment to every indicator)
    legend("topright", # add legend
           paste("R^2=", round(summary(lm(zweitstimmen.gross[,m] ~ tea.sub[,k]))$r.squared,3)), # print r-squared value
           cex=0.6, # smaller fontsize
           bty="n") # no border
    if (k %in% james[,2][c(1,11,21)]){mtext("Prozent Zweitstimmen", side=2, cex=1, outer = TRUE) # for every 10. iteration (when a new plot panel is opened) we want to call a y axis label for the whole panel...
      title(paste(colnames(zweitstimmen.gross)[m], ": Korrelationen mit allen Indikatoren"), outer=TRUE)} #... and a title
  }
  
}


########################################################################################################
################ 5. R-SQUARED-VALUES  ################################
########################################################################################################
library(reshape2)
library(tibble)
get_rsqu <- function (y,x) summary(lm(zweitstimmen.gross[,y] ~ tea.sub[,x]))$r.squared # function to extract r_squared
get_coef <- function (y,x) summary(lm(zweitstimmen.gross[,y] ~ tea.sub[,x]))$coefficients[2,1] # function to extract estimate

# create empty lists
rsqu <- list()
estim <- list()
r <- list()

library(Hmisc)
get_r <- function (y,x) cor(cbind.data.frame(zweitstimmen.gross[,y],tea.sub[,x]), method="spearman")[2,1]  # type can be pearson or spearman

# loop to create lists of r_squared and estimates
n_var <- length(zweitstimmen.gross) 
for (i in 7:length(tea.sub)) rsqu[[i]] <- sapply(4:n_var, get_rsqu, x=i) 
for (i in 7:length(tea.sub)) r[[i]] <- sapply(4:n_var, get_r, x=i) 
for (i in 7:length(tea.sub)) estim[[i]] <- sapply(4:n_var, get_coef, x=i)

rearrange_list <- function(x,y) sapply(y, '[[', x) # function to rearrange lists
estim <- lapply(1:6, rearrange_list, y=r) # rearrange estimates to build groups per party

corr <- data.frame(matrix(unlist(rsqu), nrow=30, byrow=T)) %>% # make rsqu a dataframe
  setNames(., gsub("ZweitstimmenVorläufig", "", colnames(zweitstimmen.gross[,4:n_var]))) %>% # set colnames; only party names (without ZweitstimmenVorläufig)
  `rownames<-`(colnames(tea.sub[,7:length(tea.sub)])) %>% # set the variable names as rownames
  rownames_to_column() %>%  # transform rownames to variable
  melt(., id.var=c("rowname")) %>% # make a longtable
  mutate(coefs=unlist(estim)) %>%  # add coefficients as column
  mutate(abs_coef=abs(coefs)) %>%
  arrange(desc(abs_coef)) %>% # order by r_squ
  setNames(., c("variable", "party", "r_2", "estimate", "abs_estimate")) # rename cols
corr




########################################################################################################
################ 6. FINAL PLOTS  ################################
########################################################################################################


########################################################################################################
# Setup

setwd("mypath/graphics/scatterplots")

# Set party vector and partynames for the six largest parties
party<-c("Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE")
partyname<-c("SPD", "Union (CDU/CSU)", "FDP", "Grüne", "AfD", "Die Linke")

# Define color scheme for each party
colSPDSozial<-c("#F4D7D3","#EAAEA8","#DF857B","#D3574A","#C31906")
colCDUUnion<-c("#C7C7C7","#939393","#626262","#353535","#0A0A0A")
colFDPFreieDem<-c("#F6F5D0","#EDECA0","#E4E16D","#DBD738","#D1CC00")
colGRÜNE<-c("#E0EDD3","#C2DBA7","#A4CA7B","#85B84F","#66A622")
colAlternativeAfD<-c("#CEE7F4","#9ED0E9","#6CB8DE","#389FD3","#0084C7")
colLINKE<-c("#E5D8EC","#CDB1D9","#B58CC7","#9C66B5","#8440A3")

colorFrame<-data.frame(colCDUUnion, colSPDSozial, colLINKE, colGRÜNE, colFDPFreieDem, colAlternativeAfD)

# Disable scientific notation
options(scipen=999)


########################################################################################################
# Plot plain scatterplot: one indicator, six parties, plus small multiples

party<-c("Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE")
partyname<-c("SPD", "Union (CDU/CSU)", "FDP", "Grüne", "AfD", "Die Linke")

#pick an indicator from comment.vec
comment.vec
indicator<-"Verfügbares Einkommen d. privaten Haushalte"
indiData<-tea.sub[,which(comment.vec==indicator)]

#axis limits for the indicator
xmin<-floor(min(indiData))
xmax<-ceiling(max(indiData))
xsteps<-round((xmax-xmin)/5)

#plot
plot_list_scatter<-list()
for (p in 1:length(party)){
  voteData<-zweitstimmen.gross[,grep(paste0(party[p]),colnames(zweitstimmen.gross))]
  cols<-as.character(colorFrame[5,grep(paste0(party[p]),colnames(colorFrame))]) %>% paste0(.,"77")
  #axis limits
  ymin<-floor(min(voteData))
  ymax<-ceiling(max(voteData))
  ysteps<-round((ymax-ymin)/5)
  #create dataframe
  indiXvote<-cbind.data.frame(indiData, voteData)
  filename<-paste0(paste0(indicator),"_",gsub("/","",partyname[p]),".svg")
  title.chars <- paste0("Stimmenanteil ", partyname[p])
  #plot
  plotp<-ggplot() + 
    geom_point(data=indiXvote, aes(indiData, voteData), col=cols, fill=cols, size=2) + 
    geom_smooth(data=indiXvote, aes(indiData, voteData), method="lm", se=F, color="#13175f", size=0.5) +
    scale_x_continuous(name = indicator, expand = c(0,0)) +
    scale_y_continuous(expand = c(0,0)) +
    ggtitle(paste0("Stimmenanteil ", partyname[p])) +
    theme_minimal()+
    theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
          axis.title.x=element_text(family="GT America", color="#05032d", size=13, hjust=1.08, vjust=-4), # or play around with vjust=-4/nchar(title.chars)
          axis.title.y=element_blank(),
          plot.title = element_text(family="GT America", color="#05032d", size=13, hjust=-0.1), # or play around with hjust=-0.12*(nchar(indicator)/10)
          panel.grid = element_line(color="#ececf0", size=.3),
          plot.margin=unit(c(1,1,1.5,1.2),"cm")) +
    coord_cartesian(xlim=c(pretty(xmin)[1],pretty(xmax)[2]), ylim = c(pretty(ymin)[1],pretty(ymax)[2])) #adapt the "-5" depending on indicator - otherwise we may cut scatters
  plot_list_scatter[[p]]<-plotp
  ggsave(filename, device=svglite, width=8, height=8)
}

filename<-paste0(paste0(indicator),"_","smallmult", ".svg")
svglite(filename, width=14, height=10)
grid.arrange(plot_list_scatter[[2]], plot_list_scatter[[1]], plot_list_scatter[[3]], plot_list_scatter[[4]], plot_list_scatter[[5]], plot_list_scatter[[6]], ncol=3, nrow=2)
dev.off()





########################################################################################################
# Plot plain scatterplot: one party, six indicators, plus small multiples

#pick party from "Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE"
partyi<-"Altern" #ADAPT
partynm<-partyname[grep(paste0(partyi), party)]
voteData<-zweitstimmen.gross[,grep(paste0(partyi),colnames(zweitstimmen.gross))]
cols<-as.character(colorFrame[5,grep(paste0(partyi),colnames(colorFrame))]) %>% paste0(.,"77")

#pick 6 indicators from comment.vec
comment.vec
indicator<-c("Anteil 18-24-jährige", 
             "Anteil 60-74-jährige", 
             "Kita-Betreuung", 
             "Anteil Bev. mit Migrationshintergrund", 
             "Anteil Bev. ohne Kirche",
             "Verfügbares Einkommen d. privaten Haushalte")


indiDataAll<-data.frame(matrix(NA, nrow=299, ncol=length(indicator)))
colnames(indiDataAll)<-indicator
for (i in 1:length(indicator)){indiDataAll[i]<-tea.sub[,which(comment.vec==indicator[i])]}

#axis limits for the party
ymin<-floor(min(voteData))
ymax<-ceiling(max(voteData))
ysteps<-round((ymax-ymin)/5)

#plot
plot_list_scatter<-list()
for (i in 1:length(indiDataAll)){
  #axis limits for the indicator
  indiData<-indiDataAll[,i]
  xmin<-floor(min(indiData))
  xmax<-ceiling(max(indiData))
  xsteps<-round((xmax-xmin)/5)
  #create dataframe
  indiXvote<-cbind.data.frame(indiData, voteData)
  filename<-paste0(paste0(indicator[i]),"_",gsub("/","",partynm),".svg")
  #plot
  plotp<-ggplot() + 
    geom_point(data=indiXvote, aes(indiData, voteData), col=cols, fill=cols, size=1.5) + 
    geom_smooth(data=indiXvote, aes(indiData, voteData), method="lm", se=F, color="#13175f", size=0.5) +
    scale_x_continuous(name = colnames(indiDataAll)[i], expand = c(0,0)) +
    scale_y_continuous(expand = c(0,0)) +
    ggtitle(paste0("Stimmenanteil ", partynm)) +
    theme_minimal()+
    theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
          axis.title.x=element_text(family="GT America", color="#05032d", size=13, hjust=1.08, vjust=-4),
          axis.title.y=element_blank(),
          plot.title = element_text(family="GT America", color="#05032d", size=13, hjust=-0.1),  
          panel.grid = element_line(color="#ececf0", size=.3),
          plot.margin=unit(c(1,1,1.5,1.2),"cm")) +
    coord_cartesian(xlim=c(pretty(xmin)[1],pretty(xmax)[2]), ylim = c(pretty(ymin)[1],pretty(ymax)[2])) #adapt the "+x"/"-y" depending on indicator - otherwise we may cut scatters
  plot_list_scatter[[i]]<-plotp
  ggsave(filename, device=svglite, width=8, height=8)
}

filename<-paste0(paste0(partynm),"_","smallmult", ".svg")
svglite(filename, width=14, height=10)
grid.arrange(plot_list_scatter[[1]], plot_list_scatter[[2]], plot_list_scatter[[3]], plot_list_scatter[[4]], plot_list_scatter[[5]], plot_list_scatter[[6]], ncol=3, nrow=2)
dev.off()




########################################################################################################
# Plot scatterplot with max and min values annotated as wahlkreisname and highlight

#pick party from "Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE"
partyi<-"GRÜNE" #ADAPT
partynm<-partyname[grep(paste0(partyi), party)]
voteData<-zweitstimmen.gross[,grep(paste0(partyi),colnames(zweitstimmen.gross))]

cols<-as.character(colorFrame[5,grep(paste0(partyi),colnames(colorFrame))]) %>% paste0(.,"77")
colHighlight<-"#2c32bd"

#pick an indicator from comment.vec
comment.vec
indicator<-"Verfügbares Einkommen d. privaten Haushalte"
indiData<-tea.sub[,which(comment.vec==indicator)]

#axis limits for the indicator and the party
xmin<-floor(min(indiData))
xmax<-ceiling(max(indiData))
xsteps<-round((xmax-xmin)/5)
ymin<-floor(min(voteData))
ymax<-ceiling(max(voteData))
ysteps<-round((ymax-ymin)/5)

#create dataframe
indiXvote<-cbind.data.frame(indiData, voteData, "wk_nr"=zweitstimmen.gross$wk_nr, "name"=zweitstimmen.gross$name, "land"=zweitstimmen.gross$land)

#if you want to label extrema by indicator, find instances with 5 maximal and 5 minimal indicator values (possibly adapt)
indi_ord<-sort(indiData, decreasing=T)

toLabel<-c(indi_ord[1:5],indi_ord[(length(indi_ord)-4):length(indi_ord)])
#or with only 2 or whatever
toLabel<-c(indi_ord[1:2],indi_ord[(length(indi_ord)-1):length(indi_ord)])

#if you want to label extrema by vote share
vote_ord<-sort(voteData, decreasing=T)
toLabel<-c(vote_ord[1:5], vote_ord[length(vote_ord)])

colVector<-c()
for(j in 1:nrow(indiXvote)){ifelse(indiXvote$indiData[j]%in%toLabel, colVector[j]<-colHighlight, colVector[j]<-cols)}
indiXvoteXcol<-cbind.data.frame(indiXvote, "colVector"=colVector)


filename<-paste0("labelled","_",paste0(indicator),"_",paste0(partynm),".svg")
ggplot() + 
  geom_point(data=indiXvoteXcol, aes(indiData, voteData), col=colVector, fill=colVector, size=1.5) + 
  #if you want to label extrema by indicator
  #geom_text(data=indiXvoteXcol, aes(indiData, voteData, label=ifelse(indiData %in% toLabel,as.character(indiXvoteXcol$name),'')),hjust=0,vjust=0) +
  #if you want to label estrema by vote share
  geom_text(data=indiXvoteXcol, aes(indiData, voteData, label=ifelse(voteData %in% toLabel,as.character(indiXvoteXcol$name),'')),hjust=0,vjust=0) +
  scale_fill_identity() +
  scale_x_continuous(name = paste0(indicator), expand = c(0,0)) +
  scale_y_continuous(expand = c(0,0)) +
  ggtitle(paste0("Stimmenanteil ", partynm)) +
  theme_minimal()+
  theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
        axis.title.x=element_text(family="GT America", color="#05032d", size=13, hjust=1.08, vjust=-4),
        axis.title.y=element_blank(),
        plot.title = element_text(family="GT America", color="#05032d", size=13, hjust=-0.1),  
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(2,2,2,2),"cm")) +
  coord_cartesian(xlim=c(pretty(xmin)[1],pretty(xmax)[2]), ylim = c(pretty(ymin)[1],pretty(ymax)[2])) #adapt the "+x"/"-y" depending on indicator - otherwise we may cut scatters
ggsave(filename, device=svglite, width=8, height=8)

#get labels
indiXvote$name[which(indiData %in% toLabel)]




########################################################################################################
# scatterplot with some bundesland highlighted

#pick party from "Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE"
partyi<-"GRÜNE" #ADAPT
partynm<-partyname[grep(paste0(partyi), party)]
voteData<-zweitstimmen.gross[,grep(paste0(partyi),colnames(zweitstimmen.gross))]

cols<-as.character(colorFrame[5,grep(paste0(partyi),colnames(colorFrame))]) %>% paste0(.,"77")
colHighlight<-"#13175f"

#pick an indicator from comment.vec
comment.vec
indicator<-"Verfügbares Einkommen d. privaten Haushalte"
indiData<-tea.sub[,which(comment.vec==indicator)]

#create dataframe
indiXvote<-cbind.data.frame(indiData, voteData, "wk_nr"=zweitstimmen.gross$wk_nr, "name"=zweitstimmen.gross$name, "land"=zweitstimmen.gross$land)

#axis limits for the indicator and the party
xmin<-floor(min(indiData))
xmax<-ceiling(max(indiData))
xsteps<-round((xmax-xmin)/5)
ymin<-floor(min(voteData))
ymax<-ceiling(max(voteData))
ysteps<-round((ymax-ymin)/5)

setwd("mypath/graphics/scatterplots/highlights")
#plot
plot_list_scatter<-list()
for (i in unique(indiXvote$land)){
  #create color vector
  colVector<-c()
  for(j in 1:nrow(indiXvote)){ifelse(indiXvote$land[j]==paste0(i), colVector[j]<-colHighlight, colVector[j]<-cols)}
  indiXvoteXcol<-cbind.data.frame(indiXvote, "colVector"=colVector)
  filename<-paste0("highlighted","_",paste0(i),"_",paste0(indicator),"_",gsub("/","",partynm),".svg")
  #plot
  plotp<-ggplot() + 
    geom_point(data=indiXvote, aes(indiData, voteData), col=colVector, fill=colVector, size=1.5) + 
    scale_fill_identity() +
    scale_x_continuous(name = colnames(indiDataAll)[i], expand = c(0,0)) +
    scale_y_continuous(expand = c(0,0)) +
    ggtitle(paste0("Stimmenanteil ", partynm)) +
    theme_minimal()+
    theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
          axis.title.x=element_text(family="GT America", color="#05032d", size=13, hjust=1.08, vjust=-4),
          axis.title.y=element_blank(),
          plot.title = element_text(family="GT America", color="#05032d", size=13, hjust=-0.1),  
          panel.grid = element_line(color="#ececf0", size=.3),
          plot.margin=unit(c(1,1,1.5,1.2),"cm")) +
    coord_cartesian(xlim=c(pretty(xmin)[1],pretty(xmax)[2]), ylim = c(pretty(ymin)[1],pretty(ymax)[2])) #adapt the "+x"/"-y" depending on indicator - otherwise we may cut scatters
  plot_list_scatter[[i]]<-plotp
  ggsave(filename, device=svglite, width=8, height=8)
}





#######################################################################
#plot scatterplot with particular bundesländer in a darker color shade

#pick party from "Sozial", "Union", "FreieDem", "GRÜNE", "Altern", "LINKE"
partyi<-"Freie" #ADAPT
partynm<-partyname[grep(paste0(partyi), party)]
voteData<-zweitstimmen.gross[,grep(paste0(partyi),colnames(zweitstimmen.gross))]

cols<-as.character(colorFrame[5,grep(paste0(partyi),colnames(colorFrame))]) %>% paste0(.,"77")
colHighlight<-"#13175f"

#pick an indicator from comment.vec
comment.vec
indicator<-"Verfügbares Einkommen d. privaten Haushalte"
indiData<-tea.sub[,which(comment.vec==indicator)]

#bundesländer to highlight
bundeslaender<-as.factor(c("Baden-Württemberg"))

#create dataframe
indiXvote<-cbind.data.frame(indiData, voteData, "wk_nr"=zweitstimmen.gross$wk_nr, "name"=zweitstimmen.gross$name, "land"=zweitstimmen.gross$land)

#create color vector
colVector<-c()
for(j in 1:nrow(indiXvote)){ifelse(indiXvote$land[j] %in% bundeslaender, colVector[j]<-colHighlight, colVector[j]<-cols)}
indiXvoteXcol<-cbind.data.frame(indiXvote, "colVector"=colVector)

#axis limits for the indicator and the party
xmin<-floor(min(indiData))
xmax<-ceiling(max(indiData))
xsteps<-round((xmax-xmin)/5)
ymin<-floor(min(voteData))
ymax<-ceiling(max(voteData))
ysteps<-round((ymax-ymin)/5)


fdp<-ggplot() + 
  geom_point(data=indiXvote, aes(indiData, voteData), col=colVector, fill=colVector, size=1.5) + 
  geom_smooth(data=indiXvote, aes(indiData, voteData), method="lm", se=F, color="#13175f", size=0.5) +
  scale_fill_identity() +
  scale_x_continuous(name = colnames(indiDataAll)[i], expand = c(0,0)) +
  scale_y_continuous(expand = c(0,0)) +
  ggtitle(paste0("Stimmenanteil ", partynm)) +
  theme_minimal()+
  theme(axis.text=element_text(family="GT America", color="#05032d", size=11), 
        axis.title.x=element_text(family="GT America", color="#05032d", size=13, hjust=1.08, vjust=-4),
        axis.title.y=element_blank(),
        plot.title = element_text(family="GT America", color="#05032d", size=13, hjust=-0.1),  
        panel.grid = element_line(color="#ececf0", size=.3),
        plot.margin=unit(c(1,1,1.5,1.2),"cm")) +
  coord_cartesian(xlim=c(pretty(xmin)[1],pretty(xmax)[2]), ylim = c(pretty(ymin)[1],pretty(ymax)[2])) #adapt the "+x"/"-y" depending on indicator - otherwise we may cut scatters



filename<-paste0(paste0(indicator),"_","smallmult", ".svg")
svglite(filename, width=14, height=10)
grid.arrange(plot_list_scatter[[2]], spd, fdp, plot_list_scatter[[4]], afd, linke, ncol=3, nrow=2)
dev.off()



