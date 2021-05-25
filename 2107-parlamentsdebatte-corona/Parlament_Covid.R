### Script für Textanalyse Corona/Covid Schweizer Parlament ### 
### 15/04/2021 ###

# prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
# set working directory with setwd("")

# Install packages
install.packages("tidyverse", "magrittr", "stringr", "lubridate", "readxl", "tidytext", "tm")
install.packages("magrittr")
install.packages("swissparl") # API Schnittstelle CH-Parlament
library(swissparl) 
library(tidyverse)
library(quanteda)
library(stringr)
library(lubridate)
library(magrittr)
library(readxl)
library(tidytext)
library(tm)
# package swissparl explained https://cran.r-project.org/web/packages/swissparl/swissparl.pdf 

### Swissparl: See all possible Files and variables: get_tables(), get_variables()
get_tables()
get_variables(table = "Transcript")
get_variables(table = "Business")

### Prep: Retrieve 7 Session-Ids since 31.12.2019
sessions <- get_data(
  table = "Session",
  Language = "DE",
  StartDate = ">2019-12-31"
)
sessions

### Retrieve all Transcripts since 2020
## MeetingCouncilAbbreveation: N = Nationalrat, S = Ständerat, V = Vereinigte Bundesversammlung

transcripts <- get_data(
  table = "Transcript",
  Language = "DE",
  Type = 1, # Abstimmungseinträge rausfiltern
  IdSession = as.character(sessions$ID) # Otherwise formats do not match
)
length(transcripts$Text)
# 14404 Texts


#############################
###  Create Text Doc. All ###
#############################

### Create df text_all: Alle Wortmeldungen seit 2020
text_all <- transcripts %>%
  mutate(tidyText = clean_text(Text, keep_round_brackets = F))
head(text_all)
#replace party fraction names with shorter names
text_all$ParlGroupName[text_all$ParlGroupName == "Fraktion der Schweizerischen Volkspartei"] <- "SVP Fraktion"
text_all$ParlGroupName[text_all$ParlGroupName == "FDP-Liberale Fraktion"] <- "FDP Fraktion"
text_all$ParlGroupName[text_all$ParlGroupName == "Die Mitte-Fraktion. CVP-EVP-BDP."] <- "CVP-EVP-BDP Fraktion"
text_all$ParlGroupName[text_all$ParlGroupName == "Sozialdemokratische Fraktion"] <- "SP Fraktion"

# Get rid of all transcripts that come from Council Presidents, Vice-Presidents and Bundesraete and then clean the texts
# P are "RatspräsidentInnen", VP are "Stellvertreter"
# We only want to look at Nationalrät:Innen, Staenderaet:Innen

text_all %<>%
  filter(!SpeakerLastName == "leer") %>% 
  filter(!SpeakerFunction %in% c("1VP-F", "1VP-M", "2VP-F", "2VP-M", "AP-M", "P-F", "P-M")) %>% 
  filter(!Function %in% c("1VP-M", "2VP-M", "P-F", "p-m", "P-m", "P-M", "P-MM")) %>%
  filter(!CouncilName == "Bundesrat") %>%
  filter(!SpeakerFullName == "Thurnherr Walter")

length(text_all$tidyText)
# 8097 ohne BR / 10190 Wortmeldungen mit BR

# format MeetingDate
text_all$MeetingDate <- as_date(text_all$MeetingDate, tz = NULL, format = NULL)

# when were most texts
hist_dates <- text_all %>% 
  group_by(MeetingDate) %>% 
  summarise(frequency = n())
hist(text_all$MeetingDate, "days", freq = TRUE)

# Select only columns needed
text_all %<>%
  select(ID, IdSubject, VoteId, VoteBusinessNumber, VoteBusinessShortNumber, 
         VoteBusinessTitle, LanguageOfText, tidyText, MeetingCouncilAbbreviation, MeetingDate, 
         SpeakerLastName, SpeakerFirstName, SpeakerFullName, ParlGroupName, CouncilName)
head(text_all)

## Make stopwords lists
# automatic stop word list
stopwords("de")
stopwords("it")[1:150]
stopwords("fr")[1:150]

# make an additional stopword list manually 
# typical words n parliament, that do not add to conten:
# Minderheit, Mehrheit, Vorlage, Motion, Absatz, Artikel, Kommission etc.
mystopwords <- c("für", "dass", "letzte", "letzt", "letzter", "letztes", "vorletzte", "ausserdem", "bereits", 
                 "erster", "zweiter", "dritter", "erste", "zweite", "dritte", "erstens", "zweitens", "drittens", "grundsätzlich",
                 "soeben", "nebst", "neben", "kurz" , "immer" , "selten" , "nie" , "manchmal" , "oft" , "zwischendurch" , "seitdem", "erst",
                 "ja", "z.B.", "der", "die", "das", "ab", "deshalb", "dafür", "heute", "sofort", "danach", "schon", "bald", "haben", "hat", "habt", "hatten",
                 "wäre", "viele", "vieles", "vielen", "vielem", "einfach", "so", "davon", "vielleicht", "weil", "aufgrund", "gerade", "wurden", "gegen", "wider",
                 "wurde", "wurdest", "deshalb", "dafür", "darum", "dagegen", "selbst", "selber", "weitere", "weiteres", "weiterer", "ganz", "eben", "direkt", 
                 "notre", "avons", "avez", "ont", "la", "le", "de", "I", "dovra", "Conseil", "fédéral", "Bundesrat", "Bundesrates", "Bundesräte", "confédération",
                 "Nationalrat", "Ständerat", "für", "dass", "commission", "Kommission", "letzte", "letzt", "letzter", "letztes", "vorletzte", "Minderheit", "Mehrheit",
                  "Vorlage", "Motion", "Artikel", "Absatz", "soeben", "nebst", "neben", "gleich", "ja", "nein", "z.B.", "seit", "rund", "klar", "Prozent",
                 "ausserdem", "bereits", "Antrag", "wirklich", "auch", "ebenfalls", "der", "die", "das", "ab", "deshalb", "dafür", "heute", "sofort", 
                 "daher", "natürlich", "insbesondere", "zudem", "darauf", "nämlich", "dabei","eigentlich", "schon", "sowie", "gemäss", "gleichzeitig", 
                 "Beispiel", "beim", "letzten","worden","insgesamt", "deshalb", "dafür", "darum", "dagegen", "selbst", "selber", "weitere",    "weiteres",
                 "weiterer", "ganz", "entsprechend", "entsprechendes","entsprechender", "notre", "avons", "avez", "ont", "domain", "certain", "majorité", "minorité", 
                "la", "le", "de", "I", "dovra", "donc", "c'est","plus", "puisque", "pendant", "ni", "fair", "fait", "être", "tout", "tous", "toutes", "toute",
                "aussi", "enfaite", "souvent", "aujourd'hui", "en effet", "lorsque", "donc", "l'article", "n'est", "c'est", "elle", "elles", "contre","cent",
                 "ussa", "nostro", "c'è", "che", "per", "a", "e", "di", "perche", "z.B", "ein", "zwei", "drei", "vier", "unserer", "unsere", "unser","déjà",
                 "b", "z", "i", "ii", "d'un", "d'autre", "1a", "1", "2", "3", "4", "h", "a", "cas", "mais", "un", "deux", "trois", "quatre", "cinq", "faut",
                 "d'une", "sagen", "gesagt", "très", "sehr", "herr", "frau", "monsieur", "madame", "également", "comme", "évidemment", "déjà", "l'on",
                 "où", "soutien", "concernant", "oui", "non", "si", "qu'il", "qu'elle", "qu'ils", "qu'elles", "encore", "ainsi", "entre", "lors", "dont", 
                 "2019", "2020", "2021", "demande", "question", "pour", "cent")


############################
###  Create Large Corpus ##
###########################

# Tokens: totale Wortzahl in einem Text oder Corpus, inkl. Wiederholungen
# Texte sind 520 bis 1048 Wörter lang (mit Wh.)
# Types: Zahl unterschiedlicher Worte in einem Text oder Corpus (zeigt wie vielfältig die Wortwahl ist)

parl_corpus_all <- corpus(
  text_all$tidyText,
  docnames = text_all$ID,
  docvars = text_all %>% 
    select(-tidyText))
summary(parl_corpus_all)

parl_toks_all <- tokens(parl_corpus_all, remove_number=T, remove_punct=T)
# Corpus consists of 8097 documents (Wortmeldungen pro Person)

# remove stopwords from corpus
parl_corpus_all_final <- parl_toks_all %>%
  tokens_remove(stopwords('de')) %>%
  tokens_remove(stopwords('fr')) %>%
  tokens_remove(stopwords('it')) %>%
  tokens_remove(mystopwords)

## Look at words in their context
kwic(parl_corpus_all_final, phrase("Spital")) %>% head()
kwic(parl_corpus_all_final, phrase("Gesundheit")) %>% head()
kwic(parl_corpus_all_final, phrase("Kurzarbeit")) %>% head()
kwic(parl_corpus_all_final, phrase("loi")) %>% head()

# Create final document feature matrix parl_all_dfm
parl_all_dfm <- dfm(parl_corpus_all_final)
head(parl_all_dfm)

# Wordcloud
set.seed(132)
textplot_wordcloud(parl_all_dfm, max_words = 100)

#stemming
parl_all_dfm <- dfm_wordstem(parl_all_dfm, language = "german")
parl_all_dfm <- dfm_wordstem(parl_all_dfm, language = "french")
parl_all_dfm <- dfm_wordstem(parl_all_dfm, language = "italian")

# What did they talk about? Get absolute frequency of all words
#create dataframe text_freq_all.csv 
parl_all_freq <- textstat_frequency(parl_all_dfm, n=1000)
parl_all_freq50 <- textstat_frequency(parl_all_dfm, n=60)
parl_all_freq50

# Sort by frequency order
parl_all_freq50 %<>% 
  arrange(desc(frequency))
parl_all_freq50
plot_freq50_all <- ggplot(data=parl_all_freq50, aes(x=reorder(feature, frequency), y=frequency)) +
  coord_flip() +
  geom_bar(stat="identity", fill='steelblue') + 
  labs(title="Häufigste Worte insgesamt", 
       subtitle = "Worthäufigkeit bei allen Reden",
       y = "Häufigkeit", x = "") 
# with ggsave("") save somewhere
plot_freq50_all


##############################
###  Create Text Doc. Covid ##
##############################

### Search through all Transcripts that include "Covid", "Corona", etc. in tidyText
### Create df text_covid

text_covid <- transcripts %>%
  filter(str_detect(tolower(Text), "corona|covid|sars|coronavirus")) %>%
  mutate(tidyText = clean_text(Text, keep_round_brackets = F))
length(text_covid$tidyText)
# 2203 Text Documents overall (with BR)
# write_csv(text_covid, "") # save somewhere

head(text_covid$tidyText)
# including deutsch, ital., franz.

#replace party fraction names with shorter names
unique(text_covid$ParlGroupName)
text_covid$ParlGroupName[text_covid$ParlGroupName == "Fraktion der Schweizerischen Volkspartei"] <- "SVP Fraktion"
text_covid$ParlGroupName[text_covid$ParlGroupName == "FDP-Liberale Fraktion"] <- "FDP Fraktion"
text_covid$ParlGroupName[text_covid$ParlGroupName == "Die Mitte-Fraktion. CVP-EVP-BDP."] <- "CVP-EVP-BDP Fraktion"
text_covid$ParlGroupName[text_covid$ParlGroupName == "Sozialdemokratische Fraktion"] <- "SP Fraktion"

# Again, get rid of all transcripts that come from Council Presidents and Vice-Presidents and Bunderaeten
text_covid %<>%
  filter(!SpeakerLastName == "leer") %>% 
  filter(!SpeakerFunction %in% c("1VP-F", "1VP-M", "2VP-F", "2VP-M", "AP-M", "P-F", "P-M")) %>% 
  filter(!Function %in% c("1VP-M", "2VP-M", "P-F", "p-m", "P-m", "P-M", "P-MM")) %>%
  filter(!CouncilName == "Bundesrat") %>%
  filter(!SpeakerFullName == "Thurnherr Walter")

length(text_covid$tidyText)
# 1546 Texts
# (1100 Texts mit Lang. of Text German (71%))
# format MeetingDate
text_covid$MeetingDate <- as_date(text_covid$MeetingDate, tz = NULL, format = NULL)
head(text_covid$MeetingDate)
hist(text_covid$MeetingDate, "days", freq = TRUE)

# Select only columns needed, make lowercase 
text_covid %<>%
  select(ID, IdSubject, VoteId, VoteBusinessNumber, VoteBusinessShortNumber, LanguageOfText, VoteBusinessTitle, tidyText, MeetingCouncilAbbreviation, MeetingDate, 
         SpeakerLastName, SpeakerFirstName, SpeakerFullName, ParlGroupName, CouncilName) %>%
  mutate(tidyText = tolower(tidyText))
head(text_covid)

# write_csv(text_covid, "") # save final document


##################################
###  Create Large Corpus Covid  ##
#################################

# Create Corpus with all languages 

parl_corpus <- corpus(
  text_covid$tidyText,
  docnames = text_covid$ID,
  docvars = text_covid %>% 
    select(-tidyText)
)
summary(parl_corpus)

parl_toks <- tokens(parl_corpus, remove_number=T,remove_punct=T)
length(unique(parl_toks))
# Corpus consists of 1546 documents (Wortmeldungen pro Person)

parl_corpus_final <- parl_toks %>%
  tokens_remove(stopwords('de')) %>%
  tokens_remove(stopwords('fr')) %>%
  tokens_remove(stopwords('it')) %>%
  tokens_remove(mystopwords)

# Create document feature matrix parl_dfm
parl_dfm <- dfm(parl_corpus_final)
head(parl_dfm)

parl_dfm <- dfm_wordstem(parl_dfm, language = "de")
parl_dfm <- dfm_wordstem(parl_dfm, language = "fr")
parl_dfm <- dfm_wordstem(parl_dfm, language = "it")

## Look at words in their context
kwic(parl_corpus_final, phrase("santé")) %>% head()
kwic(parl_corpus_final, phrase("Gesundheit")) %>% head()
kwic(parl_corpus_final, phrase("Kurzarbeit")) %>% head()


### Create German Corpus ###

text_covid_d <- text_covid %>% 
  filter(LanguageOfText == "DE")

parl_corpus_d <- corpus(
  text_covid_d$tidyText,
  docnames = text_covid_d$ID,
  docvars = text_covid_d %>% 
    select(-tidyText)
)
summary(parl_corpus_d)

parl_toks_d <- tokens(parl_corpus_d, remove_number=T,remove_punct=T)
length(unique(parl_toks_d))
# Corpus consists of 1108 documents (Wortmeldungen pro Person)

parl_corpus_d_final <- parl_toks_d %>%
  tokens_remove(stopwords('de')) %>%
  tokens_remove(mystopwords)

# Create document feature matrix parl_dfm
parl_dfm_d <- dfm(parl_corpus_d_final)
parl_dfm_d <- dfm_wordstem(parl_dfm_d, language = "de")

# What did they talk about? Get absolute frequency of all words (stemmed)
parl_freq_d <- textstat_frequency(parl_dfm_d, n=500)
parl_freq50d <- textstat_frequency(parl_dfm_d, n=50)


### Create French Corpus ###

text_covid_f <- text_covid %>% 
  filter(LanguageOfText == "FR")
length(text_covid_f$tidyText)

parl_corpus_f <- corpus(
  text_covid_f$tidyText,
  docnames = text_covid_f$ID,
  docvars = text_covid_f %>% 
    select(-tidyText)
)
summary(parl_corpus_f)

parl_toks_f <- tokens(parl_corpus_f, remove_number=T,remove_punct=T)
length(unique(parl_toks_f))
# Corpus consists of 408 documents (Wortmeldungen pro Person)

parl_corpus_f_final <- parl_toks_f %>%
  tokens_remove(stopwords('fr')) %>%
  tokens_remove(mystopwords)

# Create document feature matrix parl_dfm
parl_dfm_f <- dfm(parl_corpus_f_final)
parl_dfm_f <- dfm_wordstem(parl_dfm_f, language = "fr")
#view(parl_dfm_f)

# What did they talk about? Get absolute frequency of all words
parl_freq_f <- textstat_frequency(parl_dfm_f, n=500)
parl_freq50f <- textstat_frequency(parl_dfm_f, n=50)


### Count specific words like "Wirtschaft" over time
### Select only columns date and text 

text_covid_short <- text_covid %>% 
  select(MeetingDate, tidyText)
head(text_covid_short)

# Count "coronavirus, corona, covid, sars"
text_covid_short$count_coronavirus <- str_count(text_covid_short$tidyText, "coronavirus")
text_covid_short$count_corona <- str_count(text_covid_short$tidyText, "corona")
text_covid_short$count_covid <- str_count(text_covid_short$tidyText, "covid")
text_covid_short$count_sars <- str_count(text_covid_short$tidyText, "sars")
# Count "Wirtschaft"
text_covid_short$count_wirtschaft <- str_count(text_covid_short$tidyText, "wirtschaft")
text_covid_short$count_eco <- str_count(text_covid_short$tidyText, "économie")
# Count "Franken"
text_covid_short$count_franken <- str_count(text_covid_short$tidyText, "franken")
text_covid_short$count_francs <- str_count(text_covid_short$tidyText, "francs")
# Count "Millionen u. Milliarden"
text_covid_short$count_millionen <- str_count(text_covid_short$tidyText, "millionen")
text_covid_short$count_milliarden <- str_count(text_covid_short$tidyText, "milliarden")
text_covid_short$count_millions <- str_count(text_covid_short$tidyText, "millionen")
text_covid_short$count_milliards <- str_count(text_covid_short$tidyText, "milliards")
# Count "Gesundheit"
text_covid_short$count_gesundheit <- str_count(text_covid_short$tidyText, "gesundheit")
text_covid_short$count_sante <- str_count(text_covid_short$tidyText, "santé")
# Count "Massnahmen"
text_covid_short$count_massnahmen <- str_count(text_covid_short$tidyText, "Massnahmen")
text_covid_short$count_mesures <- str_count(text_covid_short$tidyText, "mesures")
head(text_covid_short)
# sum up
text_covid_short %<>%
  rowwise() %>%
  mutate(corona = sum(c(count_coronavirus, count_corona, count_covid, count_sars))) %>%
  mutate(millionen = sum(c(count_millionen, count_milliarden, count_millions, count_milliards))) %>%
  mutate(gesundheit = sum(c(count_gesundheit, count_sante))) %>%
  mutate(wirtschaft = sum(c(count_wirtschaft, count_eco))) %>%
  mutate(franken = sum(c(count_franken, count_francs))) %>%
  mutate(massnahmen = sum(c(count_massnahmen, count_mesures))) %>%
  select(MeetingDate, tidyText, corona, millionen, franken, wirtschaft, gesundheit, massnahmen)

# Economy, complete missing dates
by_date_wirtschaft <- text_covid_short %>%
  group_by(MeetingDate) %>%
  summarise(economy = sum(wirtschaft)) %>%
  complete(MeetingDate = seq.Date(min(MeetingDate), max(MeetingDate), by="day"))
head(by_date_wirtschaft)

# Franken, complete missing dates
by_date_franken <- text_covid_short %>%
  group_by(MeetingDate) %>%
  summarise(franken = sum(franken)) %>%
  complete(MeetingDate = seq.Date(min(MeetingDate), max(MeetingDate), by="day"))
head(by_date_franken)

# Millionen, complete missing dates
by_date_mio <- text_covid_short %>%
  group_by(MeetingDate) %>%
  summarise(mio = sum(millionen)) %>%
  complete(MeetingDate = seq.Date(min(MeetingDate), max(MeetingDate), by="day"))
head(by_date_franken)

# Gesundheit, complete missing dates
by_date_sante <- text_covid_short %>%
  group_by(MeetingDate) %>%
  summarise(sante = sum(gesundheit)) %>%
  complete(MeetingDate = seq.Date(min(MeetingDate), max(MeetingDate), by="day"))
head(by_date_sante)

# Massnahmen, complete missing dates
by_date_mesures <- text_covid_short %>%
  group_by(MeetingDate) %>%
  summarise(mesures = sum(massnahmen)) %>%
  complete(MeetingDate = seq.Date(min(MeetingDate), max(MeetingDate), by="day"))
head(by_date_sante)


########################
### Textstat Keyness ###
########################

# Will show us, which words are relatively found more often in text compared to text of reference

# German, make Corpus and remove stopwords
dfm_all_d <- corpus(
  text_all$tidyText,
  docnames = text_all$ID,
  docvars = text_all
) %>%
  corpus_subset(docvars(.)[["LanguageOfText"]] == "DE") %>%
  dfm(
    tolower = F,
    remove = c(stopwords('de'), mystopwords)
  )

corona_nouns_d <- textstat_keyness(
  dfm_all_d,
  target = str_detect(tolower(docvars(dfm_all_d)[["tidyText"]]), "corona|covid|sars|coronavirus")
) %>%
  filter(!tolower(feature) == feature)

# Nouns that occurred relatively more often than in the total text (excluding words such as coronavirus)
corona_nouns_d <- corona_nouns_d %<>%
  filter(!str_detect(tolower(feature), "corona|covid|sars|coronavirus"))
corona_nouns_d
# write.csv(corona_nouns_d, ""), save, if needed
# Krise, Franken, Milliarden, Millionen, Pandemie, Bewältigung, Massnahmen, Wirtschaft, Kurzarbeit, Voranschlag etc.


# French
dfm_alle_f <- corpus(
  text_all$tidyText,
  docnames = text_all$ID,
  docvars = text_all
) %>%
  corpus_subset(docvars(.)[["LanguageOfText"]] == "FR") %>%
  dfm(
    tolower = F,
    remove = c(stopwords('fr'), mystopwords)
  )

corona_nouns_f <- textstat_keyness(
  dfm_alle_f,
  target = str_detect(tolower(docvars(dfm_alle_f)[["tidyText"]]), "corona|covid|sars|coronavirus")
)

# Ohne Wörter mit Corona etc. direkt drin
corona_nouns_f %<>%
  filter(!str_detect(tolower(feature), "corona|covid|covid-19|sars|coronavirus"))
corona_nouns_f
# write.csv(corona_nouns_f, "") save, if needed
# crise, francs, pandémie, millions, crédits, budget, locataires

# Italian
dfm_alle_i <- corpus(
  text_all$tidyText,
  docnames = text_all$ID,
  docvars = text_all
) %>%
  corpus_subset(docvars(.)[["LanguageOfText"]] == "IT") %>%
  dfm(
    tolower = F,
    remove = c(stopwords('it'), mystopwords)
  )

corona_nouns_i <- textstat_keyness(
  dfm_alle_i,
  target = str_detect(tolower(docvars(dfm_alle_i)[["tidyText"]]), "corona|covid|sars|coronaviruss")
)

corona_nouns_i %<>%
  filter(!str_detect(tolower(feature), "corona|covid|sars|coronavirus"))
# crisi, crise, gestion, mesures, medici

##########################################
#### Get relative frequencies of people ##
########################################## 

# Who speaks the most? 
length(text_all$tidyText)
most_speeches_speaker <- text_all %>%
  group_by(SpeakerFullName) %>%
  count() %>%
  arrange(desc(n))   %>%
  rename(speeches = n)
most_speeches_speaker
# most speeches overall Beat Rieder, Christian Levrat, Hannes Germann

# Who absolutely speaks about covid the most? 
colnames(text_covid)
most_speeches_corona_speaker <- text_covid %>%
  group_by(SpeakerFullName) %>%
  count() %>% 
  arrange(desc(n)) %>%
  rename(speech_corona = n)
head(most_speeches_corona_speaker)
# most speeches Corona Hegglin Peter, Christian Levrat, Paul Rechsteiner

# Who relatively speaks about covid the most?
most_speeches_corona_speaker <- left_join(most_speeches_speaker, most_speeches_corona_speaker) 

most_speeches_corona_rel <- most_speeches_corona_speaker %>%
  mutate(percent = (speech_corona/speeches)*100) 

most_speeches_corona_rel %<>%
  arrange(desc(percent))
most_speeches_corona_rel
write.csv(most_speeches_corona_rel, "outcomes_Analysis/most_speeches_corona_speaker.csv")

# What party speaks about covid the most? 
most_speeches_party <- text_all %>%
  group_by(ParlGroupName) %>%
  count() %>% arrange(desc(n))  %>%
  rename(speeches = n)
# most speeches overall: SVP, CVP

most_speeches_corona_party <- text_covid %>%
  group_by(ParlGroupName) %>%
  count() %>% arrange(desc(n))%>%
  rename(speech_corona = n)
most_speeches_corona_party
# most speeches Corona: Grüne, Mitte, SVP 

most_speeches_corona_party <- left_join(most_speeches_party, most_speeches_corona_party) 

most_speeches_corona_party %<>%
  mutate(percent = (speech_corona/speeches)*100) %>%
  arrange(desc(percent))
most_speeches_corona_party
# relatively most speeches SVP, CVP, SP
# write.csv(most_speeches_corona_party, "") save, if needed

# fin
