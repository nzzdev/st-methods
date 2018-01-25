### MISE EN PLACE ###
library(dplyr)
library(ggplot2)
library(waffle)
library(knitr)
library(tidyr)
library(rgdal)

setwd("mypath/graphics")

#---------------------------------------------------------------------------------------------------------------------
### READ AND CONFIGURE DATA ###

## candidates ##

#smartvote (for zip)
candsv<-read.csv("mypath/data/kandidaten/candidates_2018-01-18_nzz_smartvote_ALL.csv", sep=";", header=T)

#open data zurich (for all other variables)
candodz<-read.csv("mypath/data/kandidaten/grw-2018-alle-kandidierenden-ogd.csv", header=T)


#---------------------------------------------------------------------------------------------------------------------
### DATA PROCESSING ###

# sex per party
sexCandParty<-candodz %>%
  mutate(gender = G %>%
           as.character %>%
           gsub("W", "Frauen", .) %>%
           gsub("M", "Männer", .)) %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  group_by(gender, Partei) %>%
  summarise("Anzahl"=n()) %>%
  group_by(Partei) %>%
  mutate("Anteil"=round(100*Anzahl/sum(Anzahl),1)) %>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>% 
  select(gender, Partei, Anteil) %>%
  spread(gender, Anteil) %>%
  arrange(desc(Frauen))%>%
  as.data.frame()
sexCandParty

# write
write.table(sexCandParty, file="mypath/data/kandidaten/sexCandParty.txt", row.names = F, sep="\t", quote=F)


## age per party
brk<-c(0,19,39,59,79,99,119)
candodz %>% 
  mutate("binned"=cut((2017-candodz$GebJ), brk)) -> candodz

candodz$binned %>% 
  gsub("\\(|\\]", "",.) %>% 
  gsub(",", "-",.) %>% 
  gsub("79-99|99-119", ">= 80",.) %>% 
  as.character -> candodz$binned

fd<-c("19-", "39-", "59-", "79-")
rpl<-c("20-", "40-", "60-", "80-")
for(i in seq_along(fd)) candodz$binned <- gsub(fd[i], rpl[i], candodz$binned, fixed = TRUE)

# buckets
ageCandPartyGroups<-
  candodz[which(!is.na(candodz$binned)),] %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  group_by(binned, Partei) %>%
  summarise("Anzahl"=n()) %>%
  group_by(Partei) %>%
  mutate("Anteil"=round(100*Anzahl/sum(Anzahl), digits=1)) %>%
  arrange(desc(Partei, binned))%>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>% 
  select(binned, Partei, Anteil) %>%
  spread(binned, Anteil) %>%
  arrange(desc(`20-39`)) %>%
  as.data.frame()
ageCandPartyGroups

write.table(ageCandPartyGroups, file="mypath/data/kandidaten/ageCandPartyGroups.txt", row.names = F, sep="\t", quote=F)


# median
candodz %>% 
  mutate(ageApprox=2017-candodz$GebJ) -> candodz

ageCandPartyMedian<-
  candodz %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  group_by(Partei) %>%
  summarise(medianAge=median(ageApprox[which(!is.na(ageApprox))])) %>%
  arrange(desc(medianAge)) %>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>% 
  as.data.frame()
ageCandPartyMedian

# write 
write.table(ageCandPartyMedian, file="mypath/data/kandidaten/ageCandPartyMedian.txt", row.names = F, sep="\t", quote=F)


## first name per party
firstnameCandParty<-
  candodz %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  group_by(Vorname, Partei) %>%
  summarise("Anzahl"=n()) %>%
  group_by(Partei) %>%
  mutate("Anteil"=round(100*Anzahl/sum(Anzahl), digits=1)) %>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>% 
  select(Vorname, Partei, Anzahl) %>%
  arrange(desc(Anzahl)) %>%
  as.data.frame()
firstnameCandParty #6xPeter und 5xMartin in SVP. schon sinnvoll, hier altersgruppen separiert anzuschauen

# write
write.table(firstnameCandParty, file="mypath/data/kandidaten/firstnameCandParty.txt", row.names = F, sep="\t", quote=F)

# look at one age group as first names change over time. 40-59 is the largest group in most parties (all but sp)
firstnameCandPartyAge4059<-
  candodz %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  filter(binned=="20-39") %>% 
  group_by(firstname, Partei) %>%
  summarise("Anzahl"=n()) %>%
  group_by(Partei) %>%
  mutate("Anteil"=round(100*Anzahl/sum(Anzahl), digits=1)) %>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>% 
  select(firstname, Partei, Anzahl) %>%
  arrange(desc(Anzahl)) %>%
  as.data.frame()
firstnameCandPartyAge4059
summary(firstnameCandPartyAge4059)


## district of residence per party

# hack for ZIP-district-correspondences
plz<-read.csv("mypath/data/kandidaten/plz/gastwirtschaftsbetriebeper20161231.csv", header=T)

plz<-plz[,c(5,11)] %>% 
  group_by(PLZ, KreisSort) %>% 
  summarize()

plz_red<-data.frame()
for(i in unique(plz$PLZ)){
  plzi<-subset(plz, plz$PLZ==i)
  ifelse(nrow(plzi)==1, kreisei<-paste0(plzi$KreisSort), 
         ifelse(nrow(plzi)==2, kreisei<-paste(plzi$KreisSort[1], plzi$KreisSort[2], sep=","),
                kreisei<-paste(plzi$KreisSort[1], plzi$KreisSort[2], plzi$KreisSort[3], sep=",")))
  plz_redi<-cbind(paste0(i), kreisei)
  plz_red<-rbind(plz_red, plz_redi)
}
colnames(plz_red)<-c("PLZ", "Wohnkreise")

# zipcodes that are not matched to district in plz
candsv[which(!(candsv$zip %in% plz$PLZ)),7] %>% 
  table() # 8000 seems to be a weird zip

plz_red$PLZ<-as.character(plz_red$PLZ)
plz_red$Wohnkreise<-as.character(plz_red$Wohnkreise)
plz_red<-rbind(plz_red, c("8000", "NA"))

# add this info to candsv
candsv_kreis<-merge(candsv, plz_red, by.x="zip", by.y="PLZ", all.x=T, stringsAsFactors=F)

# check notation of wahlkreise in candsv
table(candsv$dist) %>% 
  sort(., decreasing=T) 

# change notation and add to candsv
splitted<-strsplit(as.character(candsv_kreis$district), "kreis ")
splitted_red<-c()
for (i in 1:length(splitted)) splitted_red[i]<-splitted[[i]][2]
splitted_red<-gsub("\\+", ",", splitted_red)
splitted_red

candsv_kreis %>% 
  mutate("Wahlkreis"=splitted_red) -> candsv_kreis

wahlkreise<-strsplit(candsv_kreis$Wahlkreis, ",")
wohnkreise<-strsplit(candsv_kreis$Wohnkreis, ",")

# who does not live in the district that they want to represent? 
wohntDa<-c()
for (i in 1:length(wahlkreise)){
  responseVector<-wahlkreise[[i]] %in% wohnkreise[[i]]
  responsei<-ifelse(TRUE %in% responseVector, "ja", "nein")
  wohntDa<-c(wohntDa, responsei)
}

candsv_kreis %>% 
  mutate("wohntDa"=as.factor(wohntDa)) -> candsv_kreis

# do some parties have more candidates that live in the same district?
candsv_kreis[which(candsv_kreis$Wohnkreise!="NA"),] %>% 
  mutate(Partei = party_short %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  group_by(Partei, wohntDa) %>% 
  summarise(counts=n()) %>% 
  group_by(Partei) %>% 
  mutate(perc=round(100*counts/sum(counts), digits=1)) %>%
  filter(wohntDa=="nein") %>% 
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>% 
  #select(Partei, perc) %>%
  arrange(desc(perc)) -> kreisAusserhalbParty
kreisAusserhalbParty

#write
write.table(kreisAusserhalbParty, file="mypath/data/kandidaten/kreisAusserhalbParty.txt", row.names = F, sep="\t", quote=F)


## profession per party

# get overview
head(sort(table(candodz$Beruf), decreasing=T),40)

#replace empty by NA
candodz$Beruf<-gsub("^$", NA, candodz$Beruf)

# categorize, maybe create additional column for this; we only use the first occupation for candidates that name several occupations / professions in order to avoid candidates to appear in several categories
vec <- c("juris|anwalt|anwält|gerichtsschreib|richter|lic..*iur.|MLaw|LL.M.|strafverteidiger|dipl. iur.", 
         "lehrer|heilpäd|katechet|kindergärt|pädagog|erwachsenenbildn|ausbildungsleit|krippenleit", # without lehrbeauftragte, see vector "nope" below
         "arzt|ärztin|Dr..*med.|chirurg",
         "wiss.*mitarb|wissenschaft|forscher|professor|dozent|lehrbeauftr|doktorand|hochschullehr|historik|physik|soziolog|biolog|chemik|politolog|ökolog|geogra|naturwissenschaftler|theologe|zoolog|ethnolog|Japanologe|sinologin|math..*eth|mathematik|dipl. Natw. ETH|MSc.*ETH|dipl.*ETH|germanist", # wissenschafter, wissenschaftliche mitarbeiter, dozenten but not studierende, see vector "nope" below
         "studier|student|auszubildende|in Ausbildung|i\\. a\\.|schüler|stud.|maturand", # without studienleiter, see vector "nope" below
         "rentn|pensioni|pensionä|pens.",
         "ökonom|betriebswirt|volkswirt|oekonom|consultant|unternehmensberater|lic.oec.|mag. oec.|lic..*oec.|dr. oec.|economist",
         "unterne.*mer|selbstst|selbst.|geschäftsinhaber|inhaber|entrepreneur|freischaffend|freelance",
         "informatik|it-|software|programmier|it engineer", 
         "pfleg|pfelg|pleg|krank|betagtenbetr|praxisass|zahnarztgehilf|gesundheits|hebamme|pharma-assistent|sanitäter|fachmann gesundheit",
         "sozialarb|sozialpäd|sozialdiak|sozialber|sozi.*arb|animator|Assistentin Mütter|familienberat|Jugendbeauftragte|tagesstätte|kinder|asylkoordinator|flüchtlingshelf|jugendberater",
         "verkauf|verkäuf|detailhandel|sales",
         "kaufm|kauffrau|kfm|sachbearb|bankangest|bankfach|büroangest|postangeste|versicherungsmitarbei|versicherungsfach|versicherungs-fach|kv-|gemeindeschreiber|^angestellter|pensionskassenexp|bezirksratsschreiberin",
         "geschäftsführ|geschäftsleiter|geschäftleiter|abteilungsleiter|projektleiter|schul.*leiter|direktor|teamleiter|verantwortliche|chef|head|leiter|leitung|präsident",
         "architek|raumplan|stadtplan|quartierentwick|bau.*leiter|bauführer|bauherr|verkehrsplan",
         "buchhalter",
         "hausfrau|familienfrau|hausmann|familienmanag|familien-ceo",
         "ing\\.|ingenieu|dipl.*Ing",
         "poliz",
         "künstler|kunstmaler|kunst-|kunstexperte|gestalter|produktgestalter|gra.*iker|liedermacher|theater|schauspieler|designer|poligra|film|ausstellungskoord|konzert|musik|polygra.*|regisseur|kulturschaff",
         "gärtner|eid.*. dipl.|coiffeu|automatiker|sanitär|elektrik|mechanik|mechatronik|schweisser|barkeeper|lüftungszeichner|speditionsmitarbeiter|verwaltungssekretär|flight|sicherheitsangestellt|reisebegl|schreiner|techniker|hauswart|re.*eptionist|drucktechnologe|drucker|speditionsarbeiter|bauer|angierarbeiter|fabrikant|fahrer|optiker|chauffeur|maler|landwirt|koch|chef de cuisine|konstrukteur|maschinist|lokführ|parkettleger|maurer|schiffsführ|köch|monteur|buchhändl|bad.*meister|postbote|briefträg|logistik|lokomotivführer|bahnangestellt",
         "journalis|autor|publiz|verleg|redaktor|verlagsmitarbeiter|übersetz|dolmetsch|lektor|PR-|redaktions|medienschaffend|schriftstell|PR Berater|marketing|public affairs|mediensprecher|kampagnenkoordinatorin|kommunikation",
         "^wirt|gastron",
         "therapeut|psycholog|psychoanalyt|coach|trainer|mediator|psychophysiognom",
         "finanz|finanzberat|immobilien|real.*estate|vermögensverwalt|vermögensverwalt|account manager|wirtschaftsprüfer|banking|steuerexpert",
         "analyst|datenspez",
         "pastor|pfarrer|sigrist|diakon",
         "personal|human ressources|personalleit")

cat <- c('Juristen', 
         'Lehrer', 
         'Ärzte',
         'wissenschaftliche Mitarbeiter',
         'Studierende_Auszubildende',
         'Rentner',
         'Ökonomen',
         'Unternehmer',
         'Informatiker',
         'Pflegeberufe',
         'Sozialarbeiter etc.',
         'Verkauf',
         'KV-Berufe',
         'Führungskräfte', 
         'Architektur und Bauwesen',
         'Buchhalter',
         'Familienfrauen',
         'Ingenieure',
         'Polizisten',
         'Kunstbranche',
         'Lehre_Handwerker',
         'Publizisten',
         'Gastronomen',
         'Therapeuten',
         'Finanzwesen_Finanzberater',
         'Analysten',
         'kirchliche Berufe',
         'Personalwesen')

nope <- c("student", 
          "nachhilfelehr|pensioniert|student|hochschullehr|sozialpäd", 
          "gehilf", 
          "studier|student|chemik.*fh|b. a.|mittelschullehrer",
          NA,
          NA,
          "student",
          NA,
          "studen",
          "schulpfleg|raumpfleg|denkmalpfleg|fusspfleg|kirchenpfleg|dozent",
          "sozialpsych|kindergärt|kindergart",
          "leiter",
          NA,
          "account manager|bauleiter|haushaltsleiter|chef de cuisine|kursleiter",
          NA,
          NA,
          NA,
          "studen|marketing",
          NA,
          NA,
          "kindergärtner|kunstmaler",
          "leiter|head",
          "wirtschaft",
          "pensioniert",
          "immobilienökonom",
          NA,
          NA,
          NA)

get_cats <- function(x){
  if(!x %in% c(1:4,7,9:12,14,18,21:25)) {
    tibble(case_n=grep(vec[x], 
                       unlist(lapply(strsplit(as.character(candodz$Beruf), ",|&|/|und "),'[[', 1)), #only take first nennung, not what comes after comma or stuff
                       ignore.case=T), 
           case_red=grep(vec[x], 
                         unlist(lapply(strsplit(as.character(candodz$Beruf), ",|&|/|und "),'[[', 1)), 
                         ignore.case=T, 
                         value=T),
           category=cat[x])} 
  
  else {
    
    tibble(case_n=intersect(grep(vec[x],unlist(lapply(strsplit(as.character(candodz$Beruf), ",|&|/|und "),'[[', 1)), ignore.case = T),
                            grep(nope[x],candodz$Beruf,ignore.case = T, invert=TRUE)), 
           case_red=unlist(lapply(strsplit(as.character(candodz$Beruf), ",|&|/|und "),'[[', 1))[intersect(grep(vec[x], unlist(lapply(strsplit(as.character(candodz$Beruf), ",|&|/|und "),'[[', 1)), ignore.case = T),
                                                                                                          grep(nope[x], candodz$Beruf, ignore.case = T, invert=TRUE))],
           category=cat[x])
  }
}

occupationCand<-lapply(1:length(vec), get_cats) %>%
  do.call(rbind, .)

remain<-candodz$Beruf[-occupationCand$case_n] #check if categorizable fields were categorized, possibly interate

# merge with dataframe by candidate for party information
partyCase_n<-data.frame(ListeKurzbez=candodz$ListeKurzbez[occupationCand$case_n], case_n=occupationCand$case_n)

merged<-merge(partyCase_n,occupationCand, by="case_n", all=F) %>%
  distinct(.)
table(merged$case_n) %>% sort()

# verify for particular case_n whether we got party-occupation-combination right
merged[which(merged$case_n==406),]
candodz[406,]

# calculate proportions by party
occupationCandParty<-merged %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  group_by(category, Partei) %>% 
  summarise(Anzahl=n()) %>%
  group_by(Partei) %>%
  mutate(Anteil=100*Anzahl/sum(Anzahl)) %>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP"))

# find most frequent profession categories per party for table
partyx<-"CVP"
occupationCandParty %>% 
  filter(Partei==partyx) %>%
  arrange(desc(Anteil))

# get proportions, for each party, of the 7 most frequent categories overall + sonstige=others
sonstige<-paste(cat[which(! (cat %in% c("Führungskräfte", "Juristen", "wissenschaftliche Mitarbeiter", "Lehre_Handwerker", "Lehrer", "KV-Berufe", "Unternehmer")))], collapse="|")

occupationCandParty_7<-merged %>%
  mutate(Partei = ListeKurzbez %>%
           as.character %>%
           gsub("Grüne", "GP", .) %>%
           gsub("glp", "GLP", .)) %>%
  mutate(category_red = category %>%
           gsub(sonstige, "sonstige",.)) %>% #get the 7 overall most frequent categories, as in the "wie repräsentativ sind die gemeinderaten für die bevölkerung"-piece
  group_by(category_red, Partei) %>% 
  summarise(Anzahl=n()) %>%
  group_by(Partei) %>%
  mutate(Anteil=round(100*Anzahl/sum(Anzahl), digits=1)) %>%
  filter(Partei %in% c("AL", "SP", "GP", "GLP", "CVP", "FDP", "SVP")) %>%
  select(category_red, Partei, Anteil) %>%
  spread(category_red, Anteil) %>%
  arrange(desc(`Führungskräfte`))%>%
  as.data.frame()

# verify
rowSums(occupationCandParty_7[,2:length(occupationCandParty_7)])

# adapt order of cols
occupationCandParty_7<-occupationCandParty_7[,c(1,2,3,9,5,6,4,8,7)]

# write
write.table(occupationCandParty_7, file="mypath/data/kandidaten/occupationCandParty_7.txt", row.names = F, sep="\t", quote=F)
