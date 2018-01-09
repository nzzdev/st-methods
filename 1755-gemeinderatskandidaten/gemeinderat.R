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
candsv<-read.csv("mypath/data/kandidaten/gr-kandidaten_zuerich_2018-01-08.csv", sep=";", header=T)
candsv<-candsv[,1:54] 

## population ##
bev<-read.csv("mypath/data//bevoelkerung/bev325od3250.csv", header=T) # most recent population data
vornbev<-read.csv("mypath/data/bevoelkerung/bev370od3701.csv", header=T) # most recent data on first names
berufbev<-read.csv("/Users/marie-jose/Documents/a_NZZ/projects/wahlenZH/gemenderatskandidaten/data/bevoelkerung/2590_Berufe_T4.csv", sep=";", header=F) # polling data on occupation

# define colors
vizCols <- c("#191d63", "#f9d545", "#a0a0a0", "#d66632", "#84bfc2","#dd5b6c","#58c4d5","#dcc940","#41b293","#a3a189","#d1abbc","#e75451")


#---------------------------------------------------------------------------------------------------------------------
### DATA PROCESSING ###

## sex
sexCand<-candsv %>%
  mutate(gender = gender %>%
           as.character %>%
           gsub("f", "Frauen", .) %>%
           gsub("m", "Männer", .)) %>%
  group_by(gender) %>%
  summarise("Anzahl"=n()) %>%
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>%
  arrange(desc(gender))%>%
  as.data.frame()
colnames(sexCand)<-c("Geschlecht", "Anzahl", "Anteil")

# verify
sum(sexCand$Anzahl) 
sum(sexCand$Anteil) 

# write
write.csv(sexCand, file="mypath/data/kandidaten/sexCand.csv", row.names=F)

# per kreis
sexCandKreis<-candsv %>%
  mutate(gender = gender %>%
           as.character %>%
           gsub("f", "Frauen", .) %>%
           gsub("m", "Männer", .)) %>%
  group_by(gender, district) %>%
  summarise("Anzahl"=n()) %>%
  group_by(district) %>%
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>%
  arrange(desc(Anteil))%>%
  as.data.frame()


## age
brk<-c(0,19,39,59,79,99,119)
candsv %>% 
  mutate("binned"=cut((2017-candsv$year_of_birth), brk)) -> candsv

candsv$binned %>% 
  gsub("\\(|\\]", "",.) %>% 
  gsub(",", "-",.) %>% 
  gsub("79-99|99-119", ">= 80",.) %>% 
  as.character -> candsv$binned

fd<-c("19-", "39-", "59-", "79-")
rpl<-c("20-", "40-", "60-", "80-")
for(i in seq_along(fd)) candsv$binned <- gsub(fd[i], rpl[i], candsv$binned, fixed = TRUE)

candsv[which(!is.na(candsv$binned)),] %>% 
  group_by(binned) %>% summarize("Anzahl"=n()) %>%  
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>% 
  as.data.frame() %>% 
  arrange(binned)-> ageCand

ageCand<-rbind(ageCand[2:nrow(ageCand),], ageCand[1,])
colnames(ageCand)<-c("Alter", "Anzahl", "Anteil")

# verify
sum(ageCand$Anteil)
sum(ageCand$Anzahl) #972 candidates, of which 4 NA re age

# write
write.csv(ageCand, file="mypath/data/kandidaten/ageCand.csv", row.names=F)

# per kreis
ageCandKreis<-
  candsv[which(!is.na(candsv$binned)),] %>% 
  group_by(binned, district) %>% 
  summarize("Anzahl"=n()) %>%  
  group_by(district) %>%
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>% 
  as.data.frame() %>% 
  arrange(district)
  

## first name
firstnameCand<-table(candsv$firstname) %>% 
  sort(., decreasing = T) %>% 
  as.data.frame() %>% 
  mutate("Anteil"=Freq/sum(Freq)) 
colnames(firstnameCand)<-c("Vorname", "Anzahl", "Anteil")
firstnameCand

# verify
sum(firstnameCand$Anzahl)
sum(firstnameCand$Anteil) 

#write
write.csv(firstnameCand, file="mypath/data/kandidaten/vornameCand.csv", row.names=F)


## district of residence

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

# are some districts better represented than others, according to this measure?
candsv_kreis %>% 
  group_by(district, wohntDa) %>% 
  summarise(counts=n()) %>% 
  group_by(district) %>% 
  mutate(perc=counts/sum(counts)) -> kreisCandExtrema
kreisCandExtrema %>% 
  filter(wohntDa=="nein") %>% 
  arrange(desc(perc))


## profession

#clean  datasheet
name.vec<-c() 
for(i in 1:length(berufbev)) name.vec[i]<-paste0(berufbev[11,i])
colnames(berufbev)<-name.vec

berufbev<-berufbev[- which(berufbev$`Beschreibung 1`=="" | berufbev$`Beschreibung 1`=="Beschreibung 1" | berufbev$`Anzahl Personen`=="()"),]
berufbev$`Anzahl Personen`<-gsub(" ", "", berufbev$`Anzahl Personen`)

# get overview
head(sort(table(candsv$occupation), decreasing=T),40)

#replace empty by NA
candsv$occupation<-gsub("^$", NA, candsv$occupation)

# categorize, maybe create additional column for this; we only use the first occupation for candidates that name several occupations / professions in order to avoid candidates to appear in several categories
vec <- c("juris|anwalt|anwält|gerichtsschreib|richter|lic..*iur.|MLaw", 
         "lehrer|heilpäd|katechet|kindergärt|pädagog|erwachsenenbildn|ausbildungsleit|krippenleit", # without lehrbeauftragte, see vector "nope" below
         "arzt|ärztin|Dr..*med.",
         "wiss.*mitarb|wissenschaft|forscher|professor|dozent|lehrbeauftr|doktorand|hochschullehr|historik|physik|soziolog|biolog|chemik|politolog|ökolog|geogra|naturwissenschaftler|theologe|zoolog|ethnolog|Japanologe|math..*eth|mathematik", # wissenschafter, wissenschaftliche mitarbeiter, dozenten but not studierende, see vector "nope" below
         "studier|student|auszubildende|in Ausbildung|i\\. a\\.|schüler|stud.", # without studienleiter, see vector "nope" below
         "rentn|pensioni|pensionä",
         "ökonom|betriebswirt|volkswirt|oekonom|consultant|unternehmensberater|lic.oec.|mag. oec.|lic..*oec.|dr. oec.|economist",
         "unterne.*mer|selbstst|selbst.|geschäftsinhaber|inhaber|entrepreneur|freischaffend|freelance",
         "informatik|it-|software|programmier|it engineer", 
         "pfleg|pfelg|pleg|krank|betagtenbetr|praxisass|zahnarztgehilf|gesundheits|hebamme|pharma-assistent|sanitäter|fachmann gesundheit",
         "sozialarb|sozialpäd|sozialdiak|sozialber|sozi.*arb|animator|Assistentin Mütter|familienberat|Jugendbeauftragte",
         "verkauf|verkäuf|detailhandel|sales",
         "kaufm|kauffrau|kfm|sachbearb|bankangest|bankfach|büroangest|postangeste|versicherungsmitarbei|versicherungsfach|kv-|gemeindeschreiber|^angestellter|pensionskassenexp|bezirksratsschreiberin",
         "geschäftsführ|geschäftsleiter|geschäftleiter|abteilungsleiter|projektleiter|schul.*leiter|direktor|teamleiter|verantwortliche|chef|head|leiter",
         "architek|raumplan|stadtplan|quartierentwick|bau.*leiter|bauführer|bauherr|verkehrsplan",
         "buchhalter",
         "hausfrau|familienfrau|hausmann|familienmanag",
         "ing\\.|ingenieu|dipl.*Ing",
         "poliz",
         "künstler|kunstmaler|kunst-|kunstexperte|produktgestalter|gra.*iker|liedermacher|theater|schauspieler|designer|poligra|film|ausstellungskoord|konzert|musik|polygra.*|regisseur|kulturschaff",
         "gärtner|eid.*. dipl.|coiffeu|automatiker|sanitär|elektrik|mechanik|mechatronik|flight|reisebegl|schreiner|techniker|hauswart|rezeptionist|drucktechnologe|drucker|speditionsarbeiter|bauer|angierarbeiter|fabrikant|fahrer|optiker|chauffeur|maler|landwirt|koch|chef de cuisine|konstrukteur|maschinist|lokführ|schiffsführ|köch|monteur|buchhändl|bademeister|postbote|briefträg|logistik|lokomotivführer|bahnangestellt",
         "journalis|autor|publiz|verleg|redaktor|übersetz|dolmetsch|lektor|PR-|redaktions|schriftstell|PR Berater|marketing|public affairs|mediensprecher|kampagnenkoordinatorin|kommunikation",
         "^wirt|gastron",
         "therapeut|psycholog|psychoanalyt|coach|trainer|mediator",
         "finanz|finanzberat|immobilien|real.*estate|vermögensverwalt|vermögensverwalt|account manager|wirtschaftsprüfer",
         "analyst|datenspez",
         "pastor|pfarrer|sigrist",
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
          "sozialpsych",
          "leiter",
          NA,
          "account manager|bauleiter|haushaltsleiter|chef de cuisine|kursleiter",
          NA,
          NA,
          NA,
          "studen",
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
                       unlist(lapply(strsplit(as.character(candsv$occupation), ",|&|/|und "),'[[', 1)), #only take first nennung, not what comes after comma or stuff
                       ignore.case=T), 
           case_red=grep(vec[x], 
                     unlist(lapply(strsplit(as.character(candsv$occupation), ",|&|/|und "),'[[', 1)), 
                         ignore.case=T, 
                         value=T),
           category=cat[x])} 
  
  else {
    
    tibble(case_n=intersect(grep(vec[x],unlist(lapply(strsplit(as.character(candsv$occupation), ",|&|/|und "),'[[', 1)), ignore.case = T),
                            grep(nope[x],candsv$occupation,ignore.case = T, invert=TRUE)), 
           case_red=unlist(lapply(strsplit(as.character(candsv$occupation), ",|&|/|und "),'[[', 1))[intersect(grep(vec[x], unlist(lapply(strsplit(as.character(candsv$occupation), ",|&|/|und "),'[[', 1)), ignore.case = T),
                                            grep(nope[x], candsv$occupation, ignore.case = T, invert=TRUE))],
           category=cat[x])
  }
}

occupationCand<-lapply(1:length(vec), get_cats) %>%
  do.call(rbind, .)

# write and verify categorization, possibly add or remove terms to/from the vectors above
write.csv(occupationCand, file="mypath/data/kandidaten/berufskategorienCand.csv", row.names=F)

nOccupationCand<- occupationCand %>%
  group_by(category) %>% 
  summarise(n()) %>%
  arrange(desc(`n()`))

print(nOccupationCand, n=30)
remain<-candsv$occupation[-occupationCand$case_n] #%>% table() %>% sort(decreasing=T)

# show the 7 largest groups and highlight students and retirees from the "other" category
occupationCand_show<-nOccupationCand[1:7,]

stud<-nrow(occupationCand %>% filter(category=="Studierende_Auszubildende"))
rent<-nrow(occupationCand %>% filter(category=="Rentner"))
sonstige<-nrow(candsv)-sum(as.numeric(occupationCand_show$`n()`))-stud-rent
studRent<-nOccupationCand$`n()`[which(nOccupationCand$category=="Studierende_Auszubildende")]+nOccupationCand$`n()`[which(nOccupationCand$category=="Rentner")]
studRentrow<-c("Studierende_Rentner",studRent)
sonstigeRow<-c("sonstige", sonstige)

occupationCand_show<-rbind(occupationCand_show,sonstigeRow, studRentrow)

occupationCand_show %>% 
  mutate(Anteil=as.numeric(`n()`)/sum(as.numeric(`n()`))) -> occupationCand_show
colnames(occupationCand_show)<-c("Beruf", "Anzahl", "Anteil")

#verify
sum(as.numeric(occupationCand_show$Anzahl))
sum(as.numeric(occupationCand_show$Anteil))

#write
write.csv(occupationCand_show, file="mypath/data/kandidaten/berufCand.csv", row.names=F)

berufCand_studierendeRentner<-nOccupationCand[c(13,19),]
berufCand_studierendeRentner %>% mutate(Anteil=as.numeric(`n()`)/sum(as.numeric(`n()`))) -> berufCand_studierendeRentner
colnames(berufCand_studierendeRentner)<-c("Funktion", "Anzahl", "Anteil")

write.csv(berufCand_studierendeRentner, file="mypath/data/kandidaten/berufCand_studierendeRentner.csv", row.names=F)




## population ##

# filter in order to get the most recent data | by January 2018, this would be September 2017
summary(filter(bev, StichtagDatJahr==2017)$StichtagDatMonat)
bev<-bev %>% filter(StichtagDatJahr==2017, StichtagDatMM==9)

## sex
bev %>% 
  group_by(SexLang) %>% 
  summarise("Anzahl"=sum(AnzBestWir)) %>% 
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>% 
  as.data.frame() -> sexPop

sexPop$SexLang %>% 
  as.character %>% 
  gsub("weiblich", "Frauen", .) %>% 
  gsub("männlich", "Männer", .) -> sexPop$SexLang

sexPop %>% 
  arrange(desc(SexLang)) -> sexPop
colnames(sexPop)<-c("Geschlecht", "Anzahl", "Anteil")

# verify
sum(sexPop$Anzahl) #verify, ok: 422153
sum(sexPop$Anteil) #1, ok

# write
write.csv(sexPop, file="/Users/marie-jose/Documents/a_NZZ/projects/wahlenZH/gemenderatskandidaten/data/bevoelkerung/sexPop.csv", row.names=F)

#per kreis:
sexPopKreis<-bev %>%
  group_by(SexLang, KreisCd) %>%
  summarise("Anzahl"=sum(AnzBestWir)) %>%
  group_by(KreisCd) %>%
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>%
  arrange(desc(KreisCd))%>%
  as.data.frame()
sum(sexPopKreis$Anzahl) #ok!


## age
bev %>% 
  group_by(AlterV20Kurz) %>% 
  summarise("Anzahl"=sum(AnzBestWir)) %>% 
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>% 
  as.data.frame() -> agePop

agePop$AlterV20Kurz %>% 
  as.character %>% 
  gsub("80 u. älter", ">= 80", .) -> agePop$AlterV20Kurz
colnames(agePop)<-c("Alter", "Anzahl", "Anteil")

# verify
sum(agePop$Anzahl)
sum(agePop$Anteil)

# write
write.csv(agePop, file="mypath/data/bevoelkerung/agePop.csv", row.names=F)

# per kreis
agePopKreis<-bev %>%
  group_by(AlterV20Kurz, KreisCd) %>%
  summarise("Anzahl"=sum(AnzBestWir)) %>%
  group_by(KreisCd) %>%
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>%
  arrange(desc(KreisCd))%>%
  as.data.frame()

# verify
sum(agePopKreis$Anzahl) 


## first names
vorn %>% 
  group_by(Vorname) %>% 
  summarise("Anzahl"=sum(AnzBestWir)) %>%  
  mutate("Anteil"=Anzahl/sum(Anzahl)) %>% 
  arrange(desc(Anzahl)) %>% 
  as.data.frame() -> vornamePop

# verify
sum(vornamePop$Anzahl) # ok, as those that have less than 10 counts are missing in the data
sum(vornamePop$Anteil)

# write
write.csv(vornamePop, file="mypath/data/bevoelkerung/vornamePop.csv", row.names=F)


## district 
bev %>% 
  group_by(KreisLang) %>% 
  summarise("Anzahl"=sum(AnzBestWir)) %>% 
  as.data.frame() -> kreisPop

# verify
sum(kreisPop$Anzahl)


## profession

# get overview
berufbev$`Beschreibung 4`

#categorize
vec <- c("juris|anwalt|anwält|gerichtsschreib|richter|lic..*iur.|MLaw", 
         "lehrer|heilpäd|katechet|kindergärt|pädagog|erwachsenenbildn|ausbildungsleit|krippenleit|lehrkräfte|kinderbetreuer", 
         "arzt|ärztin|ärzte|apotheker|Dr..*med.",
         "wiss.*mitarb|wissenschaft|akademische|forscher|professor|dozent|lehrbeauftr|doktorand|hochschullehr|historik|physik|soziolog|biolog|chemik|politolog|ökolog|geogra|naturwissenschaftler|theologe|zoolog|ethnolog|Japanologe|math..*eth|mathematik", 
         "studier|student|auszubildende|in Ausbildung|i\\. a\\.|schüler|stud.", 
         "rentn|pensioni|pensionä",
         "ökonom|betriebswirt|volkswirt|oekonom|consultant|unternehmensberater|lic.oec.|mag. oec.|lic..*oec.|dr. oec.|economist",
         "unterne.*mer|selbstst|selbst.|geschäftsinhaber|inhaber|entrepreneur|freischaffend|freelance",
         "informatik|it-|software|programmier|it engineer|multimediaentwickler|systemanalytiker", 
         "pfleg|pfelg|pleg|krank|betagtenbetr|praxisass|pharmazeutisch-technische ass|medizin.*ass|medizin|zahnarztgehilf|gesundheits|hebamme|pharma-assistent|sanitäter|fachmann gesundheit|physikotechn",
         "sozialarb|sozialpäd|sozialdiak|sozialber|sozialpfleg|sozi.*arb|animator|Assistentin Mütter|familienberat|Jugendbeauftragte",
         "verkauf|verkäuf|detailhandel|sales|einkäufer|vertrieb",
         "kaufm|kauffrau|kfm|sachbearb|bankangest|bankfach|büroangest|bürokräfte|rechts- und verwandte|schalterbedienstete|reiseverkehrsfachkräfte|telefonisten|empfangskräfte|sekretariat|postangeste|versicherungsvertr|versicherungsmitarbei|versicherungsfach|kv-|gemeindeschreiber|^angestellter|pensionskassenexp|bezirksratsschreiberin",
         "geschäftsführ|geschäftsleiter|leitende|geschäftleiter|abteilungsleiter|projektleiter|schul.*leiter|direktor|teamleiter|verantwortliche|chef|head|leiter|führungskr",
         "architek|raumplan|stadtplan|quartierentwick|bau.*leiter|bauführer|bauherr|verkehrsplan",
         "buchhalter|rechnungswesen",
         "hausfrau|familienfrau|hausmann|familienmanag",
         "ing\\.|ingenieu|dipl.*Ing",
         "poliz",
         "künstler|kunstmaler|kunst-|kunstexperte|produktgestalter|raumgestalter|gestaltung|fotografen|gra.*iker|liedermacher|theater|schauspieler|designer|poligra|film|ausstellungskoord|konzert|musik|polygra.*|regisseur|kulturschaff",
         "maurer|zimmerleute|fliesenleger|stuckateure|isolierer|schornsteinfeger|schutzkräfte|schneider|reisebegleiter|friseure|barkeeper|kosmetiker|druckhandw|bäcker|bekleidungsherstellung|bediener|hauswirtschafter|fleischer|tischler|montageberufe|fahrzeugführer|hilfsarbeit|boten|gärtner|reinigungs|sicherheitswach|eid.*. dipl.|technische zeichner|coiffeu|automatiker|sanitär|elektrik|mechanik|mechatronik|schreiner|techniker|postverteiler|lagerwirtschaft|kellner|hauswart|rezeptionist|drucktechnologe|drucker|küchenchef|speditionsarbeiter|bauer|angierarbeiter|fabrikant|fahrer|optiker|chauffeur|maler|landwirt|koch|chef de cuisine|konstrukteur|maschinist|lokführ|schiffsführ|köch|monteur|buchhändl|bademeister|postbote|briefträg|logistik|lokomotivführer|bahnangestellt",
         "journalis|autor|publiz|verleg|redaktor|übersetz|dolmetsch|lektor|PR-|redaktions|schriftstell|PR Berater|marketing|public affairs|mediensprecher|kampagnenkoordinatorin|kommunikation|veranstaltungsplaner|öffentlichkeitsarbeit",
         "^wirt|gastron",
         "therapeut|psycholog|psychoanalyt|coach|trainer|mediator",
         "finanz|finanzberat|immobilien|makler|real.*estate|vermögensverwalt|vermögensverwalt|account manager|wirtschaftsprüfer",
         "analyst|datenspez",
         "pastor|pfarrer|sigrist|geistliche",
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
         'Führungskräfte', #ALEX EVT WEGLASSEN
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
          "studier|student|chemik.*fh|b. a.|nicht akademische|krankenpflege|ingenieur|medizin|gesundheitsberufe|betriebswirt|finanzen|personalfachleute|marketing|öffentlichkeitsarbeit|techniker|kommunikationstechn",
          NA,
          NA,
          "nicht akademische",
          NA,
          "studen",
          "schulpfleg|raumpfleg|denkmalpfleg|fusspfleg|kirchenpfleg|führungskräfte|sekretariat|sozialpfleg",
          "sozialpsych",
          "führungskräfte",
          "führungskräfte|sekretariatsleiter",
          "account manager|bauleiter|haushaltsleiter|chef de cuisine|kursleiter|küchenchef|begleiter",
          NA,
          NA,
          NA,
          "studen|architek",
          NA,
          "Architekten",
          "kindergärtner|kunstmaler|führungskräfte|physikotechniker|medizintechn|physiotherapeut",
          "führungskräfte|ingenieurwissenschaftler|techniker",
          "wirtschaft",
          "pensioniert|sportlehrer",
          "immobilienökonom|führungskräfte|bürokräfte",
          "finanzanalysten",
          "führungskräfte|bürokräfte|reinigungspersonal|sicherheitswachpersonal",
          "reinigungs|sicherheits|führungskräfte|bürokräfte")

get_cats_pop <- function(x){
  if(!x %in% c(1:4,7,9:14,18,20:28)) {
    tibble(case_n=grep(vec[x], 
                       berufbev$`Beschreibung 4`, 
                       ignore.case=T),
           #counts_grep(vec[])
           case=grep(vec[x], 
                     berufbev$`Beschreibung 4`, 
                     ignore.case=T, 
                     value=T),
           category=cat[x])} 
  
  else {
    
    tibble(case_n=intersect(grep(vec[x],berufbev$`Beschreibung 4`, ignore.case = T),
                            grep(nope[x],berufbev$`Beschreibung 4`,ignore.case = T, invert=TRUE)), 
           case=berufbev$`Beschreibung 4`[intersect(grep(vec[x], berufbev$`Beschreibung 4`, ignore.case = T),
                                            grep(nope[x], berufbev$`Beschreibung 4`, ignore.case = T, invert=TRUE))],
           category=cat[x])
  }
}

occupationPop<-lapply(1:length(vec), get_cats_pop) %>%
  do.call(rbind, .)

# write and verify categorization, possibly add or remove terms to/from the vectors above
write.csv(occupationPop, file="mypath/data/bevoelkerung/berufskategorienPop.csv", row.names=F)
nOccupationPop<- occupationPop %>%
  group_by(category) %>%
  summarise(n()) %>%
  arrange(desc(`n()`))
print(nOccupationPop, n=30)

# verify
sum(nOccupationPop$`n()`)
remain<-berufbev$`Beschreibung 4`[-occupationPop$case_n] #%>% table() %>% sort(decreasing=T)

#get real counts of each category
berufbev_cts<-merge(occupationPop, berufbev, by.x="case", by.y="Beschreibung 4", all.x=T)
berufbev_cts<-berufbev_cts[,-c(4:8)]

berufbev_agg<-berufbev_cts %>% group_by(category) %>% summarise(Anzahl = sum(as.numeric(`Anzahl Personen`))) %>% mutate(Anteil=Anzahl/sum(as.numeric(berufbev$`Anzahl Personen`))) %>% arrange(desc(Anzahl))
print(berufbev_agg, n=25)

total<-sum(as.numeric(berufbev$`Anzahl Personen`))

# show the 7 largest groups and juristen
occupationPop_show<-berufbev_agg[c(1:7,16),]

sonstige<-total-sum(as.numeric(occupationPop_show$Anzahl))
sonstigePerc<-sonstige/total
sonstigeRow<-c("sonstige", 66820, 0.3315142)
occupationPop_show<-rbind(occupationPop_show,sonstigeRow)
colnames(occupationPop_show)<-c("Beruf", "Anzahl", "Anteil")

# verify
sum(as.numeric(occupationPop_show$Anzahl)) 
sum(as.numeric(occupationPop_show$Anteil))

# rearrange, cf. candidates: führungskräfte, jurstien, wissensch, lehre, lehrer, kv, unternehmer, sonstige
occupationPop_show<-occupationPop_show[c(2,8,4,1,5,3,7,9),]

# write
write.csv(occupationPop_show, file="mypath/data/bevoelkerung/berufPop.csv", row.names=F)


#---------------------------------------------------------------------------------------------------------------------
### FIRST VISUALIZATIONS

## sex
colors<-vizCols[1:2]

# population
sexPopVector<-structure(sexPop[,2], names=as.character(sexPop[,1])) # the waffleplot library wants a weird data format. sorry.

divisor<-50
sexPopVector<-round(sexPopVector/divisor)
key<-paste0("1 Quadrat = ", divisor, " Personen")

title<-"mytitle"
source <- "Statistik Stadt Zürich"

nrows<-40 
spacebetween<-.3 

waffle(sexPopVector, rows=nrows, size=spacebetween, colors=colors,
       xlab=key, flip=F)+
  labs(title = title,
       caption = paste0("Source: ", source))

# candidates
sexCandVector<-structure(sexCand[,2], names=as.character(sexCand[,1])) %>% sort() # the waffleplot library wants a weird data format. sorry.

divisor<-1
sexCandVector<-round(sexCandVector/divisor) 
key<-paste0("1 Quadrat = ", divisor, " Personen")

title<-"mytitle"
source <- "Statistik Stadt Zürich"

waffle(sexCandVector, rows=nrows, size=spacebetween, colors=colors,
               xlab=key, flip=F)+
  labs(title = title,
       caption = paste0("Source: ", source))

## age
colors<-vizCols[1:5] # define numer of cols 

# population
agePopVector<-structure(agePop[,2], names=as.character(agePop[,1])) # the waffleplot library wants a weird data format. sorry.
agePopVector

divisor<-50
agePopVector<-round(agePopVector/divisor) 
key<-paste0("1 Quadrat = ", divisor, " Personen")

title<-"mytitle"
source <- "Statistik Stadt Zürich"

nrows<-40 
spacebetween<-.5 

waffle(agePopVector, rows=nrows, size=spacebetween, colors=colors,
       xlab=key, flip=F)+
  labs(title = title,
       caption = paste0("Source: ", source))
filename<-paste0("agePop",".","svg") # adapt to either .svg or .pdf
ggsave(filename, height=6)

# candidates
ageCandVector<-structure(ageCand[,2], names=as.character(ageCand[,1])) # the waffleplot library wants a weird data format. sorry.

divisor<-1
ageCandVector<-round(ageCandVector/divisor) # careful: when numeric values in dataVector_final are not integers, we get a third, useless level in the graph
key<-paste0("1 Quadrat = ", divisor, " Person")

colors<-vizCols[2:5]

title<-"mytitle"
source <- "Statistik Stadt Zürich"

waffle(ageCandVector, rows=nrows, size=spacebetween, colors=colors,
       xlab=key, flip=F)+
  labs(title = title,
       caption = paste0("Source: ", source))



#----------------------------------------------------------------------------------------------------------------------------------------------------------
### PROTOTYPICAL CANDIDATE

# mean and median age
medianage<-median(2017-candsv$year_of_birth[which(!is.na(candsv$year_of_birth))]) #46 jahre
medianageCand<-candsv[which(2017-candsv$year_of_birth==medianage),]

# of those, males
medianagegenderCand<-medianageCand %>% filter(gender=="m")

# of those, führungskräfte
find<-"geschäftsführ|geschäftsleiter|leitende|geschäftleiter|abteilungsleiter|projektleiter|schul.*leiter|direktor|teamleiter|verantwortliche|chef|head|leiter|führungskr"
nope<-"account manager|bauleiter|haushaltsleiter|chef de cuisine|kursleiter|küchenchef|begleiter"

fuehrungskraefte<-intersect(grep(find,as.character(medianagegenderCand$occupation), ignore.case = T),
                            grep(nope,as.character(medianagegenderCand$occupation),ignore.case = T, invert=TRUE))
           
medianagegenderoccupation<-medianagegenderCand[fuehrungskraefte,]

# those who live in the same district
medianagegenderoccupationzip<-merge(medianagegenderoccupation,candsv_kreis, by.x="ID_Candidate", by.y="ID_Candidate", all.x=T)

# break tie with first name - Thomas is the most frequent first name in the candidate-dataset



#----------------------------------------------------------------------------------------------------------------------------------------------------------
### MOST REPRESENTATIVE CANDIDATE

#age, gender
modeagegender<-filter(candsv, candsv$year_of_birth %in% 1978:1997 & gender=="f")

# those who live in the district: none
modeagegenderzip<-merge(modeagegender,candsv_kreis, by.x="ID_Candidate", by.y="ID_Candidate", all.x=T)
grep("Bettina", modeagegenderzip$firstname, ignore.case=T)

# profession
find<-"gärtner|eid.*. dipl.|coiffeu|automatiker|sanitär|elektrik|mechanik|mechatronik|flight|reisebegl|schreiner|techniker|hauswart|rezeptionist|drucktechnologe|drucker|speditionsarbeiter|bauer|angierarbeiter|fabrikant|fahrer|optiker|chauffeur|maler|landwirt|koch|chef de cuisine|konstrukteur|maschinist|lokführ|schiffsführ|köch|monteur|buchhändl|bademeister|postbote|briefträg|logistik|lokomotivführer|bahnangestellt"
nope<-"kindergärtner|kunstmaler"

lehre_handwerker<-intersect(grep(find,as.character(modeagegender$occupation), ignore.case = T),
                            grep(nope,as.character(modeagegender$occupation),ignore.case = T, invert=TRUE))

modeagegenderoccupation<-modeagegender[lehre_handwerker,] 



#----------------------------------------------------------------------------------------------------------------------------------------------------------
### YOUNGEST AND OLDEST CANDIDATE | MOST AND LEAST REPRESENTATIVE DISTRICT

### youngest and oldest
highestYear<-max(candsv$year_of_birth[which(!is.na(candsv$year_of_birth))])
candsv[which(candsv$year_of_birth==highestYear),] # two phonecalls broke the tie

lowestYear<-min(candsv$year_of_birth[which(!is.na(candsv$year_of_birth))]) 
candsv[which(candsv$year_of_birth==lowestYear),] 


### by kreis: the most and the least representative

# gender
sexPopKreis1_2<-sexPopKreis %>% 
  filter(KreisCd=="1" | KreisCd=="2") %>% 
  group_by(SexLang) %>% 
  summarise(Anzahl=sum(Anzahl)) %>% 
  mutate(AnteilPop=Anzahl/sum(Anzahl)) %>% 
  mutate(district="1+2")
sexPopKreis4_5<-sexPopKreis %>% 
  filter(KreisCd=="4" | KreisCd=="5") %>% 
  group_by(SexLang) %>% 
  summarise(Anzahl=sum(Anzahl)) %>% 
  mutate(AnteilPop=Anzahl/sum(Anzahl)) %>% 
  mutate(district="4+5")
sexPopKreis7_8<-sexPopKreis %>% 
  filter(KreisCd=="7" | KreisCd=="8") %>% 
  group_by(SexLang) %>% 
  summarise(Anzahl=sum(Anzahl)) %>% 
  mutate(AnteilPop=Anzahl/sum(Anzahl)) %>% 
  mutate(district="7+8")
sexPopKreis_rest<-sexPopKreis %>% 
  filter(!(KreisCd %in% c(1,2,4,5,7,8)))
sexPopKreis_rest<-sexPopKreis_rest[,c(1,3,4,2)]
colnames(sexPopKreis_rest)[3:4]<-c("AnteilPop", "district")

sexPopKreis_final<-rbind(sexPopKreis1_2,
                         sexPopKreis4_5,
                         sexPopKreis7_8,
                         sexPopKreis_rest)

sexCandKreis$district<-unlist(lapply(strsplit(as.character(sexCandKreis$district), "kreis "), '[[',2))

sexPopKreis_m<-sexPopKreis_final %>% filter(SexLang=="männlich")
sexCandKreis_m<-sexCandKreis %>% filter(gender=="Männer")

mergedSex<-merge(sexPopKreis_m, sexCandKreis_m, by="district") %>% mutate(diff=Anteil-AnteilPop) %>% arrange(desc(diff))

sexPopExtrema<-sexPopKreis_final %>% 
  filter(district %in% c("4+5", "12")) %>% 
  mutate(Gruppe="Bevölkerung")
sexCandExtrema<-sexCandKreis %>% 
  filter(district %in% c("4+5", "12")) %>% mutate(Gruppe="Kandidaten")

# write
write.csv(sexPopExtrema, file="mypath/data/bevoelkerung/sexPopExtrema.csv", row.names=F)
write.csv(sexCandExtrema, file="mypath/data/bevoelkerung/sexCandExtrema.csv", row.names=F)


# age
agePopKreis1_2<-agePopKreis %>% 
  filter(KreisCd=="1" | KreisCd=="2") %>% 
  group_by(AlterV20Kurz) %>% 
  summarise(Anzahl=sum(Anzahl)) %>% 
  mutate(AnteilPop=Anzahl/sum(Anzahl)) %>% 
  mutate(district="1+2")
agePopKreis4_5<-agePopKreis %>% 
  filter(KreisCd=="4" | KreisCd=="5") %>% 
  group_by(AlterV20Kurz) %>% 
  summarise(Anzahl=sum(Anzahl)) %>% 
  mutate(AnteilPop=Anzahl/sum(Anzahl)) %>% 
  mutate(district="4+5")
agePopKreis7_8<-agePopKreis %>% 
  filter(KreisCd=="7" | KreisCd=="8") %>% 
  group_by(AlterV20Kurz) %>% 
  summarise(Anzahl=sum(Anzahl)) %>% 
  mutate(AnteilPop=Anzahl/sum(Anzahl)) %>% 
  mutate(district="7+8")
agePopKreis_rest<-agePopKreis %>% 
  filter(!(KreisCd %in% c(1,2,4,5,7,8)))
agePopKreis_rest<-agePopKreis_rest[,c(1,3,4,2)]
colnames(agePopKreis_rest)[3:4]<-c("AnteilPop", "district")

agePopKreis_final<-rbind(agePopKreis1_2,
                         agePopKreis4_5,
                         agePopKreis7_8,
                         agePopKreis_rest)

ageCandKreis$district<-unlist(lapply(strsplit(as.character(ageCandKreis$district), "kreis "), '[[',2))

agePopKreis_019<-agePopKreis_final %>% 
  filter(AlterV20Kurz=="0-19")
ageCandKreis_019<-ageCandKreis %>% 
  filter(binned=="0-19")

merged019<-merge(agePopKreis_019, ageCandKreis_019, by="district") %>% 
  mutate(diff=Anteil-AnteilPop) %>% 
  arrange(desc(diff))

agePopKreis_2039<-agePopKreis_final %>% filter(AlterV20Kurz=="20-39")
ageCandKreis_2039<-ageCandKreis %>% filter(binned=="20-39")

merged2039<-merge(agePopKreis_2039, ageCandKreis_2039, by="district") %>% 
  mutate(diff=Anteil-AnteilPop) %>% 
  arrange(desc(diff))

agePopKreis_4059<-agePopKreis_final %>% filter(AlterV20Kurz=="40-59")
ageCandKreis_4059<-ageCandKreis %>% filter(binned=="40-59")

merged4059<-merge(agePopKreis_4059, ageCandKreis_4059, by="district") %>% 
  mutate(diff=Anteil-AnteilPop) %>% 
  arrange(desc(diff))

agePopKreis_6079<-agePopKreis_final %>% filter(AlterV20Kurz=="60-79")
ageCandKreis_6079<-ageCandKreis %>% filter(binned=="60-79")

merged6079<-merge(agePopKreis_6079, ageCandKreis_6079, by="district") %>% 
  mutate(diff=Anteil-AnteilPop) %>% 
  arrange(desc(diff))

agePopKreis_80<-agePopKreis_final %>% filter(AlterV20Kurz=="80 u. älter")
ageCandKreis_80<-ageCandKreis %>% filter(binned==">= 80")

merged80<-merge(agePopKreis_80, ageCandKreis_80, by="district") %>% 
  mutate(diff=Anteil-AnteilPop) %>% 
  arrange(desc(diff))

mergedage<-rbind(merged019,
merged2039,
merged4059,
merged6079,
merged80)

mergedage %>% arrange(desc(abs(diff))) 
mergedage %>% group_by(district) %>% summarise("Anzahl"=sum(abs(diff))) 

mergedage %>% filter(district %in% c("1+2", "9"))

agePopExtrema<-agePopKreis_final %>% filter(district %in% c("1+2", "9")) %>% mutate(Gruppe="Bevölkerung")
ageCandExtrema<-ageCandKreis %>% filter(district %in% c("1+2", "9")) %>% mutate(Gruppe="Kandidaten")

#write
write.csv(agePopExtrema, file="mypath/data/bevoelkerung/agePopExtrema.csv", row.names=F)
write.csv(ageCandExtrema, file="mypath/data/bevoelkerung/ageCandExtrema.csv", row.names=F)

